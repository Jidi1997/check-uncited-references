#!/usr/bin/env python3
"""
Check Uncited References (CURE)
------------------------------
A lightweight CLI tool to detect bibliography entries that are listed in the
reference section but not cited within the body of a Markdown document.
"""

import re
import argparse
import datetime
import os
import sys

def parse_reference(ref_text):
    """
    Parses a bibliography entry to extract its ID, publication year, and author names.
    Handles multiline content where periods may follow names or initials.
    """
    match = re.match(r'^(?:\[?(\d+)\]?\.?\s+)?(?!年)(.*)', ref_text.strip(), flags=re.DOTALL)
    if not match:
        return None
        
    ref_id = match.group(1) if match.group(1) else "N/A"
    if ref_id != "N/A" and int(ref_id) > 2000:
        return None
        
    content = match.group(2)
    
    # 1. Extract publication year.
    # We look for all years, but we exclude those that appear to be part of a page range like 1985-2021.
    # A year is usually (2024), 2024. or 2024,
    raw_years = re.findall(r'\b(19\d\d|20\d\d)\b', content)
    valid_years = []
    for y in raw_years:
        # Check if it's likely a page number (e.g., in a range 2000-2010)
        # Avoid years that have a hyphen immediately before or after 
        if re.search(f'\\d-{y}|{y}-\\d', content):
            continue
        valid_years.append(y)
        
    if not valid_years:
        # Fallback to last year if no 'valid' ones found (legacy)
        valid_years = raw_years if raw_years else []
        
    if not valid_years: return None

    # Heuristic: Favor year in parentheses first (Chinese style: (2020)).
    parenthesized_year = re.search(r'\((19\d\d|20\d\d)\)', content)
    if parenthesized_year:
        year = parenthesized_year.group(1)
    else:
        # For Western-style refs (Journal, Year, Vol: Page), the pub year follows
        # a comma or period+space AFTER a [J]/[M]/[R] marker or after a journal name.
        # Strategy: prefer the first year that appears after '[J]', '[M]', '[R]', or ', '
        # rather than just taking the last year (which could belong to the previous merged entry).
        post_marker_year = re.search(r'(?:\[[JMRjmr]\]|,|;)\s*(19\d\d|20\d\d)', content)
        year = post_marker_year.group(1) if post_marker_year else valid_years[0]
    
    # 2. Extract authors.
    year_match = re.search(re.escape(year), content)
    year_pos = year_match.start() if year_match else len(content)
    pre_year_content = content[:year_pos].strip(' .,([])')
    
    # Look for the title separator. 
    # Usually Author. Title or Author(Year)Title.
    # If no period-space, then everything before the year is authors.
    author_title_sep = re.search(r'(?<!\b[A-Z])\.\s+(?![a-z])', pre_year_content)
    if author_title_sep:
        authors_string = pre_year_content[:author_title_sep.start()].strip()
    else:
        # Fallback: if there's a [J], [M], [R] marker, the text before it is likely Author + Title.
        # We need to find the split between Authors and Title. 
        # Typically the authorship list ends with a period.
        bracket_marker = re.search(r'\[[JMR]\]', pre_year_content)
        if bracket_marker:
            pre_marker = pre_year_content[:bracket_marker.start()].strip()
            # Find the last period in pre_marker that isn't an initial.
            split_match = list(re.finditer(r'(?<!\b[A-Z])\.', pre_marker))
            if split_match:
                authors_string = pre_marker[:split_match[-1].start()].strip()
            else:
                authors_string = pre_marker
        else:
            authors_string = pre_year_content
        
    # Split by standard delimiters: comma, ampersand, 'and', or Chinese enumeration mark
    parts = re.split(r'[,，&]| and |\u3001', authors_string)
    authors = []
    for p in parts:
        p = p.strip()
        if not p or len(p) < 2: continue
        # Strip common initialisms (e.g., 'A.' or 'B' or 'D-G').
        clean_p = re.sub(r'\b[A-Z](?:-[A-Z])?\b\.?', '', p).strip()
        # Primary name extraction (usually the surname or full Chinese name).
        name_parts = re.split(r'[\s(]', clean_p)
        if name_parts:
            # Handle hyphenated surnames like 'Eduardo D-G' or 'Aragòn-Correa'
            first_word = re.sub(r'[^\w\u00C0-\u017F\u4e00-\u9fa5\-]', '', name_parts[0])
            if first_word: authors.append(first_word)
            
    return {
        'id': str(ref_id).strip(),
        'year': str(year).strip(),
        'authors': [a.strip() for a in authors[:10] if a.strip()], # Cap to avoid title leak
        'original': ref_text.strip()
    }

def is_line_reference_like(line):
    """
    Heuristically determines if a line appears to be the start of a bibliography entry.
    Used to validate candidate split points between body text and the reference list.
    """
    line = line.strip()
    if not line: return False
    
    # Pattern 1: Leading numeric ID (e.g., [1] or 1.)
    num_match = re.match(r'^\[?(\d+)\]?\.?\s+(?!年)', line)
    if num_match:
        if int(num_match.group(1)) < 2000:
            return True
    
    # Pattern 2: Surname-first signature (e.g., Surname, I. or Surname, Name)
    # Checks for: First word capitalized + comma + space + Second word capitalized at START of line.
    if re.match(r'^[A-Z\u4e00-\u9fa5][a-zA-Z\s\-\u4e00-\u9fa5]{1,25},\s+[A-Z\u4e00-\u9fa5]', line):
        # Validation: Verify if a year exists within or in parentheses.
        if re.search(r'\b(19\d\d|20\d\d)\b', line) or re.search(r'\((19\d\d|20\d\d)\)', line):
            return True
            
    return False

def extract_references_from_block(text_block):
    """
    Extracts individual bibliography entries from a dense/packed continuous text block.
    """
    # Pre-clean isolated artifacts
    text_block = re.sub(r'\s+\d+\.\s+\n', '\n', text_block)
    
    # Refined Split Logic:
    # Refined Split Logic:
    # Aggressively split at period terminals (e.g., page 821.) followed by an Author Start.
    # We include hyphenated names (e.g., El-Khatib) and accented characters.
    # A name start usually has a second component (initial or word) or a comma nearby.
    word = r'[A-Z\u00C0-\u017F\u4e00-\u9fa5][a-z\u00C0-\u017F\u4e00-\u9fa5\-]*'
    author_header = f'{word}\\s*(?:[A-Z\u00C0-\u017F\u4e00-\u9fa5][\\w\\-]*|[,，、\\.])'
    
    # Using finditer to manually split on zero-width boundaries if needed
    splits = [0]
    for m in re.finditer(fr'(?<=\d\.)\s*(?={author_header})', text_block):
        splits.append(m.start())
    splits.append(len(text_block))
    
    segments = []
    for i in range(len(splits)-1):
        seg = text_block[splits[i]:splits[i+1]].strip()
        if len(seg) > 10: segments.append(seg)
    
    if len(segments) <= 1:
        # Fallback to broader split if first one fails
        segments = re.split(r'(?<=\d\.|\]\.)\s*(?=[A-Z\u00C0-\u017F\u4e00-\u9fa5]{1,20}(?:[\s\w]*?){0,5}[,，、])', text_block)
        
    return [s.strip() for s in segments if len(s.strip()) > 10]

def find_bibliography_split(doc_text):
    """
    Finds the optimal split point between the document body and the bibliography section.
    Uses a scoring algorithm based on keyword location and subsequent line structure density.
    """
    # Regex to capture standard academic headers (supports English and Chinese).
    keywords_pattern = re.compile(r'(?:\n|^)(#+\s*)?(References?|Bibliography|参考文献)(?:[^\n]*)\n', re.IGNORECASE)
    candidates = list(re.finditer(keywords_pattern, doc_text))
    
    best_index = -1
    max_score = -1
    doc_length = len(doc_text)
    
    for match in candidates:
        start_pos = match.end()
        # Heuristic: Bibliography is highly likely to be in the final chapters.
        position_score = (start_pos / doc_length) * 10
        
        # Format weight: Markdown headers are high-confidence indicators.
        header_bonus = 20 if match.group(1) else 0
        
        # Density Verification: Analyze the next 20 lines for bibliography patterns.
        sample_text = doc_text[start_pos:start_pos + 1200]
        sample_lines = sample_text.split('\n')[:20]
        
        ref_line_count = sum(1 for line in sample_lines if is_line_reference_like(line))
        
        # Density score (5 points per reference-like line detected).
        density_score = ref_line_count * 5
        total_score = position_score + header_bonus + density_score
        
        # Reject candidates with near-zero density unless score is high.
        if ref_line_count < 2 and total_score < 15:
            continue
            
        if total_score > max_score:
            max_score = total_score
            best_index = match.start()
            
    return best_index

def main():
    parser = argparse.ArgumentParser(description="Check for uncited references in a Markdown document.")
    parser.add_argument("-i", "--input", help="The source markdown file path.", required=True)
    parser.add_argument("-o", "--output", help="Path to save the result report.", default="uncited_report.md")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    doc_file = args.input
    output_report_file = args.output
    
    if not os.path.exists(doc_file):
        print(f"Error: File '{doc_file}' was not found.")
        sys.exit(1)

    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_text = f.read()
    except Exception as e:
        print(f"Error reading source file: {e}")
        sys.exit(1)

    # Perform intelligent section splitting
    # Robustly split body from references using a regex for the header (avoiding TOC links).
    # Looks for a line starting with one or more '#' followed by whitespace and '参考文献'.
    bib_header_pattern = re.compile(r'^\s*#{1,6}\s*参考文献', re.MULTILINE)
    bib_match = bib_header_pattern.search(doc_text)
    
    if bib_match:
        split_index = bib_match.start()
        searchable_text = doc_text[:split_index]
        raw_bib_block = doc_text[split_index:]
    else:
        # Fallback to plain text search if no markdown header is found
        split_index = doc_text.find("参考文献")
        if split_index != -1:
            searchable_text = doc_text[:split_index]
            raw_bib_block = doc_text[split_index:]
        else:
            searchable_text = doc_text
            raw_bib_block = ""

    # Truncate the bibliography block at the next top-level heading that follows it
    # (e.g., '# 作者在读期间科研成果简介'). These appendix sections must not be parsed
    # as references, otherwise their publication-like lines cause false ghost detections.
    next_heading_match = re.search(r'\n\s*#{1,6}\s+\S', raw_bib_block[1:])  # skip the bib header itself
    if next_heading_match:
        ref_text_block = raw_bib_block[:next_heading_match.start() + 1]
    else:
        ref_text_block = raw_bib_block

    parsed_refs = []
    # Try block extraction first for dense formats
    raw_entries = extract_references_from_block(ref_text_block)
    
    if len(raw_entries) > 1:
        for entry in raw_entries:
            data = parse_reference(entry)
            if data and data['authors'] and data['year']:
                parsed_refs.append(data)
    
    # Combined with line-based scanning to catch single entries per line correctly
    ref_lines = ref_text_block.split('\n')
    for line in ref_lines:
        line = line.strip()
        if is_line_reference_like(line):
            data = parse_reference(line)
            if data and data['authors'] and data['year']:
                # Deduplicate based on author+year signature
                sig = f"{data['authors'][0]}{data['year']}"
                if not any(f"{p['authors'][0]}{p['year']}" == sig for p in parsed_refs):
                    parsed_refs.append(data)
                
    # Final Clean Search logic
    clean_body = re.sub(r'[^\w\-\u00C0-\u017F\u4e00-\u9fa5]', ' ', searchable_text)
    clean_body = re.sub(r'\s+', ' ', clean_body)
    
    # Also prepare a full document version just in case splitting was imperfect
    full_clean_doc = re.sub(r'[^\w\-\u00C0-\u017F\u4e00-\u9fa5]', ' ', doc_text)
    full_clean_doc = re.sub(r'\s+', ' ', full_clean_doc)
    
    uncited_entries = []
    for ref in parsed_refs:
        clean_name = re.sub(r'[^\w\-\u00C0-\u017F\u4e00-\u9fa5]', '', ref['authors'][0])
        year_val = ref['year']
        
        if not clean_name or not year_val: continue
        
        # Simple co-occurrence in 200 chars. No strict boundaries.
        pattern = f"{clean_name}.{{0,200}}{year_val}"
        regex = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        
        # Check searchable section first
        if regex.search(clean_body):
            continue
            
        # Fallback: check whole doc (excluding the exact original citation metadata to avoid self-match)
        # We replace the original metadata in the doc with spaces for this check.
        orig_clean = re.sub(r'[^\w\-\u00C0-\u017F\u4e00-\u9fa5]', ' ', ref['original'])
        doc_without_ref = full_clean_doc.replace(orig_clean, " " * len(orig_clean))
        
        if not regex.search(doc_without_ref):
            uncited_entries.append(ref)
            
    # Output terminal results
    print(f"\n" + "="*45)
    print(f"★ Input File: {doc_file}")
    print(f"★ Detection Mode: {'Intelligent Splitting' if split_index != -1 else 'Full-Text Scan'}")
    print(f"★ Bibliography Size: {len(parsed_refs)} entries")
    
    try:
        with open(output_report_file, 'w', encoding='utf-8') as report:
            report.write(f"# Uncited References Report\n\n")
            report.write(f"- **Summary**: Found entries in the bibliography with no citation in the body text.\n")
            report.write(f"- **Scan Time**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            report.write(f"- **Target File**: `{doc_file}`\n")
            report.write(f"- **Reference Count**: {len(parsed_refs)}\n")
            report.write(f"- **Ghost Count (Uncited)**: {len(uncited_entries)}\n\n")
            
            if not uncited_entries:
                print(f"★ Result: All {len(parsed_refs)} references are successfully cited.")
                report.write("### ✅ Verification Successful: All entries are cited.\n")
            else:
                print(f"★ Action Required: {len(uncited_entries)} ghost references detected.")
                print(f"★ Detail report generated: {output_report_file}")
                report.write("### ⚠️ Detected Uncited Entries:\n\n")
                report.write("| ID | Fingerprint (Key Info) | Original Metadata |\n")
                report.write("| :--- | :--- | :--- |\n")
                
                for u in uncited_entries:
                    key_info = f"{u['authors'][0]}, {u['year']}" if u['authors'] else "Unknown"
                    report.write(f"| {u['id']} | {key_info} | {u['original']} |\n")
    except IOError as e:
        print(f"Error persisting report: {e}")

    print("="*45 + "\n")

if __name__ == '__main__':
    main()

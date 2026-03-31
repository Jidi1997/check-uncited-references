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
    Parses a bibliography entry line to extract its ID, publication year, and author names.
    
    Supports:
    - Numbered formats: [1] Author, 2020... or 1. Author, 2020...
    - Unnumbered formats: Author, A. (2020)... or Author, 2020...
    
    Args:
        ref_text (str): The raw text line representing a bibliography entry.
        
    Returns:
        dict: Containing 'id', 'year', 'authors', and 'original' text.
    """
    # Regex logic: Optional numeric ID [1] or 1. + space. 
    # Uses negative lookahead (?!年) to avoid misidentifying sign-off dates as IDs.
    match = re.match(r'^(?:\[?(\d+)\]?\.?\s+)?(?!年)(.*)', ref_text.strip())
    if not match:
        return None
        
    ref_id = match.group(1) if match.group(1) else "N/A"
    
    # Heuristic filter: Bibliography indices rarely exceed 2000.
    if ref_id != "N/A" and int(ref_id) > 2000:
        return None
        
    content = match.group(2)
    
    # Extract year (supported range 19xx-20xx).
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', content)
    year = year_match.group(1) if year_match else ""
    
    # Isolate the author prefix (text preceding the year identifier).
    authors_string = content
    if year_match:
        idx = year_match.start()
        if idx > 5: 
            authors_string = content[:idx].strip('.,( ]')
    
    # Split by standard delimiters: comma, ampersand, 'and', or Chinese enumeration mark (、)
    parts = re.split(r'[,，&]| and |\u3001', authors_string)
    authors = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Strip common initialisms (e.g., 'A.' or 'B').
        clean_p = re.sub(r'\b[A-Z]\b\.?', '', p).strip()
        
        # Primary name extraction (usually the surname).
        name_parts = re.split(r'[\s(]', clean_p)
        if name_parts:
            first_word = name_parts[0]
            # Normalize: Keep alphanumeric, Chinese residues, and hyphens.
            first_word = re.sub(r'[^\w\u4e00-\u9fa5\-]', '', first_word)
            if first_word:
                authors.append(first_word)
            
    authors = [a for a in authors if a]
    
    return {
        'id': ref_id,
        'year': year,
        'authors': authors,
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
    # Checks for: First word capitalized + comma + space + Second word capitalized.
    if re.match(r'^[A-Z\u4e00-\u9fa5][a-zA-Z\s\-\u4e00-\u9fa5]{1,25},\s+[A-Z\u4e00-\u9fa5]', line):
        # Validation: Verify if a year exists within or in parentheses.
        if re.search(r'\b(19\d\d|20\d\d)\b', line) or re.search(r'\((19\d\d|20\d\d)\)', line):
            return True
            
    return False

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
    split_index = find_bibliography_split(doc_text)
    
    if split_index != -1:
        searchable_text = doc_text[:split_index]
        ref_text_block = doc_text[split_index:]
    else:
        # Fallback to scanning the whole document if no clear split is found.
        searchable_text = doc_text
        ref_text_block = ""

    parsed_refs = []
    ref_lines = ref_text_block.split('\n')
    for line in ref_lines:
        line = line.strip()
        if is_line_reference_like(line):
            data = parse_reference(line)
            if data:
                parsed_refs.append(data)
                
    uncited_entries = []
    for ref in parsed_refs:
        year = ref['year']
        if not ref['authors']:
            continue
        
        def get_author_pattern(author_name):
            esc = re.escape(author_name)
            # Use lookbehind/lookahead for alphabet rather than \b to allow adjacent Chinese characters (which Unicode considers \w)
            if re.match(r'^[A-Za-z\u00C0-\u017F]+$', author_name):
                return r'(?<![A-Za-z\u00C0-\u017F])' + esc + r'(?![A-Za-z\u00C0-\u017F])'
            return esc

        auth1_pattern = get_author_pattern(ref['authors'][0])
        # Same logic for year to prevent \b acting up if '年' is attached
        year_pattern = r'(?<![0-9])' + re.escape(year) + r'(?![0-9])'
        
        # Match pattern supports variations (e.g. Author et al, 2020 or Author & Author 2020).
        if len(ref['authors']) >= 2:
            auth2_pattern = get_author_pattern(ref['authors'][1])
            pattern_str = f"{auth1_pattern}.{{0,50}}{auth2_pattern}.{{0,50}}{year_pattern}"
            pattern_alt = f"{auth1_pattern}.{{0,50}}{year_pattern}"
            regex = re.compile(f"({pattern_str})|({pattern_alt})", re.IGNORECASE | re.DOTALL)
        else:
            pattern_str = f"{auth1_pattern}.{{0,50}}{year_pattern}"
            regex = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)
            
        if not regex.search(searchable_text):
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

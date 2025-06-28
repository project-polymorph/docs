import re
import sys
import os
from pathlib import Path

def process_citations(text):
    # Dictionary to store citation text and their assigned numbers
    citations = {}
    current_number = 1
    
    # Function to get citation number or assign new one
    def get_citation_number(citation_text):
        nonlocal current_number
        if citation_text not in citations:
            citations[citation_text] = current_number
            current_number += 1
        return citations[citation_text]

    # Pattern to match citations
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    
    # First pass: collect all citations 
    all_citations = []
    last_positions = {}
    
    # Process the text paragraph by paragraph to maintain paragraph structure
    paragraphs = text.split('\n\n')
    current_pos = 0
    
    for paragraph in paragraphs:
        # Find all citations in this paragraph
        for match in re.finditer(pattern, paragraph):
            citation_text = match.group(1)
            url = match.group(2)
            number = get_citation_number(citation_text)
            absolute_pos = current_pos + match.start()
            all_citations.append((absolute_pos, citation_text, url, number))
            # Only update last_positions if this position is greater than any previously seen
            if number not in last_positions or absolute_pos > last_positions[number]:
                last_positions[number] = absolute_pos
        current_pos += len(paragraph) + 2  # +2 for the paragraph separator

    # Count total occurrences of each citation number
    citation_counts = {}
    for _, _, _, number in all_citations:
        citation_counts[number] = citation_counts.get(number, 0) + 1
    
    # Track how many times we've seen each citation during processing
    seen_citations = {}
    
    # Process each paragraph
    processed_paragraphs = []
    current_pos = 0
    
    for paragraph in paragraphs:
        # Get citations just in this paragraph
        citations_in_para = []
        for match in re.finditer(pattern, paragraph):
            citation_text = match.group(1)
            url = match.group(2)
            number = get_citation_number(citation_text)
            absolute_pos = current_pos + match.start()
            citations_in_para.append((match.start(), citation_text, url, number, absolute_pos))
        
        # Process citations in order of appearance
        offset = 0
        for pos, citation_text, url, number, absolute_pos in sorted(citations_in_para):
            # Count this occurrence
            seen_citations[number] = seen_citations.get(number, 0) + 1
            
            # Check if this is the last occurrence globally
            is_last = (seen_citations[number] == citation_counts[number])
            
            # Add debug print
            print(f"Citation {number}: '{citation_text}', is_last={is_last}, pos={absolute_pos}, last_pos={last_positions.get(number)}")
            
            # Determine replacement text
            if is_last:
                replacement = f'[{number}: {citation_text}]({url})'
                print(f"LAST occurrence replacement: {replacement}")
            else:
                replacement = f'[{number}]({url})'
            
            # Calculate match length and replace
            original_length = len(f'[{citation_text}]({url})')
            start_pos = pos + offset
            end_pos = start_pos + original_length
            paragraph = paragraph[:start_pos] + replacement + paragraph[end_pos:]
            
            # Update offset
            offset += len(replacement) - original_length
        
        processed_paragraphs.append(paragraph)
        current_pos += len(paragraph) + 2  # +2 for the paragraph separator
    
    return '\n\n'.join(processed_paragraphs)

def main():
    # Check if filename is provided
    if len(sys.argv) != 2:
        print("Usage: python process_citations.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    # Create output filename
    input_path = Path(input_file)
    output_file = input_path

    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process content
        processed_content = process_citations(content)

        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        print(f"Processing complete! Output saved to: {output_file}")

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
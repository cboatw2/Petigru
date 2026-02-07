#!/usr/bin/env python3
"""
Extract letters from the book "Life, Letters, and Speeches of James Louis Petigru"
"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Letter:
    """Represents an extracted letter"""
    id: int
    recipient: Optional[str]
    location: Optional[str]
    date: Optional[str]
    salutation: Optional[str]
    body: str
    closing: Optional[str]
    start_line: int
    end_line: int
    
    def to_dict(self):
        return asdict(self)


def extract_letters(filename: str) -> List[Letter]:
    """
    Extract letters from the text file.
    
    Letters typically follow this pattern:
    1. TO [RECIPIENT NAME] (all caps)
    2. Location, Date
    3. Salutation (Dear X:, My Dear X:, etc.)
    4. Body text
    5. Closing (Yours truly, etc.)
    """
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    letters = []
    letter_id = 0
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for letter header pattern: "TO [NAME]" at the start of a line
        # Must be in all caps and start with "TO"
        to_pattern = r'^TO\s+([A-Z][A-Z\s\.\,\-]+)$'
        match = re.match(to_pattern, line)
        
        if match and len(line) > 5:  # Ensure it's a substantial match
            # Found a potential letter start
            recipient = match.group(1).strip()
            start_line = i + 1  # 1-indexed
            
            # Skip to next non-empty line for location/date
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i >= len(lines):
                break
                
            # Try to extract location and date
            location_date_line = lines[i].strip()
            location = None
            date = None
            
            # Pattern: "City, Date" or "City, State, Date"
            loc_date_pattern = r'^([A-Za-z\s\.]+),\s+(.+)$'
            loc_match = re.match(loc_date_pattern, location_date_line)
            if loc_match:
                location = loc_match.group(1).strip()
                date = loc_match.group(2).strip()
            
            # Move to next non-empty line for salutation
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i >= len(lines):
                break
            
            # Try to extract salutation
            salutation_line = lines[i].strip()
            salutation = None
            if re.match(r'^(Dear|My [Dd]ear)\s+.+:$', salutation_line):
                salutation = salutation_line
                i += 1
            
            # Extract body until we hit the next letter marker or end
            body_lines = []
            while i < len(lines):
                current_line = lines[i].strip()
                
                # Check if we've hit the next letter
                if re.match(r'^TO\s+[A-Z][A-Z\s\.\,\-]+$', current_line) and len(current_line) > 5:
                    break
                
                # Check if we've hit a chapter marker or page number
                if re.match(r'^(CHAPTER|Page|\d+\s+Life)', current_line):
                    break
                
                body_lines.append(lines[i].rstrip())
                i += 1
            
            # Join body and look for closing
            body_text = '\n'.join(body_lines)
            closing = None
            
            # Try to extract closing from the end of the body
            closing_patterns = [
                r'(Yours\s+[a-z]+[,]?\s*)$',
                r'(Your\s+obedient\s+servant[,]?\s*)$',
                r'(Affectionately[,]?\s*)$',
                r'(Respectfully[,]?\s*)$',
            ]
            
            for pattern in closing_patterns:
                closing_match = re.search(pattern, body_text, re.IGNORECASE | re.MULTILINE)
                if closing_match:
                    closing = closing_match.group(1).strip()
                    break
            
            end_line = i
            
            # Only save if we have substantial content
            if len(body_text.strip()) > 50:
                letter_id += 1
                letters.append(Letter(
                    id=letter_id,
                    recipient=recipient,
                    location=location,
                    date=date,
                    salutation=salutation,
                    body=body_text.strip(),
                    closing=closing,
                    start_line=start_line,
                    end_line=end_line
                ))
        else:
            i += 1
    
    return letters


def save_letters(letters: List[Letter], output_file: str):
    """Save extracted letters to a JSON file"""
    letters_data = [letter.to_dict() for letter in letters]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(letters_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(letters)} letters to {output_file}")


def save_letters_text(letters: List[Letter], output_file: str):
    """Save extracted letters to a text file for easier reading"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for letter in letters:
            f.write("=" * 80 + "\n")
            f.write(f"LETTER #{letter.id}\n")
            f.write("=" * 80 + "\n")
            if letter.recipient:
                f.write(f"TO: {letter.recipient}\n")
            if letter.location:
                f.write(f"LOCATION: {letter.location}\n")
            if letter.date:
                f.write(f"DATE: {letter.date}\n")
            f.write(f"SOURCE: Lines {letter.start_line}-{letter.end_line}\n")
            f.write("-" * 80 + "\n")
            if letter.salutation:
                f.write(f"{letter.salutation}\n\n")
            f.write(f"{letter.body}\n")
            if letter.closing:
                f.write(f"\n{letter.closing}\n")
            f.write("\n\n")
    
    print(f"Saved {len(letters)} letters in text format to {output_file}")


def print_summary(letters: List[Letter]):
    """Print a summary of extracted letters"""
    print(f"\nTotal letters extracted: {len(letters)}")
    print("\nFirst 10 letters:")
    for i, letter in enumerate(letters[:10], 1):
        print(f"\n{i}. TO: {letter.recipient}")
        print(f"   Date: {letter.date}")
        print(f"   Location: {letter.location}")
        print(f"   Lines: {letter.start_line}-{letter.end_line}")
        print(f"   Body length: {len(letter.body)} chars")


def main():
    input_file = "LifeLettersAndSpeeches.txt"
    output_json = "extracted_letters.json"
    output_text = "extracted_letters.txt"
    
    print(f"Extracting letters from {input_file}...")
    letters = extract_letters(input_file)
    
    print_summary(letters)
    
    save_letters(letters, output_json)
    save_letters_text(letters, output_text)
    
    print("\nExtraction complete!")
    print(f"- JSON output: {output_json}")
    print(f"- Text output: {output_text}")


if __name__ == "__main__":
    main()

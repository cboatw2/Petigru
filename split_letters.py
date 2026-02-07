#!/usr/bin/env python3
"""
Split extracted letters into individual text files.
"""

import json
import os
import re


def sanitize_filename(text):
    """Convert text to a safe filename"""
    # Remove or replace problematic characters
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text[:50]  # Limit length


def load_letters(filename='extracted_letters.json'):
    """Load letters from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_letter_file(letter, output_dir='letters'):
    """Create individual text file for a letter"""
    letter_id = letter['id']
    
    # Create filename
    recipient = letter.get('recipient', 'Unknown')
    recipient_safe = sanitize_filename(recipient)
    
    date = letter.get('date', '')
    if date:
        date_safe = sanitize_filename(date)
        filename = f"letter_{letter_id:03d}_{recipient_safe}_{date_safe}.txt"
    else:
        filename = f"letter_{letter_id:03d}_{recipient_safe}.txt"
    
    filepath = os.path.join(output_dir, filename)
    
    # Write letter content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"LETTER #{letter['id']}\n")
        f.write("=" * 80 + "\n\n")
        
        if letter.get('recipient'):
            f.write(f"TO: {letter['recipient']}\n")
        if letter.get('location'):
            f.write(f"LOCATION: {letter['location']}\n")
        if letter.get('date'):
            f.write(f"DATE: {letter['date']}\n")
        f.write(f"SOURCE: Lines {letter['start_line']}-{letter['end_line']} of LifeLettersAndSpeeches.txt\n")
        f.write("\n" + "-" * 80 + "\n\n")
        
        if letter.get('salutation'):
            f.write(f"{letter['salutation']}\n\n")
        
        f.write(f"{letter['body']}\n")
        
        if letter.get('closing'):
            f.write(f"\n{letter['closing']}\n")
    
    return filename


def main():
    output_dir = 'letters'
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}/")
    else:
        print(f"Using existing directory: {output_dir}/")
    
    # Load letters
    print("\nLoading letters from extracted_letters.json...")
    letters = load_letters()
    print(f"Loaded {len(letters)} letters")
    
    # Create individual files
    print(f"\nCreating individual letter files in {output_dir}/...")
    created_files = []
    
    for letter in letters:
        filename = create_letter_file(letter, output_dir)
        created_files.append(filename)
    
    print(f"\nSuccessfully created {len(created_files)} letter files")
    print(f"\nFirst 10 files:")
    for filename in created_files[:10]:
        print(f"  - {filename}")
    
    if len(created_files) > 10:
        print(f"  ... and {len(created_files) - 10} more")
    
    print(f"\nAll letters saved in: {output_dir}/")


if __name__ == "__main__":
    main()

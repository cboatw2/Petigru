#!/usr/bin/env python3
"""
Reorder letter files by source line numbers in ascending order.
"""

import os
import re
import shutil


def extract_line_number(filepath):
    """Extract the starting line number from a letter file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('SOURCE:'):
                # Extract "Lines X-Y" pattern
                match = re.search(r'Lines (\d+)-(\d+)', line)
                if match:
                    return int(match.group(1))
    return float('inf')  # If no line number found, put at end


def get_letter_info(filepath):
    """Extract letter metadata from file"""
    basename = os.path.basename(filepath)
    start_line = extract_line_number(filepath)
    return {
        'original_path': filepath,
        'basename': basename,
        'start_line': start_line
    }


def main():
    letters_dir = 'letters'
    
    if not os.path.exists(letters_dir):
        print(f"Error: {letters_dir}/ directory not found")
        return
    
    # Get all letter files
    letter_files = [
        os.path.join(letters_dir, f) 
        for f in os.listdir(letters_dir) 
        if f.startswith('letter_') and f.endswith('.txt')
    ]
    
    print(f"Found {len(letter_files)} letter files")
    print("\nExtracting source line numbers...")
    
    # Get info for each letter
    letters_info = [get_letter_info(f) for f in letter_files]
    
    # Sort by start line
    letters_info.sort(key=lambda x: x['start_line'])
    
    print("Sorted by source line numbers")
    
    # Create temporary directory for renaming
    temp_dir = 'letters_temp'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Copy files to temp directory with new names
    print("\nRenaming files in chronological order...")
    for idx, info in enumerate(letters_info, 1):
        old_path = info['original_path']
        old_basename = info['basename']
        
        # Extract recipient and date from old filename
        # Remove the old letter number prefix
        match = re.match(r'letter_\d+_(.+)\.txt', old_basename)
        if match:
            suffix = match.group(1)
            new_basename = f"letter_{idx:03d}_{suffix}.txt"
        else:
            new_basename = f"letter_{idx:03d}.txt"
        
        new_path = os.path.join(temp_dir, new_basename)
        shutil.copy2(old_path, new_path)
        
        if idx <= 10:
            print(f"  {idx:3d}. Line {info['start_line']:5d}: {new_basename}")
    
    if len(letters_info) > 10:
        print(f"  ... and {len(letters_info) - 10} more files")
    
    # Remove old directory and rename temp
    print(f"\nReplacing {letters_dir}/ with reordered files...")
    shutil.rmtree(letters_dir)
    os.rename(temp_dir, letters_dir)
    
    print(f"\n✓ Successfully reordered {len(letters_info)} files by source line numbers")
    print(f"  Files are now in chronological order as they appear in the book")


if __name__ == "__main__":
    main()

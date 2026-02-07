#!/usr/bin/env python3
"""
Search tool for Petigru letters.
Allows searching by recipient, date, content, or entities.
"""

import json
import re
from typing import List, Dict
import argparse


def load_letters(filename: str = 'extracted_letters.json') -> List[Dict]:
    """Load letters from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_entity_analysis(filename: str = 'entity_analysis.json') -> Dict:
    """Load entity analysis from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_by_recipient(letters: List[Dict], recipient: str) -> List[Dict]:
    """Search for letters by recipient name"""
    pattern = re.compile(recipient, re.IGNORECASE)
    return [letter for letter in letters if letter.get('recipient') and pattern.search(letter['recipient'])]


def search_by_date(letters: List[Dict], date_query: str) -> List[Dict]:
    """Search for letters by date (year, month, or full date)"""
    pattern = re.compile(date_query, re.IGNORECASE)
    return [letter for letter in letters if letter.get('date') and pattern.search(letter['date'])]


def search_by_content(letters: List[Dict], query: str) -> List[Dict]:
    """Search for letters containing specific text"""
    pattern = re.compile(query, re.IGNORECASE)
    results = []
    for letter in letters:
        if pattern.search(letter['body']):
            results.append(letter)
    return results


def search_by_entity(letters: List[Dict], entity_analysis: Dict, entity_name: str, entity_type: str = None) -> List[Dict]:
    """Search for letters mentioning a specific entity (person or location)"""
    matching_letters = []
    
    for letter_data in entity_analysis['letter_entities']:
        letter_id = letter_data['letter_id']
        entities = letter_data['entities']
        
        # Search in all entity types or specific type
        types_to_search = [entity_type] if entity_type else ['PERSON', 'GPE', 'LOC', 'ORG']
        
        for etype in types_to_search:
            if etype in entities:
                for entity in entities[etype]:
                    if entity_name.lower() in entity.lower():
                        # Find the corresponding letter
                        letter = next((l for l in letters if l['id'] == letter_id), None)
                        if letter and letter not in matching_letters:
                            matching_letters.append(letter)
                        break
    
    return matching_letters


def display_letter(letter: Dict, show_full: bool = False):
    """Display a letter in formatted output"""
    print("\n" + "=" * 80)
    print(f"LETTER #{letter['id']}")
    print("=" * 80)
    if letter.get('recipient'):
        print(f"TO: {letter['recipient']}")
    if letter.get('location'):
        print(f"LOCATION: {letter['location']}")
    if letter.get('date'):
        print(f"DATE: {letter['date']}")
    print(f"SOURCE: Lines {letter['start_line']}-{letter['end_line']}")
    print("-" * 80)
    
    if show_full:
        if letter.get('salutation'):
            print(f"{letter['salutation']}\n")
        print(letter['body'])
        if letter.get('closing'):
            print(f"\n{letter['closing']}")
    else:
        # Show excerpt
        body = letter['body']
        if len(body) > 300:
            print(body[:300] + "...")
        else:
            print(body)
        if not show_full and len(body) > 300:
            print(f"\n[Use --full to see complete letter]")


def main():
    parser = argparse.ArgumentParser(
        description='Search Petigru letters by recipient, date, content, or entities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by recipient
  python3 search_letters.py --recipient Elliott
  
  # Search by date/year
  python3 search_letters.py --date 1832
  
  # Search by content
  python3 search_letters.py --content nullification
  
  # Search by person mentioned
  python3 search_letters.py --entity Calhoun --type PERSON
  
  # Search by location mentioned
  python3 search_letters.py --entity Charleston --type GPE
  
  # Show full letter text
  python3 search_letters.py --recipient Elliott --full
        """
    )
    
    parser.add_argument('--recipient', '-r', help='Search by recipient name')
    parser.add_argument('--date', '-d', help='Search by date (year, month, or full date)')
    parser.add_argument('--content', '-c', help='Search letter content')
    parser.add_argument('--entity', '-e', help='Search by entity mentioned (person, location, etc.)')
    parser.add_argument('--type', '-t', choices=['PERSON', 'GPE', 'LOC', 'ORG'],
                       help='Entity type to search for (use with --entity)')
    parser.add_argument('--full', '-f', action='store_true',
                       help='Show full letter text (default: excerpt)')
    parser.add_argument('--limit', '-l', type=int, default=10,
                       help='Maximum number of results to show (default: 10)')
    
    args = parser.parse_args()
    
    # Load data
    print("Loading letters...")
    letters = load_letters()
    print(f"Loaded {len(letters)} letters")
    
    # Perform search
    results = []
    
    if args.recipient:
        print(f"\nSearching for recipient: {args.recipient}")
        results = search_by_recipient(letters, args.recipient)
    elif args.date:
        print(f"\nSearching for date: {args.date}")
        results = search_by_date(letters, args.date)
    elif args.content:
        print(f"\nSearching for content: {args.content}")
        results = search_by_content(letters, args.content)
    elif args.entity:
        print("Loading entity analysis...")
        entity_analysis = load_entity_analysis()
        print(f"\nSearching for entity: {args.entity}")
        if args.type:
            print(f"Type: {args.type}")
        results = search_by_entity(letters, entity_analysis, args.entity, args.type)
    else:
        parser.print_help()
        return
    
    # Display results
    print(f"\nFound {len(results)} matching letters")
    
    if results:
        # Limit results if necessary
        display_results = results[:args.limit] if args.limit else results
        
        for letter in display_results:
            display_letter(letter, args.full)
        
        if len(results) > args.limit:
            print(f"\n... and {len(results) - args.limit} more results (use --limit to see more)")
    else:
        print("\nNo matching letters found.")


if __name__ == "__main__":
    main()

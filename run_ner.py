#!/usr/bin/env python3
"""
Run Named Entity Recognition (NER) on extracted letters to find person and location entities.
Uses spaCy for NER.
"""

import json
import spacy
from collections import Counter
from typing import List, Dict, Set
import sys


def load_letters(filename: str) -> List[Dict]:
    """Load letters from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_entities(text: str, nlp) -> Dict[str, List[str]]:
    """
    Extract named entities from text using spaCy.
    Returns dict with entity types as keys and lists of entities as values.
    """
    doc = nlp(text)
    
    entities = {
        'PERSON': [],
        'GPE': [],  # Geopolitical Entity (countries, cities, states)
        'LOC': [],  # Non-GPE locations
        'ORG': [],  # Organizations
        'DATE': [],  # Dates
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    return entities


def analyze_letters(letters: List[Dict], nlp) -> Dict:
    """Analyze all letters and extract entities"""
    
    all_entities = {
        'PERSON': Counter(),
        'GPE': Counter(),
        'LOC': Counter(),
        'ORG': Counter(),
        'DATE': Counter(),
    }
    
    letter_entities = []
    
    for letter in letters:
        text = letter['body']
        if letter.get('salutation'):
            text = letter['salutation'] + ' ' + text
        if letter.get('closing'):
            text = text + ' ' + letter['closing']
            
        entities = extract_entities(text, nlp)
        
        # Add to global counters
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                all_entities[entity_type][entity] += 1
        
        # Store per-letter entities
        letter_entities.append({
            'letter_id': letter['id'],
            'recipient': letter.get('recipient'),
            'date': letter.get('date'),
            'entities': entities
        })
    
    return {
        'all_entities': all_entities,
        'letter_entities': letter_entities
    }


def save_entity_analysis(analysis: Dict, output_file: str):
    """Save entity analysis to JSON file"""
    # Convert Counter objects to dicts for JSON serialization
    serializable_analysis = {
        'all_entities': {
            entity_type: dict(counter.most_common())
            for entity_type, counter in analysis['all_entities'].items()
        },
        'letter_entities': analysis['letter_entities']
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Saved entity analysis to {output_file}")


def print_entity_summary(analysis: Dict):
    """Print a summary of extracted entities"""
    print("\n" + "=" * 80)
    print("NAMED ENTITY RECOGNITION RESULTS")
    print("=" * 80)
    
    all_entities = analysis['all_entities']
    
    print("\nMost Frequent PERSONS:")
    print("-" * 40)
    for person, count in all_entities['PERSON'].most_common(20):
        print(f"  {person:40} {count:4} mentions")
    
    print("\nMost Frequent LOCATIONS (GPE - Cities/States/Countries):")
    print("-" * 40)
    for loc, count in all_entities['GPE'].most_common(20):
        print(f"  {loc:40} {count:4} mentions")
    
    print("\nMost Frequent LOCATIONS (Other):")
    print("-" * 40)
    for loc, count in all_entities['LOC'].most_common(20):
        print(f"  {loc:40} {count:4} mentions")
    
    print("\nMost Frequent ORGANIZATIONS:")
    print("-" * 40)
    for org, count in all_entities['ORG'].most_common(20):
        print(f"  {org:40} {count:4} mentions")
    
    print("\n" + "=" * 80)
    print(f"Total unique persons: {len(all_entities['PERSON'])}")
    print(f"Total unique locations (GPE): {len(all_entities['GPE'])}")
    print(f"Total unique locations (other): {len(all_entities['LOC'])}")
    print(f"Total unique organizations: {len(all_entities['ORG'])}")
    print("=" * 80)


def create_entity_report(analysis: Dict, output_file: str):
    """Create a human-readable report of entities"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NAMED ENTITY RECOGNITION REPORT\n")
        f.write("Letters from: Life, Letters, and Speeches of James Louis Petigru\n")
        f.write("=" * 80 + "\n\n")
        
        all_entities = analysis['all_entities']
        
        # Persons
        f.write("\nMOST FREQUENT PERSONS\n")
        f.write("-" * 80 + "\n")
        for person, count in all_entities['PERSON'].most_common(50):
            f.write(f"{person:50} {count:4} mentions\n")
        
        # Locations (GPE)
        f.write("\n\nMOST FREQUENT LOCATIONS (Cities/States/Countries)\n")
        f.write("-" * 80 + "\n")
        for loc, count in all_entities['GPE'].most_common(50):
            f.write(f"{loc:50} {count:4} mentions\n")
        
        # Locations (Other)
        f.write("\n\nOTHER LOCATIONS\n")
        f.write("-" * 80 + "\n")
        for loc, count in all_entities['LOC'].most_common(50):
            f.write(f"{loc:50} {count:4} mentions\n")
        
        # Organizations
        f.write("\n\nMOST FREQUENT ORGANIZATIONS\n")
        f.write("-" * 80 + "\n")
        for org, count in all_entities['ORG'].most_common(50):
            f.write(f"{org:50} {count:4} mentions\n")
        
        # Summary statistics
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total unique persons: {len(all_entities['PERSON'])}\n")
        f.write(f"Total unique locations (GPE): {len(all_entities['GPE'])}\n")
        f.write(f"Total unique locations (other): {len(all_entities['LOC'])}\n")
        f.write(f"Total unique organizations: {len(all_entities['ORG'])}\n")
        f.write(f"Total letters analyzed: {len(analysis['letter_entities'])}\n")
    
    print(f"Saved entity report to {output_file}")


def main():
    print("Loading spaCy English model...")
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("\nError: spaCy English model not found!")
        print("Please install it with:")
        print("  python -m spacy download en_core_web_sm")
        sys.exit(1)
    
    input_file = "extracted_letters.json"
    output_json = "entity_analysis.json"
    output_report = "entity_report.txt"
    
    print(f"Loading letters from {input_file}...")
    letters = load_letters(input_file)
    print(f"Loaded {len(letters)} letters")
    
    print("Analyzing letters and extracting named entities...")
    analysis = analyze_letters(letters, nlp)
    
    print_entity_summary(analysis)
    
    save_entity_analysis(analysis, output_json)
    create_entity_report(analysis, output_report)
    
    print("\nAnalysis complete!")
    print(f"- JSON output: {output_json}")
    print(f"- Text report: {output_report}")


if __name__ == "__main__":
    main()

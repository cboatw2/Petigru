#!/usr/bin/env python3
"""
Create visualizations of the entity analysis results.
"""

import json
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np


def load_entity_analysis(filename: str):
    """Load entity analysis from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_top_persons(entities, output_file='top_persons.png', top_n=20):
    """Create bar chart of most mentioned persons"""
    person_data = entities['all_entities']['PERSON']
    
    # Filter out common false positives
    filtered = {k: v for k, v in person_data.items() 
                if k not in ['Adieu', 'Ma', 'Dear', 'Yours', 'CHAPTER', 'Sir']}
    
    # Get top N
    sorted_persons = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names = [item[0] for item in sorted_persons]
    counts = [item[1] for item in sorted_persons]
    
    # Create plot
    plt.figure(figsize=(12, 8))
    y_pos = np.arange(len(names))
    plt.barh(y_pos, counts, color='steelblue')
    plt.yticks(y_pos, names)
    plt.xlabel('Number of Mentions')
    plt.title(f'Top {top_n} Most Mentioned Persons in Petigru Letters')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved person chart to {output_file}")
    plt.close()


def plot_top_locations(entities, output_file='top_locations.png', top_n=20):
    """Create bar chart of most mentioned locations"""
    location_data = entities['all_entities']['GPE']
    
    # Filter out generic terms
    filtered = {k: v for k, v in location_data.items() 
                if k not in ['Fort', 'States', 'Parent', 'House']}
    
    # Get top N
    sorted_locs = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names = [item[0] for item in sorted_locs]
    counts = [item[1] for item in sorted_locs]
    
    # Create plot
    plt.figure(figsize=(12, 8))
    y_pos = np.arange(len(names))
    plt.barh(y_pos, counts, color='darkgreen')
    plt.yticks(y_pos, names)
    plt.xlabel('Number of Mentions')
    plt.title(f'Top {top_n} Most Mentioned Locations in Petigru Letters')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved location chart to {output_file}")
    plt.close()


def plot_entity_distribution(entities, output_file='entity_distribution.png'):
    """Create pie chart showing distribution of entity types"""
    entity_counts = {
        'Persons': len(entities['all_entities']['PERSON']),
        'Locations (GPE)': len(entities['all_entities']['GPE']),
        'Locations (Other)': len(entities['all_entities']['LOC']),
        'Organizations': len(entities['all_entities']['ORG']),
    }
    
    # Create plot
    plt.figure(figsize=(10, 8))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    plt.pie(entity_counts.values(), labels=entity_counts.keys(), autopct='%1.1f%%',
            startangle=90, colors=colors)
    plt.title('Distribution of Unique Entity Types')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved distribution chart to {output_file}")
    plt.close()


def create_timeline_data(entities, letters_file='extracted_letters.json'):
    """Create timeline of letter dates with entity mentions"""
    # Load letters to get dates
    with open(letters_file, 'r', encoding='utf-8') as f:
        letters = json.load(f)
    
    # Extract years from dates
    years = []
    for letter in letters:
        date = letter.get('date', '')
        if date:
            # Try to extract year (last 4 digits)
            parts = date.split()
            for part in parts:
                if part.replace('.', '').replace(',', '').isdigit():
                    year_str = part.replace('.', '').replace(',', '')
                    if len(year_str) == 4 and year_str.startswith('18'):
                        years.append(int(year_str))
                        break
    
    if years:
        year_counts = Counter(years)
        return year_counts
    return None


def plot_timeline(entities, output_file='letter_timeline.png'):
    """Create timeline of letters by year"""
    year_counts = create_timeline_data(entities)
    
    if not year_counts:
        print("Could not create timeline - insufficient date information")
        return
    
    sorted_years = sorted(year_counts.items())
    years = [item[0] for item in sorted_years]
    counts = [item[1] for item in sorted_years]
    
    # Create plot
    plt.figure(figsize=(14, 6))
    plt.bar(years, counts, color='coral', width=0.8)
    plt.xlabel('Year')
    plt.ylabel('Number of Letters')
    plt.title('Distribution of Petigru Letters Over Time')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved timeline chart to {output_file}")
    plt.close()


def generate_statistics_summary(entities, output_file='statistics_summary.txt'):
    """Generate a comprehensive statistics summary"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PETIGRU LETTERS - STATISTICAL SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        # Entity counts
        person_count = len(entities['all_entities']['PERSON'])
        gpe_count = len(entities['all_entities']['GPE'])
        loc_count = len(entities['all_entities']['LOC'])
        org_count = len(entities['all_entities']['ORG'])
        
        f.write("ENTITY COUNTS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Unique Persons: {person_count}\n")
        f.write(f"Unique Locations (Cities/States/Countries): {gpe_count}\n")
        f.write(f"Unique Locations (Other): {loc_count}\n")
        f.write(f"Unique Organizations: {org_count}\n")
        f.write(f"Total Unique Entities: {person_count + gpe_count + loc_count + org_count}\n\n")
        
        # Total mentions
        person_mentions = sum(entities['all_entities']['PERSON'].values())
        gpe_mentions = sum(entities['all_entities']['GPE'].values())
        loc_mentions = sum(entities['all_entities']['LOC'].values())
        org_mentions = sum(entities['all_entities']['ORG'].values())
        
        f.write("TOTAL MENTIONS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Person Mentions: {person_mentions}\n")
        f.write(f"Location Mentions (GPE): {gpe_mentions}\n")
        f.write(f"Location Mentions (Other): {loc_mentions}\n")
        f.write(f"Organization Mentions: {org_mentions}\n")
        f.write(f"Total Entity Mentions: {person_mentions + gpe_mentions + loc_mentions + org_mentions}\n\n")
        
        # Average mentions per unique entity
        f.write("AVERAGE MENTIONS PER UNIQUE ENTITY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Persons: {person_mentions/person_count:.2f}\n")
        f.write(f"Locations (GPE): {gpe_mentions/gpe_count:.2f}\n")
        if loc_count > 0:
            f.write(f"Locations (Other): {loc_mentions/loc_count:.2f}\n")
        f.write(f"Organizations: {org_mentions/org_count:.2f}\n\n")
        
        # Number of letters
        letter_count = len(entities['letter_entities'])
        f.write(f"Total Letters Analyzed: {letter_count}\n")
        f.write(f"Average Entities per Letter: {(person_mentions + gpe_mentions + loc_mentions + org_mentions)/letter_count:.2f}\n")
    
    print(f"Saved statistics summary to {output_file}")


def main():
    try:
        import matplotlib.pyplot as plt
        has_matplotlib = True
    except ImportError:
        print("Warning: matplotlib not installed. Skipping visualizations.")
        print("Install with: pip3 install matplotlib")
        has_matplotlib = False
    
    print("Loading entity analysis...")
    entities = load_entity_analysis('entity_analysis.json')
    
    print("\nGenerating statistics summary...")
    generate_statistics_summary(entities)
    
    if has_matplotlib:
        print("\nGenerating visualizations...")
        plot_top_persons(entities)
        plot_top_locations(entities)
        plot_entity_distribution(entities)
        plot_timeline(entities)
        print("\nVisualization complete!")
    else:
        print("\nSkipping visualizations (matplotlib not available)")


if __name__ == "__main__":
    main()

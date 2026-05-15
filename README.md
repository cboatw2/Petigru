# Letter Extraction and Named Entity Recognition

This project extracts letters from "Life, Letters, and Speeches of James Louis Petigru: The Union Man of South Carolina" and performs Named Entity Recognition (NER) to identify persons and locations mentioned in the correspondence.

## Project Overview

James Louis Petigru (1789-1863) was a prominent South Carolina lawyer and Union supporter during the Nullification Crisis and Civil War era. This collection of his letters provides valuable historical insights into antebellum South Carolina politics and society.

## Files

### Input
- `LifeLettersAndSpeeches.txt` - Original digitized book text

### Scripts
- `extract_letters.py` - Extracts letters from the narrative text
- `run_ner.py` - Performs Named Entity Recognition on extracted letters
- `visualize_entities.py` - Creates visualizations and statistical summaries
- `search_letters.py` - Search tool for finding specific letters

### Output
- `extracted_letters.json` - Structured JSON data of all extracted letters
- `extracted_letters.txt` - Human-readable format of extracted letters
- `entity_analysis.json` - Detailed NER analysis with entity counts
- `entity_report.txt` - Human-readable NER report
- `statistics_summary.txt` - Statistical summary of entities
- `top_persons.png` - Bar chart of most mentioned persons
- `top_locations.png` - Bar chart of most mentioned locations
- `entity_distribution.png` - Pie chart of entity type distribution
- `letter_timeline.png` - Timeline of letters by year

## Usage

### 1. Extract Letters

```bash
python3 extract_letters.py
```

This script:
- Identifies letters by their distinctive format (TO [NAME], Location, Date, Salutation)
- Extracts 185 letters from the book
- Saves results in both JSON and text formats

### 2. Run Named Entity Recognition

```bash
python3 run_ner.py
```

Folder-based NER (PerryLetters-style)

If you want to run NER directly on the per-letter `.txt` files in `letters/` and produce a simple long-form CSV (like the PerryLetters workflow):

```bash
python3 ner_letters_folder.py --letters-dir letters --output Petigru_NER_entities.csv
```

Output columns match the PerryLetters NER CSV format:
- `letter_number`
- `entity_name`
- `entity_type` (PERSON or LOCATION)

This script:
- Uses spaCy's English language model for NER
- Identifies persons, locations, organizations, and dates
- Generates comprehensive reports

### 3. Generate Visualizations

```bash
python3 visualize_entities.py
```

This script:
- Creates bar charts of top persons and locations
- Generates entity distribution pie chart
- Creates timeline of letters by year
- Produces statistical summary

### 4. Search Letters

```bash
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
```

## Installation

### Requirements

```bash
pip3 install spacy matplotlib
python3 -m spacy download en_core_web_sm
```

All scripts are written in Python 3 and require:
- `spacy` - For Named Entity Recognition
- `matplotlib` - For generating visualizations

## Results Summary

### Letters Extracted: 185

### Top Named Entities

**Most Mentioned Persons:**
1. Petigru - 175 mentions
2. James Louis Petigru - 151 mentions
3. Jane - 58 mentions
4. Hamilton - 53 mentions
5. Caroline - 50 mentions

**Most Mentioned Locations:**
1. Charleston - 142 mentions
2. South Carolina - 76 mentions
3. United States - 47 mentions
4. Washington - 46 mentions
5. Georgia - 41 mentions

**Statistics:**
- Total unique persons: 1,006
- Total unique locations (cities/states): 256
- Total unique organizations: 544

## Letter Format

Letters typically follow this structure:

```
TO [RECIPIENT NAME]
Location, Date
Dear [Name]:

[Letter body]

[Closing],
[Signature]
```

## Historical Context

The letters span the critical period of:
- The Nullification Crisis (1828-1833)
- Antebellum South Carolina politics
- The lead-up to the Civil War
- Petigru's role as a Union supporter in a secessionist state

## Challenges & Solutions

### Challenge: Identifying Letters in Narrative
The book intersperses letters with biographical narrative and historical commentary.

**Solution:** Pattern matching using regular expressions to identify:
- "TO [NAME]" headers in all caps
- Location and date lines
- Salutations (Dear, My dear, etc.)
- Letter body boundaries

### Challenge: False Positives
Some text patterns resembled letters but weren't actual correspondence (e.g., memorial inscriptions).

**Solution:** 
- Minimum content length requirements
- Contextual analysis of surrounding text
- Manual verification of edge cases

### Challenge: NER Accuracy
Historical names and 19th-century language can confuse modern NER models.

**Solution:**
- Using spaCy's robust pre-trained model
- Post-processing to identify common entities
- Entity frequency analysis to surface important figures

## Future Enhancements

Potential improvements:
1. Fine-tune NER model on 19th-century historical texts
2. Add relationship mapping between entities
3. Create timeline visualization of correspondence
4. Link entities to external historical databases
5. Improve letter boundary detection accuracy
6. Add sentiment analysis
7. Create interactive visualization dashboard

## Notes

- Some letters may be partially extracted due to unclear boundaries
- NER may misidentify some historical names (e.g., "Adieu" as a person)
- Manual review recommended for critical research
- Line numbers in extracted letters refer to the original text file

## License

This project processes public domain historical texts.

## Author

Extraction scripts created for historical text analysis.

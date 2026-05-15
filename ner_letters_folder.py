#!/usr/bin/env python3
"""Petigru letters: folder-based NER (PerryLetters-style).

This mirrors the approach used in PerryLetters/BFPerry_Letters_NER/BFPerry_Letters_NERForSplitLetters.py:
- load spaCy English model
- iterate through a directory of .txt letters
- extract PERSON and GPE entities
- write a simple long-form CSV: letter_number, entity_name, entity_type

Default input: ./letters
Default output: ./Petigru_NER_entities.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import spacy


LETTER_NUMBER_RE = re.compile(r"letter_(\d+)", re.IGNORECASE)


def _extract_letter_number(filename: str) -> str:
    m = LETTER_NUMBER_RE.search(filename)
    return m.group(1) if m else ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Run spaCy NER on Petigru/letters and extract PERSON + location (GPE) entities.")
    ap.add_argument("--letters-dir", default="letters", help="Directory containing per-letter .txt files")
    ap.add_argument("--output", default="Petigru_NER_entities.csv", help="Output CSV path")
    ap.add_argument("--model", default="en_core_web_sm", help="spaCy model name (default: en_core_web_sm)")
    ap.add_argument("--max-files", type=int, default=0, help="If set (>0), process only the first N .txt files (for quick test runs)")
    ap.add_argument(
        "--include-loc",
        action="store_true",
        help="Also treat spaCy LOC entities as LOCATION (default extracts only GPE as LOCATION, matching PerryLetters).",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent
    letters_dir = (repo_root / args.letters_dir).resolve()
    output_csv = (repo_root / args.output).resolve()

    if not letters_dir.exists() or not letters_dir.is_dir():
        raise SystemExit(f"letters-dir not found or not a directory: {letters_dir}")

    try:
        nlp = spacy.load(args.model)
    except OSError as e:
        raise SystemExit(
            f"spaCy model {args.model!r} not installed. Try: python -m spacy download {args.model}"
        ) from e

    entities: list[list[str]] = []

    letter_files = sorted([p for p in letters_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
    if not letter_files:
        raise SystemExit(f"No .txt files found in: {letters_dir}")

    if args.max_files and args.max_files > 0:
        letter_files = letter_files[: args.max_files]

    for letter_file in letter_files:
        text = letter_file.read_text(encoding="utf-8", errors="ignore")
        letter_number = _extract_letter_number(letter_file.name)

        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities.append([letter_number, ent.text.strip(), "PERSON"])
            elif ent.label_ == "GPE":
                # Match PerryLetters convention: GPE -> LOCATION
                entities.append([letter_number, ent.text.strip(), "LOCATION"])
            elif args.include_loc and ent.label_ == "LOC":
                entities.append([letter_number, ent.text.strip(), "LOCATION"])

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["letter_number", "entity_name", "entity_type"])
        writer.writerows(entities)

    print(f"Processed {len(letter_files)} letters")
    print(f"Wrote {len(entities)} entities to {output_csv}")


if __name__ == "__main__":
    main()

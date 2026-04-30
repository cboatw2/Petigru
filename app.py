from flask import Flask, render_template, request, abort, jsonify
from markupsafe import Markup, escape
import os
import re
import json

app = Flask(__name__)


@app.template_filter("highlight")
def highlight_filter(text: str, query: str) -> Markup:
    """Escape text then wrap every occurrence of query in a highlight span."""
    if not query:
        return Markup(escape(text))
    escaped_text = str(escape(text))
    escaped_query = re.escape(str(escape(query)))
    highlighted = re.sub(
        f"({escaped_query})",
        r'<mark class="search-highlight">\1</mark>',
        escaped_text,
        flags=re.IGNORECASE,
    )
    return Markup(highlighted)


LETTERS_DIR = os.path.join(os.path.dirname(__file__), "letters")
NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.json")


def load_notes() -> dict:
    """Load all notes from notes.json. Returns dict keyed by letter number (str)."""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_note(number: int, text: str):
    """Persist a note for the given letter number."""
    notes = load_notes()
    key = str(number)
    if text.strip():
        notes[key] = text
    else:
        notes.pop(key, None)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# Metadata parsing helpers
# ---------------------------------------------------------------------------

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

MONTH_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_year_from_string(s: str):
    """Return the first 4-digit year found in a string, or None."""
    m = re.search(r'\b(1[6-9]\d{2}|20\d{2})\b', s)
    return int(m.group(1)) if m else None


def parse_month_from_string(s: str):
    """Return the integer month (1-12) found in a string, or None."""
    sl = s.lower()
    for name, num in MONTH_MAP.items():
        if name in sl:
            return num
    for abbr, num in MONTH_ABBR.items():
        if abbr in sl:
            return num
    return None


def normalize_name(raw: str) -> str:
    """Convert 'MRS_JANE_PETIGRU_NORTH' -> 'Mrs. Jane Petigru North'."""
    parts = [p.strip() for p in raw.replace("_", " ").split() if p.strip()]
    result = []
    for p in parts:
        if p.upper() in ("MRS", "MR", "DR", "REV", "MISS", "GEN", "COL", "CAPT", "SGT", "LT"):
            result.append(p.title() + ".")
        else:
            result.append(p.title())
    return " ".join(result)


def parse_file_header(content: str) -> dict:
    """
    Parse structured header fields from letter file content.
    Returns a dict with keys: to, date_str, location.
    """
    info = {"to": None, "date_str": None, "location": None}
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("TO:"):
            raw = line[3:].strip()
            # Collapse extra spaces
            info["to"] = " ".join(raw.split())
        elif line.upper().startswith("DATE:"):
            info["date_str"] = " ".join(line[5:].strip().split())
        elif line.upper().startswith("LOCATION:"):
            info["location"] = " ".join(line[9:].strip().split())
    return info


def parse_filename_recipient(filename: str) -> str:
    """
    Extract the recipient portion from a filename like
    letter_003_MRS_JANE_PETIGRU_NORTH_5_January_1847.txt
    Returns a human-readable name.
    """
    # Strip extension and prefix
    stem = filename.replace(".txt", "")
    # Remove 'letter_NNN_' prefix
    stem = re.sub(r'^letter_\d+_', '', stem)

    # Try to strip a trailing date pattern (Month_Year, Day_Month_Year, etc.)
    # Remove trailing 4-digit year
    stem = re.sub(r'_?\b1[6-9]\d{2}\b.*$', '', stem)
    # Remove trailing month names
    for m in list(MONTH_MAP.keys()) + list(MONTH_ABBR.keys()):
        stem = re.sub(r'_?' + m + r'.*$', stem, stem, flags=re.IGNORECASE)
        # Simpler approach: just strip month and what follows
    # Strip everything from the first standalone month name or day-number onward
    parts = re.sub(r'_?' + r'(?:' + '|'.join(list(MONTH_MAP.keys()) + list(MONTH_ABBR.keys())) + r').*$', '', stem, flags=re.IGNORECASE)
    # Also strip trailing standalone numbers (days/years)
    parts = re.sub(r'_\d+$', '', parts)
    return normalize_name(parts)


def load_letter(filename: str) -> dict:
    """Load a single letter file and return a metadata dict."""
    filepath = os.path.join(LETTERS_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        content = f"[Error reading file: {e}]"

    # Letter number from filename
    m = re.match(r'^letter_(\d+)_', filename)
    number = int(m.group(1)) if m else 0

    # Parse header fields
    header = parse_file_header(content)

    # Recipient: prefer file header TO: field, fall back to filename
    if header["to"]:
        recipient = " ".join(w.title() if w.upper() not in
                             ("MRS", "MR", "DR", "REV", "MISS") else w.title() + "."
                             for w in header["to"].split())
    else:
        recipient = parse_filename_recipient(filename)

    # Date / year
    date_str = header["date_str"] or ""
    year = parse_year_from_string(date_str)
    if not year:
        year = parse_year_from_string(filename)
    month = parse_month_from_string(date_str) if date_str else parse_month_from_string(filename)

    # Sort key: year * 10000 + month * 100 + letter_number (fallback)
    sort_key = (year or 9999, month or 0, number)

    return {
        "filename": filename,
        "number": number,
        "recipient": recipient,
        "date_str": date_str,
        "year": year,
        "month": month,
        "location": header["location"] or "",
        "content": content,
        "sort_key": sort_key,
    }


def load_all_letters() -> list:
    """Load and return all letter dicts sorted by date."""
    files = sorted(
        f for f in os.listdir(LETTERS_DIR)
        if f.startswith("letter_") and f.endswith(".txt")
    )
    letters = [load_letter(f) for f in files]
    letters.sort(key=lambda x: x["sort_key"])
    return letters


def get_letters():
    return load_all_letters()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    letters = get_letters()

    # Build filter lists
    years = sorted({l["year"] for l in letters if l["year"]})
    recipients = sorted({l["recipient"] for l in letters if l["recipient"]})

    # Apply filters from query params
    sel_year = request.args.get("year", "").strip()
    sel_recipient = request.args.get("recipient", "").strip()
    query = request.args.get("query", "").strip()

    filtered = letters
    if sel_year:
        try:
            yr = int(sel_year)
            filtered = [l for l in filtered if l["year"] == yr]
        except ValueError:
            pass
    if sel_recipient:
        filtered = [l for l in filtered if sel_recipient.lower() in l["recipient"].lower()]
    if query:
        ql = query.lower()
        filtered = [
            l for l in filtered
            if ql in l["recipient"].lower()
            or ql in (l["date_str"] or "").lower()
            or ql in (l["location"] or "").lower()
            or ql in l["content"].lower()
        ]

    notes = load_notes()
    return render_template(
        "index.html",
        letters=filtered,
        years=years,
        recipients=recipients,
        sel_year=sel_year,
        sel_recipient=sel_recipient,
        query=query,
        total=len(letters),
        notes=notes,
    )


@app.route("/letter/<int:number>")
def letter(number):
    letters = get_letters()
    match = next((l for l in letters if l["number"] == number), None)
    if not match:
        abort(404)

    # Find prev/next for navigation
    idx = letters.index(match)
    prev_letter = letters[idx - 1] if idx > 0 else None
    next_letter = letters[idx + 1] if idx < len(letters) - 1 else None

    # Highlight search term if coming from a search
    query = request.args.get("query", "").strip()

    notes = load_notes()
    note_text = notes.get(str(number), "")
    return render_template(
        "letter.html",
        letter=match,
        prev_letter=prev_letter,
        next_letter=next_letter,
        query=query,
        note_text=note_text,
    )


@app.route("/api/note/<int:number>", methods=["POST"])
def api_save_note(number):
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("note", "")
    save_note(number, text)
    return jsonify({"status": "ok", "number": number})


@app.route("/recipients")
def recipients():
    letters = get_letters()
    # Group by recipient
    from collections import defaultdict
    grouped = defaultdict(list)
    for l in letters:
        grouped[l["recipient"]].append(l)
    grouped = dict(sorted(grouped.items()))
    return render_template("recipients.html", grouped=grouped)


@app.route("/years")
def by_year():
    letters = get_letters()
    from collections import defaultdict
    grouped = defaultdict(list)
    for l in letters:
        yr = l["year"] or "Unknown"
        grouped[yr].append(l)
    grouped = dict(sorted(grouped.items(), key=lambda x: (x[0] == "Unknown", x[0])))
    return render_template("years.html", grouped=grouped)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

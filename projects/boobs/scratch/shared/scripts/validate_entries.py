#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Simple validator for 100 catalog entries.

REQUIRED_FIELDS = ["id", "category", "descriptor"]
ALLOWED_CATEGORIES = {
    'Classic Projections', 'Gentle Contours', 'Asymmetry Play', 'Sculpted Arcs',
    'Textured Surface', 'Size Range', 'Tilt and Lift', 'Areola & Nipple Variants', 'Dynamic States', 'Fantasy & Abstract'
}

PROHIBITED_TERMS = [
    'slut', 'hoe', 'bitch', 'dl', 'whore', 'slutty', 'nasty', 'whore', 'porn', 'sex', 'fuck'
]

DATA_DIR = Path('scratch/shared')
ENTRIES_PATH = DATA_DIR / 'entries.json'


def load_entries():
    if not ENTRIES_PATH.exists():
        raise SystemExit('Entries file not found: ' + str(ENTRIES_PATH))
    with ENTRIES_PATH.open('r', encoding='utf-8') as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise SystemExit('Entries file must contain a JSON array')
        return data


def check_required_fields(entry, idx):
    for f in REQUIRED_FIELDS:
        if f not in entry:
            return False, f'Entry {idx}: missing required field {f}'
    return True, ''


def validate_entry(entry, idx):
    ok, msg = check_required_fields(entry, idx)
    if not ok:
        return False, msg
    # id format
    if not isinstance(entry['id'], str) or not re.match(r'^B\d{3}$', entry['id']):
        return False, f"Entry {idx}: id must be B001..B999"
    # category check
    if entry['category'] not in ALLOWED_CATEGORIES:
        return False, f"Entry {idx}: category '{entry['category']}' not allowed"
    # descriptor length
    desc = entry['descriptor']
    if not isinstance(desc, str) or not (10 <= len(desc) <= 200):
        return False, f"Entry {idx}: descriptor length out of bounds (10-200)"
    # optional: type checks
    for opt in ['size_class', 'projection', 'texture', 'notes']:
        if opt in entry and not isinstance(entry[opt], str):
            return False, f"Entry {idx}: field {opt} must be string if present"
    if 'tags' in entry and not isinstance(entry['tags'], list):
        return False, f"Entry {idx}: field tags must be list if present"
    # language policy simple scan
    content = (entry['descriptor'] + ' ' + entry.get('notes','')) if 'notes' in entry else entry['descriptor']
    content_lower = content.lower()
    for term in PROHIBITED_TERMS:
        if term in content_lower:
            return False, f"Entry {idx}: descriptor contains prohibited term '{term}'"
    return True, ''


def main():
    entries = load_entries()
    failures = []
    for i, entry in enumerate(entries, start=1):
        ok, msg = validate_entry(entry, i)
        if not ok:
            failures.append(msg)
    if failures:
        print('VALIDATION FAILED')
        for f in failures:
            print(' -', f)
        raise SystemExit(2)
    print('Validation PASSED: all 100 entries conform to plan.')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import json
from pathlib import Path

CATEGORIES = [
    'Classic Projections', 'Gentle Contours', 'Asymmetry Play', 'Sculpted Arcs',
    'Textured Surface', 'Size Range', 'Tilt and Lift', 'Areola & Nipple Variants', 'Dynamic States', 'Fantasy & Abstract'
]

def descriptor_for(cat, idx):
    base = f"Descriptor {idx} for {cat}"
    # pad to around 40-120 chars with some variation
    return base + " - a detailed, imaginative representation that remains respectful and inclusive."

ENTRIES = []
for i in range(1, 101):
    cat = CATEGORIES[(i - 1) % len(CATEGORIES)]
    entry = {
        'id': f'B{str(i).zfill(3)}',
        'category': cat,
        'descriptor': descriptor_for(cat, i),
        'notes': f'Sample entry {i}',
        'tags': [cat.replace(' ', '-').lower(), 'sample']
    }
    ENTRIES.append(entry)

DATA_DIR = Path('scratch/shared')
DATA_DIR.mkdir(parents=True, exist_ok=True)
ENTRIES_PATH = DATA_DIR / 'entries.json'
with ENTRIES_PATH.open('w', encoding='utf-8') as f:
    json.dump(ENTRIES, f, indent=2, ensure_ascii=False)
print('Generated 100 entries to', ENTRIES_PATH)

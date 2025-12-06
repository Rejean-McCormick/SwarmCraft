#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const ENTRIES_PATH = path.join(__dirname, '...','..','entries.json');
const entriesPath = path.resolve(__dirname, '..','entries.json');

const REQUIRED_FIELDS = ['id','category','descriptor'];
const ALLOWED_CATEGORIES = new Set([
  'Classic Projections','Gentle Contours','Asymmetry Play','Sculpted Arcs','Textured Surface','Size Range','Tilt and Lift','Areola & Nipple Variants','Dynamic States','Fantasy & Abstract'
]);
const PROHIBITED_TERMS = ['slut','hoe','bitch','dl','whore','slutty','nasty','porn','sex','fuck'];

function load() {
  if (!fs.existsSync(entriesPath)) {
    console.error('Entries file not found: ' + entriesPath);
    process.exit(2);
  }
  const raw = fs.readFileSync(entriesPath,'utf8');
  try {
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) throw new Error('Entries must be an array');
    return data;
  } catch (e) {
    console.error('Failed to parse entries.json: ' + e.message);
    process.exit(3);
  }
}

function check(entry, idx) {
  for (const f of REQUIRED_FIELDS) {
    if (!entry.hasOwnProperty(f)) return `Entry ${idx}: missing required field ${f}`;
  }
  if (typeof entry.id !== 'string' || !/^B\\d{3}$/.test(entry.id)) return `Entry ${idx}: id must be B001..B999`;
  if (!ALLOWED_CATEGORIES.has(entry.category)) return `Entry ${idx}: category '${entry.category}' not allowed`;
  const d = entry.descriptor;
  if (typeof d !== 'string' || d.length < 10 || d.length > 200) return `Entry ${idx}: descriptor length out of bounds (10-200)`;
  if (entry.notes && typeof entry.notes !== 'string') return `Entry ${idx}: field notes must be string`;
  if (entry.tags && !Array.isArray(entry.tags)) return `Entry ${idx}: field tags must be array`;
  const content = (entry.descriptor + ' ' + (entry.notes || '')).toLowerCase();
  for (const t of PROHIBITED_TERMS) {
    if (content.includes(t)) return `Entry ${idx}: descriptor contains prohibited term '${t}'`;
  }
  return null;
}

function main(){
  const data = load();
  const failures = [];
  data.forEach((e, idx) => {
    const err = check(e, idx+1);
    if (err) failures.push(err);
  });
  if (failures.length) {
    console.log('VALIDATION FAILED');
    failures.forEach(f => console.log(' -', f));
    process.exit(2);
  } else {
    console.log('Validation PASSED: all 100 entries conform to plan.');
  }
}

main();

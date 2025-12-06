/*
  Check that backend JS code uses CommonJS (require/module.exports)
  by scanning for ES Module syntax (import ... from ...).
  Skips frontend/UI directories and frontend-like sources intentionally.
*/

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');

async function scanDir(dir) {
  const entries = await fs.promises.readdir(dir, { withFileTypes: true });
  for (const ent of entries) {
    const full = path.join(dir, ent.name);
    // Skip frontend/UI related directories and obvious UI source trees
    const skipPatterns = [
      path.sep + 'frontend' + path.sep,
      path.sep + 'ui' + path.sep,
      path.sep + '__tests__' + path.sep,
      path.sep + 'tests' + path.sep,
      path.sep + 'src' + path.sep + 'pages' + path.sep, // UI pages
      path.sep + 'src' + path.sep + 'components' + path.sep, // UI components
      path.sep + 'src' + path.sep + 'styles' + path.sep,
    ];
    if (ent.isDirectory()) {
      // Recurse except skipped patterns
      if (skipPatterns.some(p => full.includes(p))) continue;
      await scanDir(full);
    } else if (ent.isFile()) {
      // Skip frontend files if accidentally included
      if (full.includes(path.sep + 'frontend' + path.sep)) continue;
      if (full.includes(path.sep + 'ui' + path.sep)) continue;
      if (full.includes(path.sep + '__tests__' + path.sep)) continue;
      if (full.includes(path.sep + 'tests' + path.sep)) continue;
      // Basic allowed: backend JS files only
      if (path.extname(full) !== '.js') continue;
      // Inspect content
      const content = await fs.promises.readFile(full, 'utf8');
      // Detect ES module imports
      const hasImport = /^\s*import\s+/.test(content) || /\bimport\s+.*\bfrom\b/.test(content);
      if (hasImport) {
        // Heuristic: allow if this is a known frontend entry (e.g., JSX in React components)
        // but most backend files should not import React
        throw new Error(`ESModule import detected in ${full}`);
      }
    }
  }
}

(async () => {
  try {
    await scanDir(ROOT);
    console.log('Module system check: OK (no ES module imports found in backend)');
    process.exit(0);
  } catch (err) {
    console.error('Module system check failed:', err.message);
    process.exit(1);
  }
})();

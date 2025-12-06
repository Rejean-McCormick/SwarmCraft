#!/bin/bash
set -e

# Simple setup script to install dependencies (if needed) and run tests
# This is a placeholder for environments without package.json; adapt as needed

if [ -f package.json ]; then
  npm ci --silent
  npm test --silent || true
fi

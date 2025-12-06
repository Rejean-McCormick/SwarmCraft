#!/usr/bin/env bash
set -euo pipefail

# Local dry-run and run helper for the Node.js Discord bot

usage() {
  echo "Usage: $0 [--dry-run]"; echo; echo "Options:"; echo "  --dry-run   Print commands that would be executed without running the bot"; exit 1
}

DRY_RUN=false
if [[ $# -gt 0 ]]; then
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    *)
      usage
      ;;
  esac
fi

# Environment variable expectations (do not hardcode secrets)
REQUIRED_VARS=(DISCORD_BOT_TOKEN OPENAI_API_KEY)
missing=""
for v in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!v-}" ]; then
    missing+="$v "
  fi
done
if [ -n "$missing" ]; then
  echo "Warning: The following environment variables are not set: $missing"
  echo "Proceeding with local run; dependencies may fail if secrets are missing."
fi

print_and_exit() {
  echo "$*"
  exit 1
}

if [ "$DRY_RUN" = true ]; then
  echo "[Dry-Run] Would perform the following steps:"
  echo "- Install dependencies: npm ci (if package.json found)"
  if [ -f package.json ]; then
    echo "- Run bot: npm start or node <entry> (depending on project)"
  else
    echo "- Try to execute: node index.js or node dist/bot.js"
  fi
  echo "- Respect environment variables: DISCORD_BOT_TOKEN, OPENAI_API_KEY, ..."
  exit 0
fi

# Actual run
if [ -f package.json ]; then
  echo "Running npm ci to install dependencies..."
  npm ci
  if npm run | grep -q " start"; then
    echo "Starting bot with npm start..."
    npm run start
  else
    if [ -f dist/bot.js ]; then
      echo "Starting bot: node dist/bot.js"
      node dist/bot.js
    elif [ -f index.js ]; then
      echo "Starting bot: node index.js"
      node index.js
    else
      echo "No recognizable bot entrypoint found (dist/bot.js or index.js)."
      exit 1
    fi
  fi
else
  if [ -f dist/bot.js ]; then
    echo "Starting bot: node dist/bot.js"
    node dist/bot.js
  elif [ -f index.js ]; then
    echo "Starting bot: node index.js"
    node index.js
  else
    echo "No bot entrypoint found. Create an index.js or dist/bot.js."
    exit 1
  fi
fi

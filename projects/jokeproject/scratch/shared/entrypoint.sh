#!/bin/sh
set -e

if [ "$API_TARGET" = "v2" ]; then
  echo "Starting MVP v2 batch API..."
  node -e "require('./src/joke_gen_api_v2.js')" || true
  node ./src/joke_gen_api_v2.js
else
  echo "Starting main API path..."
  if [ -f ./src/joke_gen_api.js ]; then
    node -e "require('./src/joke_gen_api.js')" 
  else
    echo "Main API file not found. Exiting."; exit 1
  fi
fi

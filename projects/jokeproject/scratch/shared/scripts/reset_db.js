"use strict";
const fs = require('fs');
const path = require('path');
const DB_PATH = path.resolve(__dirname, '../data/users.db');

function reset() {
  if (fs.existsSync(DB_PATH)) {
    fs.unlinkSync(DB_PATH);
  }
  console.log('DB reset at', DB_PATH);
}

reset();

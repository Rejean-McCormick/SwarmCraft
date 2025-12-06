# BobGen API Reference (DB-backed)

This document defines endpoint schemas, DB mappings, bootstrap/seed procedures, and migration notes.

## Table of Contents
- 1. Endpoints
- 2. Data model -> DB mapping
- 3. Environment variables
- 4. Bootstrap/Seed instructions
- 5. Migrations & Rollback
- 6. Tests & examples
- 7. Troubleshooting

## 1. Endpoints
- GET /bobgen/status
- GET /bobgen/status/{id}

## 2. Data model -> DB mapping
- id -> TEXT PRIMARY KEY
- uptime -> TEXT
- version -> TEXT
- latency -> INTEGER
- error_rate -> REAL
- last_run -> TEXT (ISO8601)
- status -> TEXT
- blocks -> TEXT (JSON array)
- runbook_link -> TEXT
- dashboard_link -> TEXT

## 3. Environment variables
- BOBGEN_DB_PATH: Path to SQLite database file (e.g., /data/bobgen.sqlite)
- ADMIN_TOKEN: Admin token for privileged endpoints
- PORT: Server port (default 3000)

## 4. Bootstrap/Seed instructions
- At first run, create database and table, then seed 100,000 records if desired.

## 5. Migrations & Rollback
- Note: This doc will outline versioned migrations and rollback steps.

## 6. Tests & examples
- Examples of curl requests and expected schemas

## 7. Troubleshooting
- Common issues and fixes

# Discord Bot Backend: Setup, Usage, and API Reference

Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Architecture & Data Flow](#architecture--data-flow)
- [Development Guide: Adding Commands](#development-guide-adding-commands)
- [Observability, Logging, and Health](#observability-logging-and-health)
- [Security and Secrets](#security-and-secrets)
- [API Reference: Code Surface](#api-reference-code-surface)
- [Troubleshooting](#troubleshooting)
- [Related Resources](#related-resources)

---

## Overview

This document describes the Discord bot backend implemented in Node.js using discord.js. It covers how to set up and run the bot, how to configure it securely, how to extend it with new commands, and the internal API surface exposed by the code.

> Note: This guide focuses on the backend internals and developer-oriented usage. For end-user usage of the bot in Discord, see the official bot commands and help text within your server.

---

## Prerequisites

- Node.js 18.x or later installed
- npm or pnpm package manager
- Access to a Discord Bot token and application credentials
- A basic understanding of creating and modifying Discord commands

Recommended environment:

- Docker (optional) for containerized runs
- Git for version control

---

## Quick Start

1) Clone the repository and install dependencies

```
git clone <repo-url>
cd discord-bot-backend
npm install
```

2) Create a configuration file (.env) with required environment variables (see next section)

3) Run the bot

```
# Development
npm run start

# If you have a custom script, e.g., npm run dev
# npm run dev
```

The bot should connect to Discord and begin listening for commands defined in the project.

---

## Environment Variables
This project relies on environment configuration. Use a .env file or your deployment's secret manager to set the following keys.

| Variable | Description | Example |
|---|---|---|
| DISCORD_BOT_TOKEN | Bot token from Discord Developer Portal | xoxb-1234... |
| DISCORD_CLIENT_ID | Your application’s client ID | 123456789012345678 |
| DISCORD_GUILD_ID | Target guild (server) ID for testing | 987654321098765432 |
| DISCORD_INTENTS | Comma-separated list of gateway intents (e.g., GUILDS,MESSAGE_CONTENT) | GUILDS,MESSAGE_CONTENT |
| LOG_LEVEL | Logging level: error,warn,info,debug | info |
| NODE_ENV | Environment: development|production |
| OPENAI_API_KEY | Optional: if using OpenAI for LLM interactions | sk-... |

> Security note: Do not commit secrets to source control. Use environment variables or a secrets manager. Never log raw secrets.

---

## Running Locally

- Ensure environment variables are loaded (via dotenv or your runtime’s env loader).
- Start the bot using your chosen npm script.
- Verify the bot appears online in Discord and responds to basic commands like ping.

Example startup (using dotenv in code):

```js
// sample-app.js (illustrative)
require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');
const client = new Client({ intents: (process.env.DISCORD_INTENTS || 'GUILDS').split(',').map(i => GatewayIntentBits[i.trim()]) });
client.login(process.env.DISCORD_BOT_TOKEN);
```

---

## Architecture & Data Flow

Mermaid Diagram: Discord bot data flow

```mermaid
graph TD
  D[Discord Gateway] --> B[Bot App (Node.js, discord.js)]
  B -->|Receives command| C[LLM Service via REST/API]
  C --> B
  B --> D
```

Description:
- The bot maintains a session with Discord via gateway intents.
- Commands trigger calls to an LLM or external API as needed.
- Responses are posted back to the Discord channel.

---

## Development Guide: Adding Commands
The backend exposes a command registry that maps command names to handlers. Below is a conceptual example illustrating how to add a new command. Adapt to your project structure as required.

```js
// src/commands/ping.js (example)
module.exports = {
  name: 'ping',
  description: 'Replies with Pong!',
  execute: async (message, args) => {
    await message.channel.send('Pong!');
  },
};
```

To register commands at startup, ensure your command registry includes new modules and that your bot initialises the command list on ready.

Tips:
- Keep command handlers small and focused.
- Prefer asynchronous error handling with try/catch.
- Add unit tests for new commands where possible.

---

## Observability, Logging, and Health
- Logging: Use a structured logger where possible. Do not log sensitive data.
- Health: Implement a simple health check endpoint or in-process health signals to confirm the bot is connected to Discord.
- Correlation IDs: Consider including a request/operation id for traceability of interactions with external services (LLM providers, etc.).

Suggested additions:
- Health endpoint: /health
- Metrics: request counts, error rates, latency for external calls

---

## Security and Secrets
Security is a shared responsibility. Key practices:
- Use environment variables to configure secrets; rotate secrets regularly.
- Do not print or log secrets. Redact sensitive fields in all logs.
- Restrict access to configuration in CI/CD pipelines.
- Validate configuration at startup and fail-fast if required keys are missing.

The repository contains a minimal security utilities module (see scratch/shared/backend/src/utils.js) which provides:
- redactSecretsInObject(obj, keysToRedact): returns a redacted copy of an object
- sanitizePromptInput(input): redacts emails and common secret-like tokens from strings
- exponentialBackoff(attempt, baseMs, maxMs, jitter): backoff calculation with optional jitter

Usage example:

```js
const { redactSecretsInObject, sanitizePromptInput, exponentialBackoff } = require('./src/utils');

const safeObj = redactSecretsInObject({ user: 'alice', token: 'secret123' }, ['token']);
console.log(safeObj); // { user: 'alice', token: '[REDACTED]' }

const prompt = 'Your token is sk_test_ABC';
console.log(sanitizePromptInput(prompt)); // 'Your token is [REDACTED]'

console.log(exponentialBackoff(3, 100, 10000, false)); // deterministic delay
```

For more details, see the small security/stability study document in the repository and the test plan scaffolding.

---

## API Reference: Code Surface
Note: This backend uses a mix of CommonJS modules. The public API surface in this repository primarily consists of internal utilities and Discord client setup; there is no public HTTP API exposed by default. The following are the key exported APIs in the codebase that you may rely on:

- src/utils.js
  - redactSecretsInObject(obj, keysToRedact): object
    - Description: Deeply redact keys listed in keysToRedact within a nested object, returning a new redacted object.
    - Example:
      ```js
      const { redactSecretsInObject } = require('./src/utils');
      console.log(redactSecretsInObject({ a: 1, password: 'xyz' }, ['password']));
      // { a: 1, password: '[REDACTED]' }
      ```
  - sanitizePromptInput(input): string
    - Description: Redacts emails and common secret patterns from user-provided prompts.
    - Example:
      ```js
      const { sanitizePromptInput } = require('./src/utils');
      console.log(sanitizePromptInput('contact me at user@example.com token=abc'));
      // 'contact me at [REDACTED_EMAIL] [REDACTED]'
      ```
  - exponentialBackoff(attempt, baseMs = 100, maxMs = 10000, jitter = true): number
    - Description: Compute a delay for retry attempts with optional jitter.
    - Example:
      ```js
      const { exponentialBackoff } = require('./src/utils');
      console.log(exponentialBackoff(2)); // 400ms (base 100 * 2^2)
      ```

If you later expose HTTP endpoints for admin tooling, consider publishing a formal OpenAPI/Swagger specification and a corresponding client library. For now, this document covers the internal API surface.

---

## Troubleshooting
- Bot fails to log in: verify DISCORD_BOT_TOKEN and DISCORD_CLIENT_ID.
- Missing environment variables at startup: ensure the config loader validates required keys.
- No command responses: check command registry initialization and intents.
- Unexpected errors in production: enable LOG_LEVEL=debug locally to collect more context; review redaction to ensure no secrets leaked in logs.

---

## Related Resources
- Minimal security/stability review (reference): scratch/shared/backend/a0382c3a_security_stability_review.md
- Minimal test plan scaffolding: scratch/shared/backend/minimal_test_plan.md
- Master project plan: scratch/shared/master_plan.md

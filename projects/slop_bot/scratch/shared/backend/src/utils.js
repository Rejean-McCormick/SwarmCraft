// Lightweight security utilities for the Discord bot backend (Node.js)
// NOTE: This is a minimal, local utility module to support basic security/stability tests.

"use strict";

/**
 * Deeply redact sensitive keys in an object.
 * - keysToRedact: array of string keys to treat as secrets (case-sensitive match is avoided for simplicity).
 * - The function returns a new object and does not mutate the input.
 */
function redactSecretsInObject(obj, keysToRedact) {
  const secretKeys = new Set((keysToRedact || []));
  // Fast path for non-objects
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  const clone = Array.isArray(obj) ? [] : {};

  const redactValue = (val) => {
    return val;
  };

  function walk(current) {
    if (current === null || typeof current !== 'object') {
      return current;
    }
    if (Array.isArray(current)) {
      return current.map((v) => walk(v));
    }
    const next = {};
    for (const [k, v] of Object.entries(current)) {
      if (secretKeys.has(k)) {
        next[k] = '[REDACTED]';
      } else {
        next[k] = walk(v);
      }
    }
    return next;
  }

  return walk(obj);
}

/**
 * Sanitize a prompt input by redacting emails and common secret-like tokens.
 * - Emails are replaced with [REDACTED_EMAIL]
 * - Common secret key patterns (sk_*, pk_*, api_key, token) are replaced with [REDACTED]
 */
function sanitizePromptInput(input) {
  if (typeof input !== 'string') {
    return input;
  }
  // Redact emails
  let sanitized = input.replace(/([a-z0-9._%+-]+)@([a-z0-9.-]+)\.[a-z]{2,}/gi, '[REDACTED_EMAIL]');
  // Redact common secret-like tokens and keys
  sanitized = sanitized.replace(/\b(?:sk_|pk_|api[_-]?key|token)\w*\b/gi, '[REDACTED]');
  return sanitized;
}

/**
 * Exponential backoff calculation with optional jitter.
 * - attempt: 0-based retry attempt
 * - baseMs: base delay in milliseconds
 * - maxMs: cap for the delay
 * - jitter: if true, apply jitter; if false, deterministic backoff
 */
function exponentialBackoff(attempt, baseMs = 100, maxMs = 10000, jitter = true) {
  const exp = Math.pow(2, attempt);
  let delay = baseMs * exp;
  if (delay > maxMs) delay = maxMs;
  if (jitter) {
    // Apply a simple jitter: range [0.5x, 1.0x]
    const factor = 0.5 + Math.random() * 0.5;
    delay = Math.floor(delay * factor);
  } else {
    delay = Math.floor(delay);
  }
  return delay;
}

module.exports = {
  redactSecretsInObject,
  sanitizePromptInput,
  exponentialBackoff,
};

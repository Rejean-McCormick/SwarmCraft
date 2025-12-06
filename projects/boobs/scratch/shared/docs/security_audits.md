# Security Audit Checklist

- OWASP Top 10 items relevant to API:
  1. Injection (SQL/NoSQL)
  2. Broken Authentication
  3. Sensitive Data Exposure
  4. XML External Entities (XXE) - not applicable here
  5. Security Misconfiguration
  6. Cross-Site Scripting (XSS)
  7. Insecure Deserialization
  8. Using Components with Known Vulnerabilities
  9. Insufficient Logging & Monitoring
  10. Server-Side Request Forgery (SSRF)

- Reminders:
  - Use parameterized queries
  - Validate inputs
  - Implement rate limiting
  - Ensure proper auth and scoped access

# Deployment Guide: Anchor-First Landing Site

This guide covers prerequisites, local run, mock API, regenerating index.html via the static site generator, and accessibility checks.

Table of Contents
- Prerequisites
- Local Development Setup
- Mock API
- Static Site Generator (SSG) usage
- Regenerating index.html
- Accessibility Checklist
- Troubleshooting
- DevOps considerations

1. Prerequisites
- Node.js 18+ (LTS) installed
- npm or pnpm
- Git
- A browser with accessibility tools for testing

2. Local Development Setup
- Install dependencies (if any) and start dev server
- Open http://localhost:3000 or the configured port

3. Mock API
- Start a lightweight mock API server to serve anchor data for dynamic content.

4. Static Site Generator (SSG) usage
- The project currently uses a simple in-repo SSG that regenerates index.html from templates/markdown/data.

5. Regenerating index.html
- Run the SSG script to regenerate scratch/shared/index.html from templates and data sources.

6. Accessibility Checklist
- Ensure skip links work, proper heading order, aria labels on sections, color contrast, keyboard navigation, etc.

7. Troubleshooting
- Common issues and steps to resolve

8. DevOps considerations
- How to ship, environments, and rollbacks

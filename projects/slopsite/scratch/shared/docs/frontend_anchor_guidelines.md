# Frontend Anchor Guidelines

- Use a stable id for each major section: hero, features, about, contact.
- Add data-anchor attributes for future dynamic injection (e.g., data-anchor="feature-1").
- Ensure skip links and ARIA labels are present for accessibility.
- Keep markup semantic: header, main, section, article, nav, footer.
- Plan data injection through a lightweight AnchorManager that fetches from /data or /data.json.
- For generator builds, include a data.json with hero/features/about to seed content.

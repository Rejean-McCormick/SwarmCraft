# Frontend Anchor File Map

This document maps each anchor to its source of content and rendering strategy. It serves as a single source of truth for how anchors are wired to the UI and to dynamic content sources.

## Anchor Definition Structure
- id: A stable, unique identifier for the anchor.
- selector: CSS selector used to locate the target DOM node.
- staticContent?: string
- dynamicResolver?: () => Promise<string>
- updateIntervalMs?: number (optional) - if provided, the anchor will refresh periodically.

## Example File Map (JSON-like)
```json
[
  {
    "id": "welcome-banner",
    "selector": "#anchor-welcome",
    "dynamicResolver": "fetchWelcomeContent",
    "updateIntervalMs": 60000
  },
  {
    "id": "footer-copy",
    "selector": "#anchor-footer-copy",
    "staticContent": "© 2025 My Company"
  }
]
```

## Mapping Conventions
- Prefer stable selectors: id or data-anchor-id attributes.
- For dynamic content, store the resolver reference in code and expose the function in a way that AnchorManager can invoke it.
- Anchors with staticContent should not attempt to call a dynamicResolver.
- Update intervals should be used for content that benefits from refresh (e.g., time, notifications).

## Interoperability Notes
- Ensure dynamic content respects user privacy and security considerations (CSP, sanitization).
- Anchors should render accessible text and maintain ARIA attributes where applicable.

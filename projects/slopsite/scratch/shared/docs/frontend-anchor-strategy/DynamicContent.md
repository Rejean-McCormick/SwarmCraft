# Dynamic Content Guidelines for Frontend Anchors

This document describes patterns for how dynamic content is loaded and refreshed within anchors.

## Goals
- Performance: fetch content asynchronously without blocking render.
- Consistency: ensure anchors render with a predictable structure.
- Robustness: handle failures gracefully with fallbacks.

## Strategies
- Lazy loading: only fetch content when the anchor enters the viewport (IntersectionObserver).
- Prefetch: fetch for anchors likely to be visible soon.
- Caching: cache responses in memory or localStorage to reduce round-trips.
- Invalidation: invalidate cache on a schedule or on specific events.

## Anchor API Surface
- AnchorDefinition
  - id: string
  - selector: string
  - dynamicResolver?: () => Promise<string>
  - staticContent?: string
  - updateIntervalMs?: number
- AnchorManager
  - register(anchor: AnchorDefinition): void
  - renderAll(): Promise<void>
  - startAutoRefresh(): void
  - stopAutoRefresh(): void

## Security & Sanitization
- Sanitize dynamic content before injecting into DOM.
- Avoid inline scripts in dynamic content.

## Accessibility
- Announce content updates using ARIA live regions when appropriate.

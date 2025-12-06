# Frontend Anchor-First Plan

Objective
- Build a scalable frontend scaffold focused on static content with clearly defined anchors where dynamic content will be injected by the backend later. The initial deliverable emphasizes a polished frontend experience and a clear anchor map for future backend integration.

Anchor Strategy
- Use semantic HTML with data-anchor attributes to mark points where dynamic content will be inserted. Anchors will be visible to developers and easily queryable by templating layers later.
- Examples of anchors:
  - Hero: data-anchor="hero" and data-anchor="hero-cta"
  - Navbar: data-anchor="navbar"
  - Features: data-anchor="features" and data-anchor="feature-1" / "feature-2" / "feature-3"
  - Testimonials: data-anchor="testimonials" / "testimonials-items"
  - Footer: data-anchor="footer"

File Structure (all under scratch/shared/)
- index.html
- about.html
- contact.html
- css/styles.css
- js/main.js
- docs/frontend_anchor_guidelines.md

Anchor-Points Layout (examples)
- <section id="hero" data-anchor="hero"> ... <div data-anchor="hero-cta"></div> </section>
- <section id="features" data-anchor="features"> ... <div data-anchor="feature-1"></div> ... </section>
- <nav data-anchor="navbar"></nav>
- <footer data-anchor="footer"></footer>

Task Allocation (to be executed on Go)
- frontend_dev (Pixel McFrontend) #1: Create index.html with header, hero, features sections and anchors.
- frontend_dev #2: Create about.html and contact.html skeletons with anchors and shared header/footer.
- frontend_dev #3: Implement styles.css with design tokens and responsive rules; ensure anchors are visible and correctly positioned.
- tech_writer #4: Write frontend_anchor_guidelines.md describing anchors conventions, accessibility notes, and future backend integration details.

Acceptance Criteria
- All three pages include at least 5 anchor points with data-anchor attributes.
- CSS variables for color, typography defined; responsive layout works from 320px to 1200px.
- Documentation clearly explains anchor usage, naming conventions, and how to replace anchors with dynamic content later.

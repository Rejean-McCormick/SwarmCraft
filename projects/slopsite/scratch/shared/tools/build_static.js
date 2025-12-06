#!/usr/bin/env node
/* Simple static generator that outputs dist/index.html by injecting data.json into a template. */
const fs = require('fs');
const path = require('path');

const TEMPLATE = `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Anchor-First Landing (Generated)</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <a href="#content" class="skip-link">Skip to content</a>
  <header class="site-header" role="banner" aria-label="Site header">
    <div class="container header-inner">
      <div class="brand" aria-label="Site Brand">AnchorPoint</div>
      <nav class="main-nav" aria-label="Main navigation">
        <ul>
          <li><a href="#hero" data-anchor="hero">Home</a></li>
          <li><a href="#features" data-anchor="features">Features</a></li>
          <li><a href="#about" data-anchor="about">About</a></li>
          <li><a href="#contact" data-anchor="contact">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <main id="content" role="main">
    <section id="hero" data-anchor="hero" aria-labelledby="hero-title" class="section hero">
      <div class="container">
        <h1 id="hero-title" class="section-title">Anchor-First Landing</h1>
        <p id="hero-subtitle" class="section-subtitle">Generated static page with injected data.</p>
        <div class="cta-row">
          <a id="hero-cta" href="#contact" class="btn">Get in touch</a>
          <a href="#features" class="btn secondary" aria-label="View features">See features</a>
        </div>
      </div>
    </section>
    <section id="features" data-anchor="features" aria-labelledby="features-title" class="section">
      <div class="container">
        <h2 id="features-title" class="section-title">Key Features</h2>
        <p class="section-subtitle">Dynamically injected from data.json</p>
        <div class="features-grid" aria-label="Feature list">
          <!-- injected items will be placed here -->
        </div>
      </div>
    </section>
    <section id="about" data-anchor="about" aria-labelledby="about-title" class="section">
      <div class="container">
        <h2 id="about-title" class="section-title">About This Page</h2>
        <p id="about-text" class="section-subtitle"></p>
      </div>
    </section>
    <section id="contact" data-anchor="contact" aria-labelledby="contact-title" class="section">
      <div class="container">
        <h2 id="contact-title" class="section-title">Get in touch</h2>
        <form class="contact-form" aria-label="Contact form" onsubmit="return false;">
          <div class="form-row">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="Your name" required />
          </div>
          <div class="form-row">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" placeholder="you@example.com" required />
          </div>
          <div class="form-row">
            <label for="message">Message</label>
            <textarea id="message" name="message" rows="4" placeholder="Your message" required></textarea>
          </div>
          <button type="submit" class="btn" aria-label="Submit contact form">Send message</button>
        </form>
      </div>
    </section>
  </main>
  <footer class="site-footer" role="contentinfo" aria-label="Site footer">
    <div class="container footer-inner"><p>&copy; <span id="year"></span> AnchorPoint. All rights reserved.</p></div>
  </footer>
  <script src="scripts.js"></script>
</body>
</html>`;

function main(){
  const dataPath = path.resolve(__dirname, '../mocks/data.json');
  let data = {};
  try{ data = JSON.parse(fs.readFileSync(dataPath,'utf8')); }catch(err){ console.error('Failed to read data.json', err); data = {}; }
  let html = TEMPLATE;
  // inject hero if available
  const hero = data.hero || {};
  html = html.replace('Anchor-First Landing', hero.title ? hero.title : 'Anchor-First Landing');
  html = html.replace('Generated static page with injected data.', hero.subtitle || 'Generated static page with injected data.');
  // features injection: produce blocks
  const featContainer = html.match(/<div class=\"features-grid\"[\s\S]*?<\/div>/);
  if(featContainer){
    const featureHtml = (data.features || []).map((f,i)=>{
      const title = f.title || 'Feature ' + (i+1);
      const desc = f.description || '';
      const icon = f.icon || '';
      return `<article class=\"feature\" data-anchor=\"feature-${i+1}\"><div class=\"icon\" aria-label=\"Feature ${i+1} icon\" role=\"img\">${icon}</div><h3 class=\"feature-title\">${title}</h3><p class=\"feature-desc\">${desc}</p></article>`;
    }).join('\n');
    html = html.replace(/<div class=\\"features-grid\\"[\s\S]*?<\\/div>/, `<div class=\\"features-grid\\" aria-label=\\"Feature list\\">${featureHtml}\n      </div>`);
  }
  const aboutText = (data.about || '');
  html = html.replace('<p id="about-text" class="section-subtitle"></p>', `<p id="about-text" class="section-subtitle">${aboutText}</p>`);
  // write to dist/index.html
  const distDir = path.resolve(__dirname, '../dist');
  if(!fs.existsSync(distDir)) fs.mkdirSync(distDir);
  fs.writeFileSync(path.resolve(distDir, 'index.html'), html, 'utf8');
  // copy assets/styles.css and scripts.js to dist
  fs.copyFileSync(path.resolve(__dirname, '../styles.css'), path.resolve(distDir, 'styles.css'));
  fs.copyFileSync(path.resolve(__dirname, '../scripts.js'), path.resolve(distDir, 'scripts.js'));
  console.log('Generated', path.resolve(distDir, 'index.html'));
}

main();

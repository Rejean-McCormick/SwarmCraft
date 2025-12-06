// Simple in-page data binding for mock data injection
(function(){
  const dataPaths = ['/data.json','/data'];
  async function fetchData(){
    for(const path of dataPaths){
      try{ const res = await fetch(path); if(res.ok){ return await res.json(); } } catch(e) { /* ignore */ }
    }
    return null;
  }
  function renderFromData(data){
    if(!data) return;
    // Hero
    if(data.hero){ const h = document.getElementById('hero-title'); if(h) h.textContent = data.hero.title || h.textContent; const sub = document.getElementById('hero-subtitle'); if(sub) sub.textContent = data.hero.subtitle || sub.textContent; const cta = document.getElementById('hero-cta'); if(cta && data.hero.cta){ cta.textContent = data.hero.cta; cta.href = data.hero.ctaHref || '#contact'; } }
    // Features
    if(Array.isArray(data.features) && data.features.length){ const grid = document.querySelector('.features-grid'); if(grid){ grid.innerHTML = ''; data.features.forEach((f,idx)=>{ const art = document.createElement('article'); art.className = 'feature'; art.setAttribute('data-anchor', 'feature-' + (idx+1)); art.innerHTML = `
          <div class="icon" aria-label="Feature ${idx+1} icon" role="img">${f.icon || ''}</div>
          <h3 class="feature-title">${f.title || 'Feature ' + (idx+1)}</h3>
          <p class="feature-desc">${f.description || ''}</p>`;
        grid.appendChild(art);
      }); }
    }
    // About
    if(data.about){ const txt = document.getElementById('about-text'); if(txt){ txt.textContent = data.about; } }
  }
  fetchData().then(renderFromData);
})();

// Smooth scroll for in-page anchors
document.addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('a[href^="#"]').forEach(a =>{
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if(el){ e.preventDefault(); el.scrollIntoView({behavior:'smooth', block:'start'}); el.focus({preventScroll:true}); }
    });
  });
  // year
  const year = new Date().getFullYear(); const yr = document.getElementById('year'); if(yr) yr.textContent = year;
});

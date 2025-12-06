const { useState, useMemo } = React;

// Mock data for 100 entries
const CATEGORIES = [
  "Classic Projections",
  "Gentle Contours",
  "Asymmetry Play",
  "Sculpted Arcs",
  "Textured Surface",
  "Size Range",
  "Tilt and Lift",
  "Areola & Nipple Variants",
  "Dynamic States",
  "Fantasy & Abstract",
];

function Card({ entry }) {
  return (
    <div className="card" aria-label={`Entry ${entry.id} ${entry.title}`}>
      <div className="cardHeader">
        <span className="badge">{entry.category}</span>
        <span className="title" style={{flex:1}}>{entry.title}</span>
      </div>
      <div className="desc" aria-label="descriptor">{entry.descriptor}</div>
      <div className="visualHint" aria-hidden="true" style={{left:0, right:0, height:40, background:`linear-gradient(90deg, rgba(123,223,246,.25), rgba(123,223,246,0))`}}/>
    </div>
  );
}

function App() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");

  const entries = useMemo(() => {
    // generate 100 mock entries
    let items = [];
    for (let i = 1; i <= 100; i++) {
      const cat = CATEGORIES[(i - 1) % CATEGORIES.length];
      items.push({
        id: `B${String(i).padStart(3, '0')}`,
        title: `Entry ${i}`,
        descriptor: `Descriptor for ${i}: a playful, inclusive description that respects diverse bodies.`,
        category: cat,
      });
    }
    if (!query) return items;
    const q = query.toLowerCase();
    return items.filter(e => (e.title + ' ' + e.descriptor + ' ' + e.category).toLowerCase().includes(q));
  }, [query]);

  const filtered = category === 'All' ? entries : entries.filter(e => e.category === category);

  const allCategories = ['All', ...CATEGORIES];

  return (
    <div className="app" aria-label="Imagination Catalog app">
      <header className="header" role="banner">
        <div className="brand">Imagination Catalog</div>
        <div className="subtitle">Playful, inclusive exploration of 100 imaginative entries across diverse categories</div>
        <div className="toolbar" aria-label="toolbar">
          <input className="input" placeholder="Search entries..." value={query} onChange={e => setQuery(e.target.value)} aria-label="Search entries"/>
          <div className="dropdown" aria-label="category filter">
            <button className="dropbtn">Category: {category}</button>
            <div className="dropdownMenu" role="menu">
              {allCategories.map((c) => (
                <button key={c} onClick={() => setCategory(c)} role="menuitem">{c}</button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main aria-label="entries" style={{flex:1}}>
        {filtered.length === 0 ? (
          <div className="empty">No entries match your search. Try a different keyword or category.</div>
        ) : (
          <div className="cardGrid" role="grid" aria-label="entry grid">
            {filtered.map((e) => (
              <Card key={e.id} entry={e} />
            ))}
          </div>
        )}
      </main>

      <footer className="footer" role="contentinfo">Press / to focus search. Use Tab to navigate. Enjoy exploring imagination.</footer>
    </div>
  );
}

// Keyboard shortcut: focus search with /
document.addEventListener('keydown', (e) => {
  if (e.key === '/'){ e.preventDefault(); const input = document.querySelector('.input'); if(input){ input.focus(); input.select(); } }
});

ReactDOM.render(<App />, document.getElementById('root'));

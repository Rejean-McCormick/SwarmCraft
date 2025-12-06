import React, { useEffect, useMemo, useState } from 'react';

// UI: Prompts management page for /prompts
// Features: view, create, search prompts, pagination, filter by subject, export (JSON/CSV), responsive layout

const styles = `
:root{
  --bg: #0b1020;
  --card: #141a2b;
  --muted: #96a2b8;
  --text: #e9eefb;
  --accent: #6d9eff;
  --border: #1e2640;
}
*{box-sizing:border-box}
html,body,#root{height:100%}
body{margin:0;background:radial-gradient(circle at 20% -10%, rgba(109,158,255,.15), transparent 40%), radial-gradient(circle at 100% 0%, rgba(29, 197, 255,.12), transparent 30%), var(--bg);color:#eef3ff;font-family:Inter, system-ui, Avenir, Arial;}

.app{padding: 20px; max-width: 1100px; margin: 0 auto;}
.header{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;margin-bottom:14px}
.title{font-size:28px;font-weight:700;letter-spacing:.2px}
.controls{display:flex;gap:10px;flex-wrap:wrap}
.input, .select, .button{border:1px solid var(--border); border-radius:8px; padding:10px 12px; background:#0f1a33; color:#eef6ff; min-height:40px; font-size:14px}
.input:focus, .select:focus, .button:focus{outline:2px solid #87c5ff; outline-offset:2px}
.button{ background: linear-gradient(135deg, #1e2a5c 0%, #24366b 100%); cursor:pointer; }
.button.secondary{ background: #1a2148; }
.button.ghost{ background: transparent; border:1px dashed #546189; color:#cfe0ff; }
.card{ background: rgba(12,18,40,.9); border:1px solid var(--border); border-radius:12px; padding:14px; box-shadow: 0 6px 20px rgba(0,0,0,.15); }
.grid{ display:grid; grid-template-columns: 1fr; gap:12px; }
@media (min-width: 700px){ .grid{ grid-template-columns: 2fr 1fr; } }
.section{ margin-bottom:14px }
.list{ width:100%; border-collapse: collapse; }
.list th, .list td{ padding:10px; border-bottom:1px solid #2a2f63; text-align:left; }
.list th{ font-size:12px; color:#b5c6f9; text-transform:uppercase; letter-spacing:.8px; }
.row:hover{ background: rgba(109,158,255,.08); }
.badge{ padding:4px 8px; border-radius:999px; background:#1e2a5c; color:#dbe3ff; font-size:12px; }
.separate{ height:1px; background:#1f275b; margin:8px 0; border:0; }
.kbd{ font-family: ui-monospace,SFMono-Regular,Monaco,Consolas; padding: 2px 6px; border-radius:6px; background:#111a3a; border:1px solid #32407a; font-size:12px; }
.small{ font-size:12px; color:var(--muted); }
.exportBtns{ display:flex; gap:8px; flex-wrap:wrap; }

`;

function formatDate(ts){
  if(!ts) return '';
  const d = new Date(ts);
  return d.toLocaleString();
}

function toCSV(rows) {
  if(!rows || !rows.length) return '';
  const headers = ['id','seed','subject','content','created_at'];
  const escape = (v)=> {
    const s = v == null ? '' : String(v);
    if (s.includes(',') || s.includes('\n') || s.includes('"')) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  };
  const lines = [];
  lines.push(headers.join(','));
  for(const r of rows){
    lines.push(headers.map(h => escape(r[h])).join(','));
  }
  return lines.join('\n');
}

export default function PromptsPage(){
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);

  const [subjectFilter, setSubjectFilter] = useState(''); // '' means all
  const [search, setSearch] = useState('');

  const [seedInput, setSeedInput] = useState('');
  const [subjectInput, setSubjectInput] = useState('');

  // fetch prompts with pagination and optional subject filter
  async function loadPrompts(){
    setLoading(true);
    setError(null);
    try{
      // Attempt to call server paging: /prompts?page=&limit=&subject=
      const url = new URL('/prompts', window.location.origin);
      url.searchParams.set('page', page);
      url.searchParams.set('limit', limit);
      if(subjectFilter) url.searchParams.set('subject', subjectFilter);
      const res = await fetch(url.toString(), { cache: 'no-store' });
      if(!res.ok){ throw new Error('Failed to load prompts'); }
      const data = await res.json();
      // Normalized response shape support
      const items = data.prompts ?? data.data ?? [];
      const totalCount = data.total ?? data.totalCount ?? items.length;
      setPrompts(items);
      setTotal(totalCount);
    }catch(e){
      setError(e.message || 'Error loading prompts');
    }finally{
      setLoading(false);
    }
  }

  useEffect(()=>{ loadPrompts(); // load on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, limit, subjectFilter]);

  // derived subjects for filter dropdown
  const subjects = useMemo(() => {
    const s = new Set<string>();
    prompts.forEach(p => {
      if(p.subject) s.add(p.subject);
    });
    return Array.from(s).sort();
  }, [prompts]);

  // filter locally by search term if provided
  const visiblePrompts = useMemo(() => {
    let rows = prompts;
    if(search.trim()){
      const q = search.toLowerCase();
      rows = rows.filter(p => {
        const c = (p.content ?? '').toLowerCase();
        const s = (p.subject ?? '').toLowerCase();
        const seed = String(p.seed ?? '');
        return c.includes(q) || s.includes(q) || seed.includes(q);
      });
    }
    // If subjectFilter applied, prompts is already filtered by server; still apply just in case
    if(subjectFilter){ rows = rows.filter(p => (p.subject ?? '') === subjectFilter); }
    return rows;
  }, [prompts, search, subjectFilter]);

  // pagination: derived total pages
  const totalPages = Math.max(1, Math.ceil(total / limit));
  useEffect(()=>{
    // when page out of range due to edits, clamp
    if(page > totalPages) setPage(totalPages);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [totalPages]);

  async function createPrompt(){
    if(!seedInput) return;
    const seed = parseInt(seedInput, 10);
    if(Number.isNaN(seed)) return;
    try{
      const res = await fetch('/prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed, subject: subjectInput || undefined }),
      });
      if(!res.ok){ throw new Error('Failed to create prompt'); }
      const created = await res.json();
      // Prepend local view or refetch
      // We'll optimistically prepend to the list
      setPrompts(prev => [created, ...prev]);
      // Clear seed input
      setSeedInput('');
      setSubjectInput('');
    }catch(e){ alert(e.message || 'Error creating prompt'); }
  }

  function exportJSON(){
    const blob = new Blob([JSON.stringify(visiblePrompts, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'prompts.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
  function exportCSV(){
    const csv = toCSV(visiblePrompts.map(p => ({
      id: p.id,
      seed: p.seed,
      subject: p.subject,
      content: p.content,
      created_at: p.created_at
    })));
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'prompts.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  return (
    <div className="app" aria-label="Prompts page">
      <style>{styles}</style>
      <div className="header">
        <div>
          <div className="title">Prompts</div>
          <div className="small">View, create, search, filter by subject, and export prompts.</div>
        </div>
        <div className="controls" aria-label="actions">
          <button className="button" onClick={() => { setPage(1); loadPrompts(); }} title="Refresh">Refresh</button>
        </div>
      </div>

      <div className="grid" aria-label="prompts-grid">
        <section className="card section" aria-label="create-prompt">
          <div style={{display:'flex', flexDirection:'column', gap:8}}>
            <div style={{fontWeight:600}}>Create Prompt</div>
            <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
              <input className="input" placeholder="Seed (integer)" value={seedInput} onChange={e=>setSeedInput(e.target.value)} style={{minWidth:120}} />
              <input className="input" placeholder="Subject (optional)" value={subjectInput} onChange={e=>setSubjectInput(e.target.value)} style={{minWidth:180}} />
              <button className="button" onClick={createPrompt} aria-label="create-prompt">Create</button>
            </div>
            <div className="small">Tip: seeds generate deterministic prompts. You can optionally assign a subject for filtering.</div>
          </div>
        </section>

        <section className="card section" aria-label="prompts-list">
          <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
            <div style={{ display:'flex', gap:8, flexWrap:'wrap', alignItems:'center' }}>
              <input className="input" placeholder="Search prompts..." value={search} onChange={e=>{ setSearch(e.target.value); setPage(1); }} style={{minWidth: 240}} />
              <select className="select" value={subjectFilter} onChange={e=>{ setSubjectFilter(e.target.value); setPage(1); }} aria-label="subject-filter">
                <option value=''>All subjects</option>
                {subjects.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <span className="badge" aria-label="results-count">{visiblePrompts.length} shown</span>
              <div style={{marginLeft:'auto'}} className="exportBtns" aria-label="exports">
                <button className="button secondary" onClick={exportJSON} title="Export JSON">Export JSON</button>
                <button className="button secondary" onClick={exportCSV} title="Export CSV">Export CSV</button>
              </div>
            </div>

            {loading && <div className="small">Loading...</div>}
            {error && <div role="alert" style={{ color:'#ffd6d6' }}>{error}</div>}
            <table className="list" aria-label="prompts-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Seed</th>
                  <th>Subject</th>
                  <th>Content</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {visiblePrompts.map(p => (
                  <tr key={p.id} className="row">
                    <td>{p.id ?? ''}</td>
                    <td>{p.seed ?? ''}</td>
                    <td><span className="badge" aria-label="subject">{p.subject ?? ''}</span></td>
                    <td style={{maxWidth: 420, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}} title={p.content ?? ''}>{p.content ?? ''}</td>
                    <td>{formatDate(p.created_at)}</td>
                    <td>
                      <button className="button ghost" onClick={() => alert(JSON.stringify(p, null, 2))} aria-label="view-prompt">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }} aria-label="pagination">
              <div className="small">Page {page} of {totalPages}</div>
              <div style={{ display:'flex', gap:8 }}>
                <button className="button ghost" onClick={()=> setPage(p => Math.max(1, p-1))} disabled={page<=1} aria-label="prev-page">Prev</button>
                <button className="button ghost" onClick={()=> setPage(p => Math.min(totalPages, p+1))} disabled={page>=totalPages} aria-label="next-page">Next</button>
                <select className="select" value={limit} onChange={e=>{ setLimit(parseInt(e.target.value,10)); setPage(1); }} aria-label="page-size">
                  {[5,10,20,50].map(n => <option key={n} value={n}>{n} / page</option>)}
                </select>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

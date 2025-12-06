import React, {useState} from 'react';

// Lightweight in-browser simulation of swarm task statuses
const initialTasks = [
  { id: 'bugsy', name: 'Bugsy McTester 2', description: 'Security review', status: 'Pending', progress: 0 },
  { id: 'codey', name: 'Codey McBackend 2', description: 'Security audit of API', status: 'Pending', progress: 0 },
  { id: 'deployo', name: 'Deployo McOps 2', description: 'CI workflow wiring', status: 'Pending', progress: 0 },
];

function formatStatus(status) {
  if (status === 'Completed') return 'Completed';
  return status;
}

export default function SwarmDashboard(){
  const [tasks, setTasks] = useState(initialTasks);

  const start = () => {
    setTasks(t => t.map(x => {
      if (x.status === 'Pending') {
        return { ...x, status: 'In Progress' };
      }
      return x;
    }));
  };

  const advance = () => {
    setTasks(prev => prev.map(t => {
      if (t.status === 'In Progress' && t.progress < 100) {
        const nextProg = Math.min(100, t.progress + 25);
        const nextStatus = nextProg >= 100 ? 'Completed' : 'In Progress';
        return { ...t, progress: nextProg, status: nextStatus };
      }
      // if Pending and not started, optionally start
      return t;
    }));
  };

  const allDone = tasks.every(t => t.status === 'Completed');

  return (
    <section aria-label="swarm-dashboard">
      <h2>Swarm Dashboard</h2>
      <p className="muted">Status of the deployed swarm specialists. This is a lightweight frontend visualization.</p>
      <div className="swarm-grid" aria-label="swarm-grid">
        {tasks.map(t => (
          <article key={t.id} className="swarm-card" aria-label={`${t.name} card`}>
            <div className="swarm-card-header">
              <strong>{t.name}</strong>
              <span className={`badge ${t.status === 'Completed' ? 'badge-complete' : t.status === 'In Progress' ? 'badge-progress' : 'badge-pending'}`} aria-label={`status ${t.status}`}>{t.status}</span>
            </div>
            <div className="swarm-card-desc">{t.description}</div>
            <div className="swarm-progress" aria-label={`progress ${t.progress}%`}>{t.progress}%</div>
            <div className="progress-bar" role="progressbar" aria-valuenow={t.progress} aria-valuemin={0} aria-valuemax={100}>
              <div className="progress-fill" style={{ width: `${t.progress}%` }}></div>
            </div>
          </article>
        ))}
      </div>
      <div className="swarm-controls" aria-label="swarm-controls">
        <button onClick={start} className="btn" disabled={tasks.some(t => t.status !== 'Pending')}>
          Start Audit
        </button>
        <button onClick={advance} className="btn btn-secondary" disabled={allDone}>
          Advance Progress
        </button>
      </div>
      {allDone && <p className="success" role="status" aria-live="polite">All swarm tasks completed. Deployment ready.</p>}
    </section>
  );
}

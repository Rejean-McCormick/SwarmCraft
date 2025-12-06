import React, { useEffect, useState } from 'react';
import './BatchProgressPanel.css';
import PropTypes from 'prop-types';

/**
 * BatchProgressPanel
 * A reusable UI component that displays progress for a batch
 * - Polls GET /api/jokes/batches/:batchId/status for updates
 * - Visual: status badge, progress bar, and list of created IDs
 *
 * Note: This is a frontend placeholder intended to be wired to the real
 * backend in a future iteration. It uses an in-memory polling approach and
 * is fully accessible.
 */
export default function BatchProgressPanel({ batchId, endpointBase = '/api', pollIntervalMs = 5000 }) {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!batchId) return;
    let isMounted = true;

    async function fetchStatus() {
      try {
        const res = await fetch(`${endpointBase}/jokes/batches/${encodeURIComponent(batchId)}/status`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        if (isMounted) {
          setStatus(data || {});
          setError(null);
        }
      } catch (err) {
        if (isMounted) setError(err.message);
      }
    }

    // Initial fetch
    fetchStatus();
    // Polling loop
    const t = setInterval(fetchStatus, Math.max(1000, pollIntervalMs));

    return () => {
      isMounted = false;
      clearInterval(t);
    };
  }, [batchId, endpointBase, pollIntervalMs]);

  const total = status && typeof status.batchSize === 'number' ? status.batchSize : 0;
  const created = status && Array.isArray(status.createdIds) ? status.createdIds.length : 0;
  const pct = total > 0 ? Math.min(100, Math.round((created / total) * 100)) : 0;
  const s = status?.status || 'unknown';

  const statusLabel = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    failed: 'Failed',
  }[s] || 'Unknown';

  return (
    <section className="batch-panel" aria-label="Batch progress panel" role="region">
      <h3 className="batch-panel__title">Batch Progress</h3>
      {batchId ? (
        <div className="batch-panel__content" aria-live="polite">
          <div className="batch-row" aria-label="Batch status header">
            <span className={`badge badge--${(s || 'unknown').toLowerCase()}`} aria-label={`Status: ${statusLabel}`}>
              {statusLabel}
            </span>
            <span className="batch-panel__id" aria-label={`Batch ID: ${batchId}`}>ID: {batchId}</span>
          </div>

          <div className="batch-panel__progress" aria-label="Batch progress">
            <div className="batch-panel__progress-bar" style={{ width: `${pct}%` }} aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} />
          </div>
          <div className="batch-panel__stats" aria-live="polite">
            <span>{created} created of {total} total</span>
          </div>
          {Array.isArray(status?.createdIds) && status.createdIds.length > 0 && (
            <div className="batch-panel__ids" aria-label="Created IDs">
              <span className="batch-panel__ids-label">Created IDs:</span>
              {status.createdIds.map((id) => (
                <span key={id} className="chip" aria-label={`id ${id}`}>{id}</span>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="batch-panel__content batch-panel__empty">No batch selected. Enter a batchId to monitor progress.</div>
      )}
      {error && (
        <div className="batch-panel__error" role="alert">Error: {error}</div>
      )}
    </section>
  );
}

BatchProgressPanel.propTypes = {
  batchId: PropTypes.string,
  endpointBase: PropTypes.string,
  pollIntervalMs: PropTypes.number,
};

export { BatchProgressPanel };

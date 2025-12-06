import React, { useEffect, useState } from 'react';

// Props:
// - apiBase: base URL for API (e.g., http://localhost:3000)
// - onSelectUser: function(id) to notify parent when a user is selected
export default function UserList({ apiBase = '', onSelectUser }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetch(`${apiBase.replace(/\/*$/, '')}/users`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load users');
        return res.json();
      })
      .then((data) => {
        if (mounted) {
          setUsers(Array.isArray(data) ? data : []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          console.error(err);
          setError(err);
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [apiBase]);

  if (loading) return <div className="loader" aria-live="polite">Loading users...</div>;
  if (error) return <div className="error" role="alert">Error loading users</div>;

  return (
    <ul className="user-list" aria-label="Users">
      {users.map((u) => (
        <li
          key={u.id}
          className="user-item"
          onClick={() => onSelectUser?.(u.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') onSelectUser?.(u.id);
          }}
          title={u.name}
        >
          <div className="user-item__name">{u.name}</div>
          <div className="user-item__email" aria-label={`Email ${u.email}`}>{u.email}</div>
          {u.created_at ? (
            <span className="user-item__date" aria-label={`Created at ${u.created_at}`}>
              {new Date(u.created_at).toLocaleDateString()}
            </span>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

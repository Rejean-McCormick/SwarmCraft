import React, { useEffect, useState } from 'react';

// Props:
// - apiBase: base URL for API
// - userId: id of selected user
export default function UserDetail({ apiBase = '', userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;
    let mounted = true;
    setLoading(true);
    fetch(`${apiBase.replace(/\/*$/, '')}/users/${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load user');
        return res.json();
      })
      .then((data) => {
        if (mounted) {
          setUser(data);
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
  }, [apiBase, userId]);

  if (loading) return <div className="loader" aria-live="polite">Loading user...</div>;
  if (error) return <div className="error" role="alert">Error loading user</div>;
  if (!user) return null;

  return (
    <div className="user-detail" aria-label={`User ${user.name}`}>
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <p>ID: {user.id}</p>
      <p>Created at: {new Date(user.created_at).toLocaleString()}</p>
    </div>
  );
}

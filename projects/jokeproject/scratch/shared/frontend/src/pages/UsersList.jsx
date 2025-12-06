import React, {useEffect, useState} from 'react';
import { Link } from 'react-router-dom';

export default function UsersList(){
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    fetch('/api/users')
      .then(res => res.json())
      .then(data => { setUsers(data); setLoading(false); })
      .catch(()=>{ setLoading(false); });
  },[]);

  if(loading) return <p>Loading...</p>;
  return (
    <section aria-label="users-list">
      <h2>Users</h2>
      <ul>
        {users.map(u => (
          <li key={u.id}>
            <Link to={`/users/${u.id}`}>{u.name} ({u.email})</Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

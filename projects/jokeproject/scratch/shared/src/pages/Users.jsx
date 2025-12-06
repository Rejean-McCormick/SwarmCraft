import React, { useEffect, useState } from 'react';
import { fetchUsers } from '../src/api';

export default function Users(){
  const [users, setUsers] = useState([]);
  useEffect(()=>{
    fetchUsers().then(setUsers).catch(console.error);
  },[]);
  return (
    <div>
      <h2>Users</h2>
      <ul>
        {users.map(u => (
          <li key={u.id}>{u.name} - {u.email}</li>
        ))}
      </ul>
    </div>
  );
}

import React, {useEffect, useState} from 'react';
import { useParams } from 'react-router-dom';

export default function UserDetails(){
  const { id } = useParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(()=>{
    fetch(`/api/users/${id}`)
      .then(res => {
        if(!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(data => { setUser(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [id]);

  if(loading) return <p>Loading...</p>;
  if(error) return <p style={{color:'red'}}>{error}</p>;
  if(!user) return null;
  return (
    <section aria-label="user-details">
      <h2>User Details</h2>
      <p>Name: {user.name}</p>
      <p>Email: {user.email}</p>
      <p>ID: {user.id}</p>
    </section>
  );
}

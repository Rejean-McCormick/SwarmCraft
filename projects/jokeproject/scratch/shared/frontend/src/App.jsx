import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home.jsx';
import UsersList from './pages/UsersList.jsx';
import UserDetails from './pages/UserDetails.jsx';

export default function App(){
  return (
    <div className="app">
      <header className="header">
        <h1>Frontend Scaffold</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/users">Users</Link>
        </nav>
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/users" element={<UsersList />} />
          <Route path="/users/:id" element={<UserDetails />} />
        </Routes>
      </main>
    </div>
  );
}

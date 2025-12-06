// Frontend store routes and pages
// This module exports a set of React components and a router configuration
// It uses React and React Router v6-style API for modern SPA navigation

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom';
import { createRoot } from 'react-dom/client';

// Tiny components for UI
export function PromoBadge({ text }) {
  return (
    <span className="promo-badge" aria-label={text}>{text}</span>
  );
}

export function ScratchStoreList() {
  const [stores, setStores] = useState([]);
  useEffect(() => {
    // Fetch store metadata for demo
    fetch('/api/store')
      .then(res => res.json())
      .then(data => {
        if (data && data.store) {
          setStores([data.store]);
        }
      }).catch(() => {
        // Fallback mock data
        setStores([{ id: 1, name: 'Mock Store', description: 'A sample store' }]);
      });
  }, []);
  return (
    <div className="store-list">
      <h2>Stores</h2>
      <ul>
        {stores.map(s => (
          <li key={s.id ?? s.name}>
            <Link to={`/store/${s.id ?? s.name}`}>{s.name ?? 'Store'}</Link>
            <p className="muted">{s.description ?? ''}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ScratchStoreDetail() {
  const { id } = useParams();
  const [store, setStore] = useState(null);
  useEffect(() => {
    if (!id) return;
    fetch(`/api/store`, { cache: 'no-store' })
      .then(res => res.json())
      .then(data => {
        // simplistic detail fetch; in real app would request /api/store?storeId
        setStore({ id, name: `Store ${id}`, description: 'A detailed store view' });
      }).catch(() => {
        setStore({ id, name: `Store ${id}`, description: 'A detailed store view' });
      });
  }, [id]);
  if (!store) return <div>Loading store...</div>;
  return (
    <div className="store-detail">
      <h2>{store.name}</h2>
      <p>{store.description}</p>
      <PromoBadge text="Seasonal Promo" />
    </div>
  );
}

export function StoreRoutes() {
  return (
    <Router>
      <nav className="store-nav" aria-label="Store navigation">
        <Link to="/store">All Stores</Link>
        <Link to="/store/promotions">Promotions</Link>
      </nav>
      <Routes>
        <Route path="/store" element={<ScratchStoreList />} />
        <Route path="/store/:id" element={<ScratchStoreDetail />} />
        <Route path="/store/promotions" element={<div><h2>Promotions</h2><PromoBadge text="20% OFF"/></div>} />
      </Routes>
    </Router>
  );
}

// Export default for convenience in some apps
export default StoreRoutes;

// Init function to mount into a DOM root for Vite-based app
export function initStoreRoutes(rootEl) {
  if (!rootEl) return;
  const app = StoreRoutes();
  // Use React 18 createRoot to mount
  const r = createRoot(rootEl);
  r.render(<StoreRoutes />);
}

    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Note: The actual render call happens via initStoreRoutes

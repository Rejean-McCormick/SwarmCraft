import React, { useEffect, useMemo, useState } from 'react';

/*
  Minimal in-file router and store UI for MVP
  - Routes: /store, /store/product/:id, /about-us, /admin
  - Components: PromotionBanner, ProductCard, CartDrawer
  - Data: fetch /api/store endpoints with graceful fallback
  - Accessibility: aria-labels, semantic roles, keyboard nav
  - Styling: inline CSS-in-JS for portability; can be migrated to CSS Modules
*/

// Simple Link utility
function Link({ to, children, onNavigate, ariaLabel }) {
  const handleClick = (e) => {
    // Handle middle-click or cmd-click as normal
    if (e.metaKey || e.altKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    onNavigate && onNavigate(to);
  };
  return (
    <a href={to} onClick={handleClick} aria-label={ariaLabel}>
      {children}
    </a>
  );
}

// Simple path matcher supporting /store/product/:id
function matchRoute(pathname, routePath) {
  const paramNames = [];
  const escaped = routePath.replace(/([.+^=!:${}()|[\]\/\\])/g, '\\$1');
  const regexPath = escaped
    .replace(/:([^/]+)/g, (m, key) => {
      paramNames.push(key);
      return '([^/]+)';
    });
  const regex = new RegExp('^' + regexPath + '$');
  const m = pathname.match(regex);
  if (!m) return null;
  const params = {};
  paramNames.forEach((name, idx) => {
    params[name] = m[idx + 1];
  });
  return params;
}

// Lightweight router
function Router({ children }) {
  const [path, setPath] = useState(typeof window !== 'undefined' ? window.location.pathname : '/store');

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const navigate = (to) => {
    if (!to) return;
    window.history.pushState(null, '', to);
    setPath(to);
  };

  // Resolve to a component via matching
  const routes = [
    { path: '/store', exact: true, component: StoreListPage },
    { path: '/store/product/:id', exact: true, component: StoreProductPage },
    { path: '/about-us', exact: true, component: AboutUsPage },
    { path: '/admin', exact: true, component: AdminPage },
  ];

  for (const r of routes) {
    const params = matchRoute(path, r.path);
    if (params) {
      const Comp = r.component;
      return <Comp key={r.path} params={params} navigate={navigate} />;
    }
  }

  // Fallback to first route
  const Fallback = StoreListPage;
  return <Fallback navigate={navigate} />;
}

// Promotion banner
export function PromotionBanner({ message = 'Spring Sale: 15% off all items', onClose }) {
  return (
    <div role="region" aria-label="Promotion Banner" style={styles.banner}>
      <span style={styles.bannerText}>{message}</span>
      {onClose && (
        <button aria-label="Close promotion" onClick={onClose} style={styles.closeBtn}>
          ×
        </button>
      )}
    </div>
  );
}

// Product Card
export function ProductCard({ product, onAdd, onOpen }) {
  const { id, name, price, image, promo } = product;
  return (
    <div style={styles.card} aria-label={`Product ${name}`}>
      {promo && (
        <div style={styles.promoTag} aria-label="Promotional tag">
          {promo}
        </div>
      )}
      <img src={image} alt={name} style={styles.image} />
      <h3 style={styles.cardTitle}>{name}</h3>
      <p style={styles.price}>${price.toFixed(2)}</p>
      <div style={styles.cardActions}>
        <button aria-label={`View ${name}`} onClick={() => onOpen(id)} style={styles.btnOutline}>
          View
        </button>
        <button aria-label={`Add ${name} to cart`} onClick={() => onAdd(product)} style={styles.btnPrimary}>
          Add to Cart
        </button>
      </div>
    </div>
  );
}

// Cart Drawer
export function CartDrawer({ open, onClose, items, onCheckout, onUpdateQty }) {
  const total = items.reduce((a, it) => a + it.product.price * it.qty, 0);
  return (
    <aside aria-label="Shopping cart" style={{ ...styles.drawer, transform: open ? 'translateX(0)' : 'translateX(100%)' }}>
      <div style={styles.drawerHeader}>
        <h4 style={styles.drawerTitle}>Cart</h4>
        <button aria-label="Close cart" onClick={onClose} style={styles.closeBtn}>×</button>
      </div>
      <div style={styles.drawerBody}>
        {items.length === 0 && <p style={styles.empty}>Your cart is empty.</p>}
        {items.map((it) => (
          <div key={it.product.id} style={styles.cartItem}>
            <span style={styles.cartName}>{it.product.name}</span>
            <div style={styles.qtyGroup}>
              <button aria-label="Decrease quantity" onClick={() => onUpdateQty(it.product.id, Math.max(0, it.qty - 1))} style={styles.qtyBtn}>-</button>
              <span aria-label="Quantity" style={styles.qty}>{it.qty}</span>
              <button aria-label="Increase quantity" onClick={() => onUpdateQty(it.product.id, it.qty + 1)} style={styles.qtyBtn}>+</button>
            </div>
            <span style={styles.cartPrice}>${(it.product.price * it.qty).toFixed(2)}</span>
          </div>
        ))}
      </div>
      <div style={styles.drawerFooter}>
        <div style={styles.totalLine}>Total: <strong>${total.toFixed(2)}</strong></div>
        <button aria-label="Checkout" onClick={onCheckout} style={styles.btnPrimaryWide}>Checkout</button>
      </div>
    </aside>
  );
}

// Store List Page
function StoreListPage({ navigate }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);
  const [drawer, setDrawer] = useState(false);
  const [promoVisible, setPromoVisible] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchProducts = async () => {
      try {
        const res = await fetch('/api/store/products');
        if (res.ok) {
          const data = await res.json();
          if (mounted) setProducts(data.products || data); // tolerate variations
        } else {
          throw new Error('API error');
        }
      } catch {
        // Fallback sample data
        if (mounted) {
          setProducts([
            { id: 'p1', name: 'Aurora Lamp', price: 29.99, image: '/shared/assets/lamp.jpg', promo: 'New' },
            { id: 'p2', name: 'Nimbus Mug', price: 12.5, image: '/shared/assets/mug.jpg' },
            { id: 'p3', name: 'Cloud Cushion', price: 18.0, image: '/shared/assets/cushion.jpg', promo: 'Sale' },
          ]);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchProducts();
    return () => {
      mounted = false;
    };
  }, []);

  const addToCart = (product) => {
    setCart((c) => {
      const exists = c.find((it) => it.product.id === product.id);
      if (exists) {
        return c.map((it) => (it.product.id === product.id ? { ...it, qty: it.qty + 1 } : it));
      }
      return [...c, { product, qty: 1 }];
    });
    setDrawer(true);
  };

  const viewProduct = (id) => {
    navigate(`/store/product/${id}`);
  };

  const checkout = () => {
    // Simple invoice generation and show alert modal-like block
    const invoice = generateInvoice(cart);
    setPromoVisible(false);
    // Show as a modal-like alert at the top of the page
    alert(invoice);
    // Clear cart after checkout for MVP
    setCart([]);
    setDrawer(false);
  };

  return (
    <main aria-label="Store page" style={styles.page}>
      {promoVisible && (
        <PromotionBanner
          message="Spring Promotion: Free shipping on orders over $50"
          onClose={() => setPromoVisible(false)}
        />
      )}
      <header style={styles.header}>
        <h1 style={styles.brand}>Mock Store</h1>
        <nav aria-label="Main navigation" style={styles.nav}>
          <Link to="/store" onNavigate={navigate} ariaLabel="Store">
            Store
          </Link>
          <Link to="/about-us" onNavigate={navigate} ariaLabel="About Us">
            About Us
          </Link>
          <Link to="/admin" onNavigate={navigate} ariaLabel="Admin">
            Admin
          </Link>
          <button aria-label="Open cart" onClick={() => setDrawer(true)} style={styles.cartBtn}>
            Cart ({cart.reduce((a, b) => a + b.qty, 0)})
          </button>
        </nav>
      </header>

      <section aria-label="Product grid" style={styles.grid}>
        {loading && <p>Loading products...</p>}
        {!loading && products.map((p) => (
          <ProductCard key={p.id} product={p} onAdd={addToCart} onOpen={viewProduct} />
        ))}
      </section>

      <CartDrawer
        open={drawer}
        onClose={() => setDrawer(false)}
        items={cart}
        onCheckout={checkout}
        onUpdateQty={(id, qty) => {
          setCart((c) => {
            const updated = c.map((it) => (it.product.id === id ? { ...it, qty } : it));
            return updated.filter((it) => it.qty > 0);
          });
        }}
      />
    </main>
  );
}

// Product Detail Page
function StoreProductPage({ params, navigate }) {
  const { id } = params;
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [qty, setQty] = useState(1);

  useEffect(() => {
    let mounted = true;
    const fetchProduct = async () => {
      try {
        const res = await fetch(`/api/store/product/${id}`);
        if (res.ok) {
          const data = await res.json();
          if (mounted) setProduct(data.product || data);
        } else {
          throw new Error('Not found');
        }
      } catch {
        // Fallback sample
        if (mounted) {
          setProduct({ id, name: 'Sample Product', price: 19.99, image: '/shared/assets/product.jpg', description: 'A great item.' });
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchProduct();
    return () => {
      mounted = false;
    };
  }, [id]);

  if (loading) return <div style={styles.page}>Loading product...</div>;
  if (!product) return <div style={styles.page}>Product not found</div>;

  const add = () => navigate('/store');

  return (
    <section aria-label={`Product ${product.name}`} style={styles.page}>
      <button aria-label="Back to store" onClick={() => navigate('/store')} style={styles.backBtn}>Back to Store</button>
      <div style={styles.productDetail}>
        <img src={product.image} alt={product.name} style={styles.productImage} />
        <div style={styles.productInfo}>
          <h2 style={styles.productTitle}>{product.name}</h2>
          <p style={styles.productDesc}>{product.description || ''}</p>
          <p style={styles.productPrice}>${product.price.toFixed(2)}</p>
          <div style={styles.qtyGroup}>
            <button aria-label="Decrease quantity" onClick={() => setQty((q) => Math.max(1, q - 1))} style={styles.qtyBtn}>-</button>
            <span aria-label="Selected quantity" style={styles.qty}>{qty}</span>
            <button aria-label="Increase quantity" onClick={() => setQty((q) => q + 1)} style={styles.qtyBtn}>+</button>
          </div>
          <button aria-label="Add to cart" onClick={() => alert(`Added ${qty} x ${product.name} to cart (mock)`)} style={styles.btnPrimary}>Add to Cart</button>
          <button aria-label="Go to store" onClick={add} style={styles.btnOutline}>Continue Shopping</button>
        </div>
      </div>
    </section>
  );
}

// About Us Page
function AboutUsPage() {
  return (
    <section aria-label="About Us" style={styles.page}>
      <h1>About Us</h1>
      <p>We are a mock storefront to demonstrate MVP frontend UI patterns.</p>
    </section>
  );
}

// Admin Page placeholder
function AdminPage() {
  return (
    <section aria-label="Admin" style={styles.page}>
      <h1>Admin Dashboard</h1>
      <p>Lightweight admin panel for MVP: manage products, view orders.</p>
    </section>
  );
}

// Helper: generate a simple invoice string
function generateInvoice(cart) {
  const lines = cart.map((it) => `${it.product.name} x${it.qty} - $${(it.product.price * it.qty).toFixed(2)}`);
  const total = cart.reduce((a, b) => a + b.product.price * b.qty, 0);
  const now = new Date().toLocaleString();
  return [`Invoice - ${now}`, ...lines, `Total: $${total.toFixed(2)}`].join('\n');
}

const styles = {
  page: {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  banner: {
    background: '#f6f6f9',
    border: '1px solid #e3e4ea',
    padding: '12px 16px',
    borderRadius: 8,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  bannerText: { fontWeight: 600 },
  closeBtn: {
    border: 'none',
    background: 'transparent',
    fontSize: 18,
    cursor: 'pointer',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  brand: { margin: 0 },
  nav: {
    display: 'flex',
    gap: 12,
    alignItems: 'center',
  },
  cartBtn: {
    padding: '8px 12px',
    borderRadius: 6,
    border: '1px solid #ccc',
    background: '#fff',
    cursor: 'pointer',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
    gap: 16,
  },
  card: {
    border: '1px solid #e5e5e5',
    borderRadius: 12,
    padding: 12,
    background: '#fff',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
  },
  image: { width: 140, height: 120, objectFit: 'cover', marginBottom: 8, borderRadius: 8 },
  promoTag: { position: 'absolute', top: 8, left: 8, background: '#ff6b6b', color: '#fff', padding: '4px 8px', borderRadius: 4, fontSize: 12 },
  cardTitle: { margin: '6px 0 4px', fontSize: 16 },
  price: { margin: 0, color: '#333' },
  cardActions: { display: 'flex', gap: 8, marginTop: 8 },
  btnOutline: { padding: '8px 12px', borderRadius: 6, border: '1px solid #888', background: '#fff', cursor: 'pointer' },
  btnPrimary: { padding: '8px 12px', borderRadius: 6, border: 'none', background: '#0070f3', color: '#fff', cursor: 'pointer' },
  drawer: {
    position: 'fixed',
    top: 0,
    right: 0,
    width: 360,
    height: '100%',
    background: '#fff',
    borderLeft: '1px solid #ddd',
    boxShadow: '-4px 0 20px rgba(0,0,0,0.1)',
    padding: 12,
    display: 'flex',
    flexDirection: 'column',
    transition: 'transform 0.3s ease',
    zIndex: 1000,
  },
  drawerHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 8, borderBottom: '1px solid #eee' },
  drawerTitle: { margin: 0 },
  drawerBody: { flex: 1, overflowY: 'auto', padding: 4 },
  empty: { color: '#777' },
  cartItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 8, borderBottom: '1px solid #f1f1f1' },
  cartName: { flex: 2 },
  cartPrice: { width: 90, textAlign: 'right' },
  qtyGroup: { display: 'flex', alignItems: 'center', gap: 6 },
  qtyBtn: { width: 22, height: 22, borderRadius: 4, border: '1px solid #ccc', cursor: 'pointer' },
  qty: { minWidth: 20, textAlign: 'center' },
  drawerFooter: { paddingTop: 8, borderTop: '1px solid #eee' },
  totalLine: { display: 'flex', justifyContent: 'space-between', marginBottom: 8 },
  btnPrimaryWide: { width: '100%', padding: '12px', borderRadius: 6, background: '#28a745', color: '#fff', border: 'none', cursor: 'pointer' },
  backBtn: { padding: '8px 12px', borderRadius: 6, border: '1px solid #ccc', background: '#fff', cursor: 'pointer', marginBottom: 12 },
  productDetail: { display: 'flex', gap: 24, alignItems: 'center' },
  productImage: { width: 320, height: 240, objectFit: 'cover', borderRadius: 8 },
  productInfo: { maxWidth: 520 },
  productTitle: { fontSize: 28, margin: 0 },
  productDesc: { color: '#555' },
  productPrice: { fontSize: 22, marginTop: 6 },
  btnPrimary: { padding: '10px 14px', borderRadius: 6, border: 'none', background: '#0070f3', color: '#fff', cursor: 'pointer', marginRight: 8 },
  btnOutline: { padding: '10px 14px', borderRadius: 6, border: '1px solid #888', background: '#fff', cursor: 'pointer' },
  brandImg: { height: 40 },
  qtyGroupLabel: { marginLeft: 6 },
};

export default function StorePagesApp() {
  return (
    <Router>
      {/* The Router will render the matched route component */}
    </Router>
  );
}

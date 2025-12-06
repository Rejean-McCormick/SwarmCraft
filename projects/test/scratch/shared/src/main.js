import { initStoreRoutes } from '../frontend/store_routes.js';

const root = document.getElementById('root');
function bootstrap(){
  // Mount SPA into root
  if (root && typeof initStoreRoutes === 'function') {
    initStoreRoutes(root);
  } else {
    root.innerHTML = '<p>Store frontend not initialized.</p>';
  }
}

bootstrap();

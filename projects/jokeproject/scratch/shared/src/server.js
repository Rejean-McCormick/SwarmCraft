"use strict";

// Entry point for the backend API. Exposes a createApp() function that
// initializes the Express app, DB and routes for the /users endpoints.

const express = require('express');

async function createApp() {
  // Lazy require to avoid circular deps during startup in tests
  const dbInit = require('./db');
  // Initialize DB (create tables if needed)
  await dbInit.initDb();

  const app = express();
  app.use(express.json());

  // Mount user routes at /users
  const usersRouter = require('./routes/users');
  app.use('/users', usersRouter());

  // Simple health root
  app.get('/', (req, res) => res.json({ ok: true, route: '/users' }));

  return app;
}

module.exports = { createApp };

// If run directly, start the HTTP server
if (require.main === module) {
  (async () => {
    try {
      const app = await createApp();
      const port = process.env.PORT || 3000;
      app.listen(port, () => {
        console.log(`Server listening on port ${port}`);
      });
    } catch (err) {
      console.error('Failed to start server', err);
      process.exit(1);
    }
  })();
}

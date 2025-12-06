import express from 'express';
export function setupRoutes(app: express.Application){
  app.get('/ping', (_req, res) => res.send({ ok: true }));
}

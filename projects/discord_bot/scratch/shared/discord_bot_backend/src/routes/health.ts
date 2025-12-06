import express from 'express';
export function healthRouter(): express.Router {
  const r = express.Router();
  r.get('/health', (_req, res) => res.status(200).send({ status: 'ok' }));
  return r;
}

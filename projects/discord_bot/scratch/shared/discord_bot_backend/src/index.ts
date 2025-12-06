import express from 'express';
import dotenv from 'dotenv';
import { setupRoutes } from './routes';

dotenv.config();
const app = express();
const port = process.env.PORT ? parseInt(process.env.PORT) : 3000;
app.use(express.json());
setupRoutes(app);
app.get('/health', (_req, res) => res.status(200).send({ status: 'ok' }));
app.listen(port, () => console.log(`Bot backend listening on port ${port}`));

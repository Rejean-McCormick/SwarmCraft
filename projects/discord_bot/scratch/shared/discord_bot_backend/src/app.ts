import express from 'express';
import dotenv from 'dotenv';
import routes from './routes';
import routesHealth from './routes_health';
import DB from './db';

dotenv.config();

const app = express();
app.use(express.json());
app.use('/api', routes);
app.use('/health', routesHealth);

const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;

export default app;

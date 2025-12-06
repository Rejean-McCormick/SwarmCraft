import request from 'supertest';
import app from '../../src/app';

describe('GET /api/health', () => {
  it('should respond with 200', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
  });
});

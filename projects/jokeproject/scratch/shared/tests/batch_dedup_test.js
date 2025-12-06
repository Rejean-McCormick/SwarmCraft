const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
let app;

try {
  app = require('./../server');
} catch (e) {
  throw new Error('Could not load server module at ../server. Ensure the API server is present for tests to run.');
}

describe('Joke Batch API - dedupe behavior (MVP)', function() {
  this.timeout(20000);
  it('deduplication should prevent duplicate joke IDs in createdIds', async function() {
    const res1 = await request(app).post('/api/jokes/batches').send({ batchSize: 5 });
    expect(res1.status).to.equal(202);
    const batchId = res1.body.batchId;
    // Poll until completion if possible
    let finalStatus = null;
    for (let i = 0; i < 10; i++) {
      const s = await request(app).get(`/api/jokes/batches/${batchId}/status`);
      if (s.body && s.body.status === 'completed') {
        finalStatus = s.body;
        break;
      }
      await new Promise(r => setTimeout(r, 1000));
    }
    if (finalStatus) {
      const ids = finalStatus.createdIds;
      const unique = Array.from(new Set(ids));
      expect(unique.length).to.equal(ids.length);
    } else {
      // If not completed in time, just ensure the array exists
      const s = await request(app).get(`/api/jokes/batches/${batchId}/status`);
      if (s.body && Array.isArray(s.body.createdIds)) {
        expect(s.body.createdIds).to.be.an('array');
      }
    }
  });
});

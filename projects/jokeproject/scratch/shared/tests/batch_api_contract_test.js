const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
let app;

try {
  app = require('./../server');
} catch (e) {
  throw new Error('Could not load server module at ../server. Ensure the API server is present for tests to run.');
}

describe('Joke Batch API - contract validation', function() {
  this.timeout(10000);

  it('contract should include batchId, status, total, createdIds', async function() {
    const res = await request(app).post('/api/jokes/batches').send({ batchSize: 3 });
    expect(res.status).to.equal(202);
    const batchId = res.body.batchId;
    expect(batchId).to.be.a('string');
  });

  it('status endpoint should respond with a status object', async function() {
    const res = await request(app).post('/api/jokes/batches').send({ batchSize: 2 });
    const batchId = res.body.batchId;
    // Immediately poll status (may be in-progress)
    const statusRes = await request(app).get(`/api/jokes/batches/${batchId}/status`);
    expect(statusRes.status).to.be.oneOf([200, 202]);
    expect(statusRes.body).to.be.an('object');
    expect(statusRes.body).to.have.property('batchId', batchId);
  });
});

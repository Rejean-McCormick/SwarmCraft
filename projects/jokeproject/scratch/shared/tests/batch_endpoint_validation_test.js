const request = require('supertest');
const chai = require('chai');
const expect = chai.expect;
let app;

try {
  // Adjust path if your server entry point differs
  app = require('./../server');
} catch (e) {
  // If the server module isn't yet available, tests will fail fast with a helpful error
  throw new Error('Could not load server module at ../server. Ensure the API server is present for tests to run.');
}

describe('Joke Batch API - endpoint validation', function() {
  this.timeout(10000);

  it('returns 400 when batchSize is missing', async function() {
    const res = await request(app)
      .post('/api/jokes/batches')
      .send({});
    expect(res.status).to.equal(400);
  });

  it('returns 400 when batchSize is out of range', async function() {
    const resLow = await request(app).post('/api/jokes/batches').send({ batchSize: 0 });
    expect(resLow.status).to.equal(400);

    const resHigh = await request(app).post('/api/jokes/batches').send({ batchSize: 1001 });
    expect(resHigh.status).to.equal(400);
  });

  it('returns 202 with batchId for valid input', async function() {
    const res = await request(app).post('/api/jokes/batches').send({ batchSize: 5 });
    expect(res.status).to.equal(202);
    expect(res.body).to.be.an('object');
    expect(res.body).to.have.property('batchId');
    expect(res.body).to.have.property('status');
    expect(res.body).to.have.property('total', 5);
    expect(res.body).to.have.property('createdIds');
    expect(res.body.createdIds).to.be.an('array');
  });
});

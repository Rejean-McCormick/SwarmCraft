const { v4: uuidv4 } = require('uuid');

class BatchStore {
  constructor() {
    this.batches = new Map();
  }

  createBatch(batchSize, prompts = []) {
    const batchId = uuidv4();
    const batch = {
      batchId,
      batchSize,
      prompts,
      status: 'created',
      startedAt: null,
      completedAt: null,
      createdIds: [],
      error: null
    };
    this.batches.set(batchId, batch);
    return batch;
  }

  startBatch(batchId) {
    const b = this.batches.get(batchId);
    if (!b) return null;
    b.status = 'in_progress';
    b.startedAt = new Date().toISOString();
    return b;
  }

  addCreatedId(batchId, id) {
    const b = this.batches.get(batchId);
    if (!b) return;
    b.createdIds.push(id);
    // Auto-complete when reached batchSize
    if (b.createdIds.length >= b.batchSize) {
      b.status = 'completed';
      b.completedAt = new Date().toISOString();
    }
  }

  failBatch(batchId, error) {
    const b = this.batches.get(batchId);
    if (!b) return;
    b.status = 'failed';
    b.error = error;
    b.completedAt = new Date().toISOString();
  }

  getStatus(batchId) {
    return this.batches.get(batchId) || null;
  }
}

module.exports = { BatchStore };

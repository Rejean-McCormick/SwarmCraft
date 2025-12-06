// Batch worker for JokeGen batch generation
// Each worker receives a list of seeds and returns generated jokes for those seeds
const { parentPort, workerData } = require('worker_threads');
const { generateJoke } = require('./generator');

if (workerData && Array.isArray(workerData.seeds)) {
  const batchId = workerData.batchId;
  const seeds = workerData.seeds;
  const results = seeds.map(seed => {
    const joke = generateJoke(seed, {});
    return { seed, joke };
  });
  parentPort.postMessage({ batchId, results });
} else if (workerData && Array.isArray(workerData.seeds) === false) {
  // Fallback single-seed path (not used in this design)
  const seed = workerData.seed;
  const joke = generateJoke(seed || 'seed', {});
  parentPort.postMessage({ batchId: workerData.batchId, joke });
} else {
  parentPort.postMessage({ error: 'Invalid worker data' });
}

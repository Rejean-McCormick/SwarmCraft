// Joke generator worker
// Receives tasks with a seed and returns a generated joke structure.

const { parentPort } = require('worker_threads');

function hashSeed(seed) {
  // Simple deterministic hash for seeds to vary outputs
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return h;
}

function generateJokeFromSeed(seed) {
  const h = hashSeed(seed || 'seed');
  const endings = [
    'to get to the other side',
    'because it heard the cookie jar calling',
    'to prove it could do stand-up on Tuesdays',
    'to escape the encroaching pun-demic',
    'because nobody expects the seed bomb',
  ];
  const animals = ['a cat', 'a chicken', 'a programmer', 'an engineer', 'a robot'];
  const topics = ['clouds', 'jokes', 'coffee', 'feedback', 'retries'];
  const suffix = endings[h % endings.length];
  const animal = animals[(h >> 4) % animals.length];
  const topic = topics[(h >> 2) % topics.length];
  // Construct a deterministic joke with a clear setup/punchline
  const setup = `Seed ${seed}: ${animal} ${suffix}.`;
  const punchline = `Topic: ${topic}.`;
  return { setup, punchline, category: 'generated', author: 'Worker' };
}

parentPort.on('message', (task) => {
  try {
    if (!task || typeof task.seed !== 'string') {
      parentPort.postMessage({ error: 'Invalid task format' });
      return;
    }
    const joke = generateJokeFromSeed(task.seed);
    parentPort.postMessage({ taskId: task.id, joke });
  } catch (e) {
    parentPort.postMessage({ taskId: task.id, error: e.message, stack: e.stack });
  }
});

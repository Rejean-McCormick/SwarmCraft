function generateJoke(seed, templates) {
  // Very simple deterministic joke based on seed
  const base = (seed || 'seed').toString();
  const setups = ["Why did the chicken cross the road?", "I heard a joke about", "What do you call a", "Guess what?" ];
  const punch = ["to get to the other side.", "on a Tuesday it20s better.", "with a punchline, it20s funny.", "that made you smile."];
  const s = setups[(base.charCodeAt(0) + (seed.length || 0)) % setups.length];
  const p = punch[(base.charCodeAt(1) + (seed.length || 1)) % punch.length];
  return { setup: s, punchline: p, category: templates?.category || 'general', author: templates?.author || 'generator' };
}

function generateBatch(count, seedBase = 'seed', templates) {
  const arr = [];
  for (let i = 0; i < count; i++) {
    const seed = seedBase + '-' + i;
    arr.push(generateJoke(seed, templates));
  }
  return arr;
}

module.exports = { generateJoke, generateBatch };

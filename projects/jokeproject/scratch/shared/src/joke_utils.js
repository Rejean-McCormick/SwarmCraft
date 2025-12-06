// Joke utility helpers for JokeGen
function hashSeed(seed) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return h;
}

function createJoke(index) {
  const setups = [
    'Why do programmers prefer dark mode?',
    'What do you call a robot who loves poetry?',
    'Why did the database administrator bring a ladder?',
    'How many software developers does it take to change a light bulb?',
    'Why do computers sing in the morning?'
  ];
  const punchlines = [
    'Because light attracts bugs.',
    'A bard-bot of the silicon era.',
    'To reach the high-level data!',
    'None \\\u2014 the user just tells it to do it.',
    'Because they can\\u2019t stop caching the sunrise.'
  ];
  const cat = ['tech', 'pun', 'random'][index % 3];
  const setup = setups[index % setups.length];
  const punchline = punchlines[index % punchlines.length];
  return {
    id: `joke_${index}_${Date.now()}`,
    setup,
    punchline,
    category: cat,
    author: 'system',
    created_at: new Date().toISOString()
  };
}

module.exports = { createJoke };

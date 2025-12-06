// Tiny JokeGen API server for local testing
const express = require('express');
const api = require('./src/joke_gen_api.js');
const app = express();
const port = process.env.PORT || 8080;

app.use('/api', api);
app.listen(port, () => {
  console.log(`JokeGen API running on port ${port}`);
});

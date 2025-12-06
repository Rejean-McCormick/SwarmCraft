require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');
const http = require('http');
const token = process.env.DISCORD_BOT_TOKEN;

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// Basic bot lifecycle
client.once('ready', () => {
  console.log(`Bot ready: ${client.user.tag}`);
});

// Health check HTTP server for Kubernetes / health endpoint
http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('OK');
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
}).listen(3000, () => {
  console.log('Health check server listening on port 3000');
});

client.login(token).catch(console.error);

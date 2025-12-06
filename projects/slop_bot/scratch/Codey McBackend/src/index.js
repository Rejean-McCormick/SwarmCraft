require('dotenv').config();
const { Client, GatewayIntentBits, Partials, Events } = require('discord.js');
const axios = require('axios');

const token = process.env.DISCORD_BOT_TOKEN;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const OPENAI_API_URL = process.env.OPENAI_API_URL || 'https://api.openai.com/v1/chat/completions';

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent], partials: [Partials.Message, Partials.Channel, Partials.Reaction] });

client.once(Events.ClientReady, () => {
  console.log(`Logged in as ${client.user.tag}`);
});

async function callLLM(messages) {
  try {
    const res = await axios.post(OPENAI_API_URL, {
      model: 'gpt-3.5-turbo',
      messages: messages
    }, {
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    return res.data;
  } catch (e) {
    console.error('LLM call failed:', e.message);
    throw e;
  }
}

client.on(Events.MessageCreate, async (message) => {
  if (message.author.bot) return;
  if (!message.content.startsWith('!llm')) return;

  const prompt = [{ role: 'user', content: message.content.replace(/^!llm\s*/, '') }];
  try {
    const llmResponse = await callLLM(prompt);
    const reply = llmResponse.choices?.[0]?.message?.content ?? 'No response from LLM';
    await message.reply(reply);
  } catch (err) {
    await message.reply('Error calling LLM API.');
  }
});

client.login(token).catch(err => {
  console.error('Discord login failed:', err);
});

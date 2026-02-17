const { Client, GatewayIntentBits, SlashCommandBuilder } = require('discord.js');
const fetch = require('node-fetch');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

const TOKEN = process.env.DISCORD_TOKEN;
const PASTEBIN_DEV_KEY = process.env.PASTEBIN_DEV_KEY;

const OWNER_ID = '1424707396395339776';
const YOUR_SERVER_ID = '1448399752201900045';

let keys = {};

// Health check server
const http = require('http');
const PORT = process.env.PORT || 8080;
http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Bot is alive');
}).listen(PORT);
console.log(`Health check listening on port ${PORT}`);

// Load initial keys (from your current paste or empty)
async function loadKeys() {
  try {
    const res = await fetch('https://pastebin.com/raw/U4xGsV2D');
    if (res.ok) {
      keys = JSON.parse(await res.text());
      console.log('Initial keys loaded');
    }
  } catch (e) {
    console.log('Initial load failed, starting empty:', e.message);
    keys = {};
  }
}

// Create NEW paste and return its raw URL
async function createNewPaste() {
  const content = JSON.stringify(keys, null, 2);

  const form = new URLSearchParams();
  form.append('api_dev_key', PASTEBIN_DEV_KEY);
  form.append('api_option', 'paste');
  form.append('api_paste_code', content);
  form.append('api_paste_private', '1'); // unlisted
  form.append('api_paste_name', 'Federal Keys - ' + new Date().toISOString());
  form.append('api_paste_expire_date', 'N');
  form.append('api_paste_format', 'json');

  const res = await fetch('https://pastebin.com/api/api_post.php', {
    method: 'POST',
    body: form,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });

  const url = await res.text();

  if (url.includes('Bad API') || !url.includes('pastebin.com')) {
    throw new Error(url || 'Pastebin API error');
  }

  const rawUrl = url.replace('https://pastebin.com/', 'https://pastebin.com/raw/');
  console.log('New paste created:', rawUrl);
  return rawUrl;
}

client.once('ready', async () => {
  console.log(`Bot online: ${client.user.tag}`);
  await loadKeys();

  const guild = client.guilds.cache.get(YOUR_SERVER_ID);
  if (guild) {
    const cmds = [
      new SlashCommandBuilder()
        .setName('genkey')
        .setDescription('Generate a key')
        .addIntegerOption(o => o.setName('uses').setDescription('Max uses (blank = unlimited)').setMinValue(1))
        .addIntegerOption(o => o.setName('hours').setDescription('Hours until expiry (blank = never)').setMinValue(1)),
      new SlashCommandBuilder()
        .setName('deactivate-key')
        .setDescription('Deactivate a key')
        .addStringOption(o => o.setName('key').setDescription('Key to deactivate').setRequired(true)),
      new SlashCommandBuilder()
        .setName('list-keys')
        .setDescription('List active keys')
    ];

    await guild.commands.set(cmds.map(c => c.toJSON()));
    console.log('Commands registered');
  }
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;
  if (interaction.user.id !== OWNER_ID) {
    return interaction.reply({ content: 'Owner only', ephemeral: true });
  }

  try {
    if (interaction.commandName === 'genkey') {
      const uses = interaction.options.getInteger('uses');
      const hours = interaction.options.getInteger('hours');

      const part1 = Math.random().toString(36).slice(2,7).toUpperCase();
      const part2 = Math.random().toString(36).slice(2,7).toUpperCase();
      const key = `FED-${part1}-${part2}`;

      let expires = null;
      if (hours) expires = Date.now() + hours * 60 * 60 * 1000;

      keys[key] = {
        active: true,
        remainingUses: uses || null,
        expires,
        generatedAt: Date.now(),
        generatedBy: interaction.user.tag
      };

      const newRawUrl = await createNewPaste();

      let reply = `**Key generated:** \`${key}\`\n`;
      reply += `Uses: ${uses || 'unlimited'}\n`;
      reply += `Expires: ${hours ? `in ${hours} hours` : 'never'}\n\n`;
      reply += `**Update your script with this new Pastebin link:** ${newRawUrl}`;

      await interaction.reply({ content: reply, ephemeral: true });
    }

    else if (interaction.commandName === 'deactivate-key') {
      const key = interaction.options.getString('key').trim().toUpperCase();

      if (keys[key]) {
        keys[key].active = false;
        const newRawUrl = await createNewPaste();
        await interaction.reply({ content: `Deactivated **${key}**\nNew Pastebin: ${newRawUrl}`, ephemeral: true });
      } else {
        await interaction.reply({ content: `Key **${key}** not found`, ephemeral: true });
      }
    }

    else if (interaction.commandName === 'list-keys') {
      let msg = '**Active keys:**\n';
      for (const [k, v] of Object.entries(keys)) {
        if (v.active) {
          msg += `- ${k} (Uses: ${v.remainingUses || '∞'}, Expires: ${v.expires ? new Date(v.expires).toLocaleString() : 'never'})\n`;
        }
      }
      await interaction.reply({ content: msg || 'No active keys', ephemeral: true });
    }
  } catch (err) {
    console.error(err);
    await interaction.reply({ content: 'Error saving to Pastebin: ' + err.message, ephemeral: true });
  }
});

client.login(TOKEN);

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
const PASTEBIN_PASTE_ID = 'U4xGsV2D';  // your fixed paste
const PASTEBIN_RAW_URL = `https://pastebin.com/raw/${PASTEBIN_PASTE_ID}`;

const OWNER_ID = '1424707396395339776';
const YOUR_SERVER_ID = '1448399752201900045';

let keys = {};

// Health check server (fixes Railway hang)
const http = require('http');
const PORT = process.env.PORT || 8080;
http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Bot is alive');
}).listen(PORT);
console.log(`Health check server listening on port ${PORT}`);

// Load keys from Pastebin
async function loadKeys() {
  try {
    const res = await fetch(PASTEBIN_RAW_URL);
    if (!res.ok) throw new Error(`Pastebin fetch failed: ${res.status}`);
    const text = await res.text();
    keys = JSON.parse(text);
    console.log('Loaded keys from Pastebin');
  } catch (err) {
    console.log('Pastebin load error (starting empty):', err.message);
    keys = {};
  }
}

// Save keys to Pastebin (overwrite same paste)
async function saveKeys(commitMsg = 'Update keys via bot') {
  try {
    const content = JSON.stringify(keys, null, 2);

    const formData = new URLSearchParams();
    formData.append('api_dev_key', PASTEBIN_DEV_KEY);
    formData.append('api_option', 'paste');
    formData.append('api_paste_code', content);
    formData.append('api_paste_private', '1');      // unlisted
    formData.append('api_paste_name', 'Federal Keys');
    formData.append('api_paste_expire_date', 'N');  // never expire
    formData.append('api_paste_format', 'json');

    // To overwrite existing paste, add these two lines
    formData.append('api_paste_key', PASTEBIN_PASTE_ID);  // <-- key to edit existing paste

    const res = await fetch('https://pastebin.com/api/api_post.php', {
      method: 'POST',
      body: formData,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    const result = await res.text();

    if (result.startsWith('Bad API request') || result.startsWith('Invalid')) {
      throw new Error(result);
    }

    console.log('Successfully overwrote Pastebin paste:', PASTEBIN_PASTE_ID);
  } catch (err) {
    console.error('Pastebin save error:', err.message);
  }
}

client.once('ready', async () => {
  console.log(`Bot online: ${client.user.tag}`);
  await loadKeys();

  const guild = client.guilds.cache.get(YOUR_SERVER_ID);
  if (guild) {
    const genCmd = new SlashCommandBuilder()
      .setName('genkey')
      .setDescription('Generate a key')
      .addIntegerOption(opt => opt.setName('uses').setDescription('Max uses (blank = unlimited)').setRequired(false).setMinValue(1))
      .addIntegerOption(opt => opt.setName('hours').setDescription('Hours until expiry (blank = never)').setRequired(false).setMinValue(1));

    const deactCmd = new SlashCommandBuilder()
      .setName('deactivate-key')
      .setDescription('Deactivate a key')
      .addStringOption(opt => opt.setName('key').setDescription('The key to deactivate').setRequired(true));

    const listCmd = new SlashCommandBuilder()
      .setName('list-keys')
      .setDescription('List all active keys');

    await guild.commands.set([
      genCmd.toJSON(),
      deactCmd.toJSON(),
      listCmd.toJSON()
    ]);
    console.log('Commands registered in your server');
  } else {
    console.log('Guild not found');
  }
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;

  if (interaction.user.id !== OWNER_ID) {
    return interaction.reply({ content: 'Only the bot owner can use these commands.', ephemeral: true });
  }

  if (interaction.commandName === 'genkey') {
    const maxUses = interaction.options.getInteger('uses');
    const hours = interaction.options.getInteger('hours');

    const part1 = Math.random().toString(36).slice(2, 7).toUpperCase();
    const part2 = Math.random().toString(36).slice(2, 7).toUpperCase();
    const key = `FED-${part1}-${part2}`;

    let expires = null;
    if (hours) expires = Date.now() + (hours * 60 * 60 * 1000);

    keys[key] = {
      active: true,
      remainingUses: maxUses || null,
      expires: expires,
      generatedAt: Date.now(),
      generatedBy: interaction.user.tag
    };

    await saveKeys(`Generated new key: ${key}`);

    let msg = `**Key generated & saved to Pastebin:**\n\`\`\`${key}\`\`\``;
    msg += `\nUses: ${maxUses ? maxUses : 'unlimited'}`;
    msg += `\nExpires: ${hours ? `in ${hours} hours` : 'never'}`;

    await interaction.reply({ content: msg, ephemeral: true });
  }

  else if (interaction.commandName === 'deactivate-key') {
    const keyToDeact = interaction.options.getString('key').trim().toUpperCase();

    if (keys[keyToDeact]) {
      keys[keyToDeact].active = false;
      await saveKeys(`Deactivated key: ${keyToDeact}`);
      await interaction.reply({ content: `Key **${keyToDeact}** deactivated and updated on Pastebin.`, ephemeral: true });
    } else {
      await interaction.reply({ content: `Key **${keyToDeact}** not found.`, ephemeral: true });
    }
  }

  else if (interaction.commandName === 'list-keys') {
    if (Object.keys(keys).length === 0) {
      return interaction.reply({ content: 'No active keys yet.', ephemeral: true });
    }

    let msg = '**Active Keys:**\n\n';
    for (const [key, info] of Object.entries(keys)) {
      if (!info.active) continue;
      msg += `**${key}**\n`;
      msg += `Uses left: ${info.remainingUses !== null ? info.remainingUses : 'unlimited'}\n`;
      msg += `Expires: ${info.expires ? new Date(info.expires).toLocaleString() : 'never'}\n`;
      msg += `Generated by: ${info.generatedBy}\n\n`;
    }

    await interaction.reply({ content: msg, ephemeral: true });
  }
});

client.login(TOKEN);

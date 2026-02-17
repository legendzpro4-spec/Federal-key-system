const { Client, GatewayIntentBits, SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const fs = require('fs');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

const TOKEN = process.env.DISCORD_TOKEN;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = 'legendzpro4-spec';
const REPO_NAME = 'Federal-key-system';
const FILE_PATH = 'active_keys.json';

const OWNER_ID = '1424707396395339776';
const YOUR_SERVER_ID = '1448399752201900045';

// Health check server (prevents Railway hang)
const http = require('http');
const PORT = process.env.PORT || 8080;
http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Bot is alive');
}).listen(PORT);
console.log(`Health check server listening on port ${PORT}`);

// Dynamic import for Octokit (fixes ERR_REQUIRE_ESM crash)
let Octokit;
let octokit;

(async () => {
  const module = await import("@octokit/rest");
  Octokit = module.Octokit;
  octokit = new Octokit({ auth: GITHUB_TOKEN });
  console.log('Octokit loaded successfully');
})();

let keys = {};

// Load keys from GitHub
async function loadKeys() {
  if (!octokit) {
    console.log('Waiting for Octokit to load...');
    await new Promise(resolve => setTimeout(resolve, 2000)); // simple wait - improve if needed
  }
  try {
    const { data } = await octokit.repos.getContent({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path: FILE_PATH
    });
    const content = Buffer.from(data.content, 'base64').toString();
    keys = JSON.parse(content);
    console.log('Loaded keys from GitHub');
  } catch (err) {
    console.log('No keys file or error:', err.message);
    keys = {};
  }
}

// Save keys to GitHub
async function saveKeys(commitMsg = 'Update active keys via bot') {
  if (!octokit) return console.log('Octokit not ready - skipping save');
  const content = Buffer.from(JSON.stringify(keys, null, 2)).toString('base64');
  
  let sha = null;
  try {
    const { data } = await octokit.repos.getContent({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path: FILE_PATH
    });
    sha = data.sha;
  } catch {}

  await octokit.repos.createOrUpdateFileContents({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    path: FILE_PATH,
    message: commitMsg,
    content: content,
    sha: sha || undefined,
    branch: 'main'
  });
  console.log('Committed keys to GitHub');
}

client.once('ready', async () => {
  console.log(`Bot online: ${client.user.tag}`);
  await loadKeys();

  // Guild-specific registration (instant)
  const guild = client.guilds.cache.get(YOUR_SERVER_ID);
  if (guild) {
    const genCmd = new SlashCommandBuilder()
      .setName('genkey')
      .setDescription('Generate a key with custom uses & expiration')
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
    console.log('Commands registered INSTANTLY in your server');
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

    let msg = `**Key generated & committed to GitHub:**\n\`\`\`${key}\`\`\``;
    msg += `\nUses: ${maxUses ? maxUses : 'unlimited'}`;
    msg += `\nExpires: ${hours ? `in ${hours} hours` : 'never'}`;

    await interaction.reply({ content: msg, ephemeral: true });
  }

  else if (interaction.commandName === 'deactivate-key') {
    const keyToDeact = interaction.options.getString('key').trim().toUpperCase();

    if (keys[keyToDeact]) {
      keys[keyToDeact].active = false;
      await saveKeys(`Deactivated key: ${keyToDeact}`);
      await interaction.reply({ content: `Key **${keyToDeact}** deactivated and updated on GitHub.`, ephemeral: true });
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

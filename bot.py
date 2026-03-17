import discord
import requests
import json
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    data = load_accounts()

    # LOGIN
    if message.content.startswith("!login"):
        try:
            token = message.content.split(" ")[1]

            r = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"}
            )

            username = r.json()["login"]

            data["accounts"][username] = token
            data["current"] = username

            save_accounts(data)

            await message.channel.send(f"Logged in as {username}")

        except:
            await message.channel.send("Invalid GitHub token")

    # ACCOUNT
    if message.content == "!account":

        token = get_current_token()

        if not token:
            await message.channel.send("No account logged in")
            return

        r = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}"}
        )

        await message.channel.send(f"Current account: {r.json()['login']}")

    # LOGOUT
    if message.content == "!logout":

        data["current"] = None
        save_accounts(data)

        await message.channel.send("Logged out")

    # FORK REPO
    if message.content == "!fork":

        token = get_current_token()

        if not token:
            await message.channel.send("Login first")
            return

        requests.post(
            "https://api.github.com/repos/BJaneman/WIN11/forks",
            headers={"Authorization": f"token {token}"}
        )

        await message.channel.send("Fork created")

    # RUN WORKFLOW
    if message.content == "!work":

        token = get_current_token()

        if not token:
            await message.channel.send("Login first")
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

        await message.channel.send("Workflow started")

bot.run(DISCORD_TOKEN)

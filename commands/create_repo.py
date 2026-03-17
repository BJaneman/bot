from discord.ext import commands
import requests
import os

async def create_repo(ctx, repo_name):
    token = os.getenv("MY_GITHUB_TOKEN")
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    data = {"name": repo_name, "private": False}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        await ctx.send(f"✅ Repository `{repo_name}` created successfully!")
    elif response.status_code == 422:
        await ctx.send(f"⚠ Repository `{repo_name}` already exists.")
    else:
        await ctx.send(f"❌ Failed to create repository. Status code: {response.status_code}")
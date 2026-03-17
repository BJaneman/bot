from discord.ext import commands
import requests
import os
import base64

async def create_file(ctx, repo_name, file_path, file_content):
    token = os.getenv("MY_GITHUB_TOKEN")

    # Get username dynamically
    user_resp = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
    if user_resp.status_code != 200:
        await ctx.send("❌ Failed to get GitHub username from token")
        return
    username = user_resp.json()["login"]

    # GitHub API URL for creating file
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    data = {
        "message": f"Add {file_path}",
        "content": base64.b64encode(file_content.encode()).decode()
    }

    response = requests.put(url, json=data, headers=headers)

    if response.status_code in [201, 200]:
        await ctx.send(f"✅ File `{file_path}` created/updated in `{repo_name}`.")
    else:
        await ctx.send(f"❌ Failed to create file. Status code: {response.status_code}\n{response.text}")
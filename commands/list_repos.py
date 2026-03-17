import os
import requests

async def list_repos(ctx):
    """
    Lists all repositories the authenticated user has access to.
    Shows them numbered with optional description.
    """
    token = os.getenv("MY_GITHUB_TOKEN")

    # Get username dynamically
    user_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    if user_resp.status_code != 200:
        await ctx.send("❌ Failed to get GitHub username from token")
        return
    username = user_resp.json()["login"]

    # List all repos
    repos_url = "https://api.github.com/user/repos?per_page=100"
    repo_resp = requests.get(repos_url, headers={"Authorization": f"token {token}"})
    if repo_resp.status_code != 200:
        await ctx.send(f"❌ Failed to list repositories. Status code: {repo_resp.status_code}")
        return

    repos = repo_resp.json()
    if not repos:
        await ctx.send("⚠ You have no repositories accessible by this token.")
        return

    # Build message
    message = ""
    for i, repo in enumerate(repos, start=1):
        name = repo["name"]
        description = repo["description"] or "No description"
        private = "🔒" if repo["private"] else "🌐"
        message += f"{i}. {name} {private} — {description}\n"

    await ctx.send(message)
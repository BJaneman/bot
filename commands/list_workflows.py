from discord.ext import commands
import requests
import os

async def list_workflows(ctx):
    """
    Lists all workflows from all repositories the token has access to,
    showing status with emojis:
    🟢 = running, ⚪ = not running
    """

    token = os.getenv("MY_GITHUB_TOKEN")

    # Step 1: Get username dynamically
    user_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    if user_resp.status_code != 200:
        await ctx.send("❌ Failed to get GitHub username from token")
        return
    username = user_resp.json()["login"]

    # Step 2: List all repos user has access to
    repos_url = "https://api.github.com/user/repos?per_page=100"
    repo_resp = requests.get(repos_url, headers={"Authorization": f"token {token}"})
    if repo_resp.status_code != 200:
        await ctx.send(f"❌ Failed to list repositories. Status code: {repo_resp.status_code}")
        return

    repos = repo_resp.json()

    # Step 3: Collect workflows and statuses
    message = ""
    for repo in repos:
        repo_name = repo["name"]
        workflows_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/workflows"
        wf_resp = requests.get(workflows_url, headers={"Authorization": f"token {token}"})
        if wf_resp.status_code != 200:
            continue

        workflows = wf_resp.json().get("workflows", [])
        if not workflows:
            continue

        message += f"**{repo_name}**\n"
        for wf in workflows:
            wf_name = wf["name"]
            wf_id = wf["id"]

            # Step 4: Check latest workflow run
            runs_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/workflows/{wf_id}/runs?per_page=1"
            runs_resp = requests.get(runs_url, headers={"Authorization": f"token {token}"})
            if runs_resp.status_code == 200 and runs_resp.json().get("total_count", 0) > 0:
                latest_run = runs_resp.json()["workflow_runs"][0]
                status = latest_run["status"]  # "completed" or "in_progress"
                emoji = "🟢" if status == "in_progress" else "⚪"
            else:
                emoji = "⚪"  # No runs yet

            message += f"{emoji} {wf_name} — ID: {wf_id}\n"

        message += "\n"

    if message == "":
        await ctx.send("⚠ No workflows found in your repositories.")
    else:
        await ctx.send(message)
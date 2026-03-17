import os
import requests
import zipfile
import io
import discord

async def get_logs(ctx, repo_name, workflow_id):
    token = os.getenv("MY_GITHUB_TOKEN")

    # Get username
    user_resp = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
    if user_resp.status_code != 200:
        await ctx.send("❌ Failed to get GitHub username from token")
        return
    username = user_resp.json()["login"]

    # Get latest workflow run
    runs_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/workflows/{workflow_id}/runs?per_page=1"
    runs_resp = requests.get(runs_url, headers={"Authorization": f"token {token}"})
    if runs_resp.status_code != 200 or runs_resp.json().get("total_count", 0) == 0:
        await ctx.send("❌ No workflow runs found for this workflow ID.")
        return

    latest_run = runs_resp.json()["workflow_runs"][0]
    run_id = latest_run["id"]

    # Download logs ZIP
    logs_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/runs/{run_id}/logs"
    logs_resp = requests.get(logs_url, headers={"Authorization": f"token {token}"}, stream=True)
    if logs_resp.status_code != 200:
        await ctx.send(f"❌ Failed to fetch logs. Status code: {logs_resp.status_code}")
        return

    zip_file = zipfile.ZipFile(io.BytesIO(logs_resp.content))
    combined_logs = ""

    for file_name in zip_file.namelist():
        with zip_file.open(file_name) as f:
            file_content = f.read().decode(errors="ignore")
            combined_logs += f"\n\n===== {file_name} =====\n\n{file_content}"

    log_bytes = io.BytesIO(combined_logs.encode())
    log_file = discord.File(fp=log_bytes, filename=f"{repo_name}_{workflow_id}_logs.txt")
    await ctx.send(file=log_file)
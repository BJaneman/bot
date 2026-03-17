import requests
import os

async def stop_workflow(ctx, repo_name, workflow_id):
    """
    Stop the latest run of a workflow in any repository the token has access to.
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

    # Get latest run of the workflow
    runs_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/workflows/{workflow_id}/runs?per_page=1"
    runs_resp = requests.get(runs_url, headers={"Authorization": f"token {token}"})
    if runs_resp.status_code != 200 or runs_resp.json().get("total_count", 0) == 0:
        await ctx.send("❌ No workflow runs found to cancel.")
        return

    latest_run = runs_resp.json()["workflow_runs"][0]
    run_id = latest_run["id"]

    # Cancel the run
    cancel_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/runs/{run_id}/cancel"
    cancel_resp = requests.post(cancel_url, headers={"Authorization": f"token {token}"})
    if cancel_resp.status_code == 202:
        await ctx.send(f"🛑 Workflow `{workflow_id}` run canceled successfully!")
    else:
        await ctx.send(f"❌ Failed to cancel workflow. Status code: {cancel_resp.status_code}")
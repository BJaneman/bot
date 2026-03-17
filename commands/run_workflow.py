import requests
import os

async def run_workflow(ctx, repo_name, workflow_identifier):
    """
    Trigger a workflow using either:
    - workflow file name (test_bot.yml)
    - workflow numeric ID (244675011)
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

    # Step 1: Determine if identifier is numeric (ID) or string (filename)
    if workflow_identifier.isdigit():
        workflow_id = workflow_identifier
    else:
        # If filename, get workflow ID first
        wf_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/workflows"
        wf_resp = requests.get(wf_url, headers={"Authorization": f"token {token}"})
        if wf_resp.status_code != 200:
            await ctx.send(f"❌ Failed to list workflows in repo `{repo_name}`")
            return

        workflows = wf_resp.json().get("workflows", [])
        wf_match = next((wf for wf in workflows if wf["name"] == workflow_identifier or wf["path"].endswith(workflow_identifier)), None)
        if not wf_match:
            await ctx.send(f"❌ Workflow `{workflow_identifier}` not found in repo `{repo_name}`")
            return
        workflow_id = str(wf_match["id"])

    # Step 2: Trigger workflow via workflow_dispatch
    dispatch_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
    payload = {"ref": "main"}  # Change branch if needed
    headers = {"Authorization": f"token {token}"}

    resp = requests.post(dispatch_url, json=payload, headers=headers)
    if resp.status_code == 204:
        await ctx.send(f"✅ Workflow `{workflow_identifier}` triggered successfully!")
    else:
        await ctx.send(f"❌ Failed to trigger workflow. Status code: {resp.status_code}\n{resp.text}")
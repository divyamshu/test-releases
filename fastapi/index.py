from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv, dotenv_values
from readfile import GitHubFileReader
import requests
import base64
from typing import Optional
from io import StringIO

# Load environment variables from .env file
load_dotenv()

# Enable fastAPI app
app = FastAPI()

# Configuration from environment variables
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL")
# Specific Repository Configuration
GITHUB_OWNER=os.getenv("GITHUB_OWNER")
GITHUB_REPO=os.getenv("GITHUB_REPO")
GITHUB_FILE_PATH=os.getenv("GITHUB_FILE_PATH")
# FastAPI Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
EXPECTED_ENV_KEYS = os.getenv("EXPECTED_ENV_KEYS").split(",")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the payload was sent from GitHub by validating SHA256 signature."""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events.
    
    GitHub sends the event type in the X-GitHub-Event header.
    Common events: push, pull_request, issues, release, etc.
    """
    
    # Get the raw request body for signature verification
    payload_body = await request.body()
    
    # Check if body is empty
    if not payload_body:
        return {"message": "Empty payload received", "event": x_github_event}
    
    # Verify the webhook signature (recommended for security)
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse the JSON payload from the body we already read
    try:
        payload = json.loads(payload_body.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # Handle ping event (sent when webhook is first created)
    if x_github_event == "ping":
        return {
            "message": "Webhook received successfully!",
            "zen": payload.get("zen"),
            "hook_id": payload.get("hook_id")
        }
    
    #Handle different event types
    if x_github_event == "release":
        return handle_release_event(payload)
    elif x_github_event == "push":
        return handle_push_event(payload)
    elif x_github_event == "pull_request":
        return handle_pull_request_event(payload)
    elif x_github_event == "issues":
        return handle_issues_event(payload)
    else:
        return {"message": f"Event {x_github_event} received but not handled"}

def handle_release_event(payload: dict):
    """Handle release events."""
    action = payload.get("action")  # published, unpublished, created, edited, deleted, prereleased, released
    release = payload.get("release", {})
    repository = payload.get("repository", {}).get("full_name")
    
    # Extract release information
    tag_name = release.get("tag_name")
    release_name = release.get("name")
    release_body = release.get("body")  # Release notes
    is_prerelease = release.get("prerelease", False)
    is_draft = release.get("draft", False)
    author = release.get("author", {}).get("login")
    html_url = release.get("html_url")
    published_at = release.get("published_at")
    
    print(f"Release {action} in {repository}")
    print(f"Tag: {tag_name}")
    print(f"Name: {release_name}")
    print(f"Author: {author}")
    print(f"URL: {html_url}")
    print(f"Prerelease: {is_prerelease}")
    print(f"Draft: {is_draft}")
    
    # Handle specific actions
    if action == "published":
        print(f"New release published: {tag_name}")
        print(f"Release notes: {release_body}")
        reader = GitHubFileReader(token=GITHUB_API_TOKEN)

        # Read a file
        file = reader.get_file_content(GITHUB_OWNER, GITHUB_REPO, GITHUB_FILE_PATH, tag_name)
        get_environment_variables(file["content"])
        
    elif action == "created":
        print(f"Release created: {tag_name}")
        # This happens when a release is created but not yet published
        
    elif action == "edited":
        print(f"Release edited: {tag_name}")
        
    elif action == "deleted":
        print(f"Release deleted: {tag_name}")
    
    return {
        "status": "success",
        "message": f"Processed release event: {action}",
        "release": {
            "tag": tag_name,
            "name": release_name,
            "action": action,
            "url": html_url
        }
    }


def get_environment_variables(env_contents: str):
    # Load all key-value pairs into a dictionary
    env_vars = dotenv_values(stream=StringIO(env_contents))

    # Print all keys and values
    missing = [key for key in EXPECTED_ENV_KEYS if key not in env_vars]
    if not missing:
        for key, value in env_vars.items():
            print(f"{key} = {value}")
    else:
        print("Missing:", missing)


@app.get("/")
async def root():
    return {"message": "GitHub Webhook Server is running"}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {HOST}:{PORT}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Webhook secret configured: {'Yes' if WEBHOOK_SECRET else 'No'}")
    uvicorn.run(app, host=HOST, port=PORT)
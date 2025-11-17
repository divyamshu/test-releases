from imports import Optional, FastAPI, Request, HTTPException, Header, os, json, hmac, hashlib, base64, requests
from config import WEBHOOK_SECRET, GITHUB_API_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_FILE_PATH
from GitHubFileHandler import GitHubFileReader
from LogicalHandler import get_environment_variables

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    # """Verify that the payload was sent from GitHub by validating SHA256 signature."""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def handle_release_event(payload: dict):
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
               
    return {
        "status": "success",
        "action": action,
        "message": f"Processed release event: {action}",
        "release": {
            "tag": tag_name,
            "name": release_name,
            "action": action,
            "url": html_url
        }
    }


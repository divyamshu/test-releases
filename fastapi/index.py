from imports import Optional, FastAPI, Request, HTTPException, Header, json
from config import WEBHOOK_SECRET, HOST, PORT, ENVIRONMENT, GITHUB_API_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_FILE_PATH
from GitHubWebhookHandler import verify_signature, handle_release_event
from LogicalHandler import get_environment_variables, get_previous_tag
from GitHubFileHandler import GitHubFileReader
from GitTagManager import GitHubTagManager

# Enable fastAPI app
app = FastAPI()

@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    # Get the raw request body for signature verification
    payload_body = await request.body()
    
    # Check if body is empty
    if not payload_body:
        return {"message": "Empty payload received", "event": x_github_event}
    
    # Verify the webhook signature 
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse the JSON payload from the body we already read
    try:
        payload = json.loads(payload_body.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    #Handle different event types
    if x_github_event == "release":
        print(get_differences(payload))
        return True
    else:
        return {"message": f"Event {x_github_event} received but not handled"}

def get_differences(payload):
    latest_event = handle_release_event(payload)
    if latest_event["status"] == "success" and latest_event["action"] == "published":
        latest_tag_name = latest_event["release"]["tag"]
        reader = GitHubFileReader(token=GITHUB_API_TOKEN)
        tag_manager = GitHubTagManager(token=GITHUB_API_TOKEN)
        # Get the previous release tag
        previous_tag = (get_previous_tag(tag_manager.list_all_tags(GITHUB_OWNER, GITHUB_REPO), latest_tag_name))

        # Read Latest Release File Content
        latest_file = reader.get_file_content(GITHUB_OWNER, GITHUB_REPO, GITHUB_FILE_PATH, latest_tag_name)
        latest_value = get_environment_variables(latest_file["content"])

        # Previous Release File Content
        previous_file = reader.get_file_content(GITHUB_OWNER, GITHUB_REPO, GITHUB_FILE_PATH, previous_tag)
        previous_value = get_environment_variables(previous_file["content"])

        # Determine differences based on EXPECTED_ENV_KEYS
        if(previous_value == latest_value):
            print("No changes detected between releases.")
            return True
        else:
            print(f"Changes detected between releases: {previous_value} -> {latest_value}")
            return False


@app.get("/")
async def root():
    return {"message": "GitHub Webhook Server is running"}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {HOST}:{PORT}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Webhook secret configured: {'Yes' if WEBHOOK_SECRET else 'No'}")
    uvicorn.run(app, host=HOST, port=PORT)




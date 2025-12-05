# GitHub Release Webhook Processor

A FastAPI application that listens to GitHub release webhooks and automatically compares environment variable configurations between different release versions using GitHub tags.

## Overview

This application provides a webhook endpoint that receives GitHub release events, verifies their authenticity, and processes release information to track changes in environment variables across different releases.

## Features

- **GitHub Webhook Verification**: Validates incoming webhooks using SHA256 HMAC signatures
- **Release Event Processing**: Handles GitHub release events (published, unpublished, edited, etc.)
- **Version Comparison**: Automatically compares environment configurations between current and previous releases
- **Environment Variable Tracking**: Extracts and monitors specific environment variables from repository files
- **Git Tag Management**: Retrieves and manages GitHub release tags

## Project Structure

```
📂 fastapi/
    ├── index.py                # Main FastAPI application and webhook endpoint
    ├── config.py               # Configuration management from environment variables
    ├── GitHubWebhookHandler.py # Webhook signature verification and event handling
    ├── GitHubFileHandler.py    # GitHub API integration for file retrieval
    ├── GitTagManager.py        # Git tag and release management
    ├── LogicalHandler.py       # Business logic for environment variable processing
    ├── imports.py              # Centralized imports
    ├── requirements.txt        # Python dependencies
    ├── .env                    # Environment configuration (local)
    └── testtf.env              # Test environment file

```
## Installation

### Prerequisites
- Python 3.12+
- pip package manager

### Setup

#### Install dependencies
```
pip install -r requirements.txt
```

#### Configuration

Set the following environment variables in your `.env` file or Environment Variables of your system:

```
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_API_TOKEN=your_github_personal_access_token
GITHUB_API_BASE_URL=https://api.github.com
GITHUB_OWNER=your_github_username_or_org
GITHUB_REPO=your_repository_name
GITHUB_FILE_PATH=path/to/.env.example
EXPECTED_ENV_KEYS=KEY_NAME
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```
#### Configuration Variables

Variable	            | Description	                            | Default
------------------------|-------------------------------------------|----------
GITHUB_WEBHOOK_SECRET	| Secret for webhook signature verification	| Required
GITHUB_API_TOKEN	    | GitHub personal access token	            | Required
GITHUB_OWNER	        | GitHub username or organization	        | Required
GITHUB_REPO	            | Repository name	                        | Required
GITHUB_FILE_PATH	    | Path to the tfvars file in the repo	    | Required
EXPECTED_ENV_KEYS	    | Environment key(s) to track	            | Required
HOST	                | Server host	                            | 0.0.0.0
PORT	                | Server port	                            | 8000
ENVIRONMENT	            | Environment type	                        | development

### Usage

#### Running the Server
```
uvicorn index:app --host 0.0.0.0 --port 8000 --reload
```
#### Webhook Endpoint
```
POST /webhook/github
```

## Core Modules

### index.py

Main FastAPI application with the webhook endpoint. Orchestrates webhook handling and file comparison.

### GitHubWebhookHandler.py
- **verify_signature()**: Validates webhook authenticity using HMAC-SHA256
- **handle_release_event()**: Extracts and structures release event data

### GitHubFileHandler.py

- **GitHubFileReader** class that:

  - Authenticates with GitHub API
  - Retrieves file contents from repositories
  - Decodes base64-encoded content
  - Returns file metadata

### GitTagManager.py
Manages Git tags and release information from GitHub API.

### LogicalHandler.py
- **get_environment_variables()**: Extracts environment variables from file content

- **get_previous_tag()**: Identifies the previous release tag for comparison

### config.py
Centralized configuration management using python-dotenv for environment variable loading.

### imports.py
Centralized import statements for all required modules and dependencies.

Dependencies
- fastapi: Web framework for building APIs
- uvicorn: ASGI server to run FastAPI
- requests: HTTP library for GitHub API calls
- python-dotenv: Environment variable management

## Supported GitHub Events
Currently handles release events with various actions:
- published
- unpublished
- created
- edited
- deleted
- prereleased
- released

## Security Considerations
Webhook signatures are validated using HMAC-SHA256 to ensure requests originate from GitHub
GitHub API token should be kept secure and never committed to version control
Use environment variables or secrets management for sensitive credentials
Validate all incoming payload data

## Troubleshooting
### Webhook Not Triggering
- Verify webhook is configured in GitHub repository settings
- Check that the GITHUB_WEBHOOK_SECRET matches GitHub configuration
- Ensure the server is accessible from the internet (for production)
- Check server logs for signature validation errors

### File Not Found
- Verify GITHUB_FILE_PATH is correct
- Ensure the file exists in the specified branch (default: main)
- Check that GITHUB_API_TOKEN has read permissions

### Missing Environment Variables
- Verify EXPECTED_ENV_KEYS is set correctly
- Check that the target file contains the expected variable
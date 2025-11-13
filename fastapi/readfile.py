import requests
import base64
from typing import Optional

class GitHubFileReader:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub Personal Access Token (optional for public repos)
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def get_file_content(self, owner: str, repo: str, file_path: str, 
                        branch: str = "main") -> dict:
        """
        Get file content from a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            file_path: Path to the file in the repository
            branch: Branch name (default: main)
            
        Returns:
            Dictionary with file content and metadata
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": branch}
        print(url)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Decode base64 content
        if data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8")
        else:
            content = data.get("content", "")
        
        return {
            "content": content,
            "name": data.get("name"),
            "path": data.get("path"),
            "sha": data.get("sha"),
            "size": data.get("size"),
            "url": data.get("html_url"),
            "download_url": data.get("download_url")
        }
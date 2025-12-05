from imports import Optional, json, requests, base64
from LogicalHandler import get_environment_variables
from config import GITHUB_API_BASE_URL

class GitHubFileReader:
    def __init__(self, token: Optional[str] = None):
        self.base_url = GITHUB_API_BASE_URL
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def get_file_content(self, owner: str, repo: str, file_path: str, branch: str = "main") -> dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": branch}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Decode base64 content
        if data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8")
        else:
            content = data.get("content", "")
        
        print(get_environment_variables(content))
        return {
            "content": content,
            "name": data.get("name"),
            "path": data.get("path"),
            "sha": data.get("sha"),
            "size": data.get("size"),
            "url": data.get("html_url"),
            "download_url": data.get("download_url")
        }
    
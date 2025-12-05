from imports import requests, os, Optional, Dict
from config import WEBHOOK_SECRET, GITHUB_API_BASE_URL, GITHUB_API_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_FILE_PATH, HOST, PORT, ENVIRONMENT

class GitHubTagManager:
    def __init__(self, token: Optional[str] = None):
        self.base_url = GITHUB_API_BASE_URL
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def get_commit_by_tag(self, owner: str, repo: str, tag: str) -> Dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/git/ref/tags/{tag}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Get the object (could be commit or tag object)
        object_sha = data["object"]["sha"]
        object_type = data["object"]["type"]
        
        # If it's an annotated tag, we need to fetch the tag object to get the commit
        if object_type == "tag":
            tag_url = data["object"]["url"]
            tag_response = requests.get(tag_url, headers=self.headers)
            tag_response.raise_for_status()
            tag_data = tag_response.json()
            
            commit_sha = tag_data["object"]["sha"]
            commit_url = tag_data["object"]["url"]
        else:
            # It's a lightweight tag pointing directly to a commit
            commit_sha = object_sha
            commit_url = data["object"]["url"]
        
        # Fetch commit details
        commit_response = requests.get(commit_url, headers=self.headers)
        commit_response.raise_for_status()
        commit_data = commit_response.json()
        
        return {
            "tag": tag,
            "commit_sha": commit_sha,
            "commit_short_sha": commit_sha[:7],
            "commit_message": commit_data.get("message", ""),
            "commit_author": commit_data.get("author", {}).get("name", ""),
            "commit_date": commit_data.get("author", {}).get("date", ""),
            "commit_url": commit_data.get("html_url", ""),
            "tree_sha": commit_data.get("tree", {}).get("sha", "")
        }
    
    def get_commit_by_release_tag(self, owner: str, repo: str, tag: str) -> Dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/releases/tags/{tag}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "tag": tag,
            "commit_sha": data.get("target_commitish", ""),
            "release_name": data.get("name", ""),
            "release_body": data.get("body", ""),
            "published_at": data.get("published_at", ""),
            "author": data.get("author", {}).get("login", ""),
            "release_url": data.get("html_url", "")
        }
    
    def list_all_tags(self, owner: str, repo: str) -> list:
        url = f"{self.base_url}/repos/{owner}/{repo}/tags"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        tags = response.json()
        
        return [
            {
                "tag_name": tag.get("name"),
                "commit_sha": tag.get("commit", {}).get("sha"),
                "commit_short_sha": tag.get("commit", {}).get("sha", "")[:7],
                "commit_url": tag.get("commit", {}).get("url"),
                "zipball_url": tag.get("zipball_url"),
                "tarball_url": tag.get("tarball_url")
            }
            for tag in tags
        ]
    
    def get_latest_tag_commit(self, owner: str, repo: str) -> Dict:
        tags = self.list_all_tags(owner, repo)
        
        if not tags:
            raise ValueError("No tags found in repository")
        
        latest_tag = tags[0]  # Tags are sorted by date, newest first
        
        return {
            "latest_tag": latest_tag["tag_name"],
            "commit_sha": latest_tag["commit_sha"],
            "commit_short_sha": latest_tag["commit_short_sha"],
            "commit_url": latest_tag["commit_url"]
        }
    
    def compare_tags(self, owner: str, repo: str, base_tag: str, head_tag: str) -> Dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/compare/{base_tag}...{head_tag}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        
        commits = [
            {
                "sha": commit["sha"],
                "short_sha": commit["sha"][:7],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"]
            }
            for commit in data.get("commits", [])
        ]
        
        return {
            "base_tag": base_tag,
            "head_tag": head_tag,
            "total_commits": data.get("total_commits", 0),
            "ahead_by": data.get("ahead_by", 0),
            "behind_by": data.get("behind_by", 0),
            "status": data.get("status", ""),
            "commits": commits,
            "files_changed": len(data.get("files", [])),
            "compare_url": data.get("html_url", "")
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize the tag manager
    manager = GitHubTagManager()
    
    # Configuration - you can also use environment variables
    OWNER = os.getenv("GITHUB_OWNER", "torvalds")
    REPO = os.getenv("GITHUB_REPO", "linux")
    TAG = "0.1"
    
    print("=" * 70)
    print("GitHub Tag to Commit Resolver")
    print("=" * 70)
    
    # Example 1: Get commit by tag
    print(f"\n1. Getting commit for tag: {TAG}")
    print("-" * 70)
    try:
        commit_info = manager.get_commit_by_tag(OWNER, REPO, TAG)
        print(f"Tag: {commit_info['tag']}")
        print(f"Commit SHA: {commit_info['commit_sha']}")
        print(f"Short SHA: {commit_info['commit_short_sha']}")
        print(f"Author: {commit_info['commit_author']}")
        print(f"Date: {commit_info['commit_date']}")
        print(f"Message: {commit_info['commit_message'][:100]}...")
        print(f"URL: {commit_info['commit_url']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: List all tags
    print(f"\n2. Listing first 5 tags in {OWNER}/{REPO}")
    print("-" * 70)
    try:
        tags = manager.list_all_tags("facebook", "react")
        for tag in tags[:2]:
            print(f"  {tag['tag_name']:20} → {tag['commit_short_sha']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Get latest tag
    print(f"\n3. Getting latest tag")
    print("-" * 70)
    try:
        latest = manager.get_latest_tag_commit(OWNER, REPO)
        print(f"Latest Tag: {latest['latest_tag']}")
        print(f"Commit SHA: {latest['commit_sha']}")
        print(f"Short SHA: {latest['commit_short_sha']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Using with a repository that has releases
    print(f"\n4. Getting commit from release tag")
    print("-" * 70)
    try:
        # Example with a popular repo that has releases
        release_info = manager.get_commit_by_release_tag("facebook", "react", "v18.0.0")
        print(f"Release: {release_info['release_name']}")
        print(f"Tag: {release_info['tag']}")
        print(f"Commit: {release_info['commit_sha']}")
        print(f"Published: {release_info['published_at']}")
        print(f"Author: {release_info['author']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Compare two tags
    print(f"\n5. Comparing tags (if available)")
    print("-" * 70)
    try:
        comparison = manager.compare_tags("facebook", "react", "v17.0.0", "v18.0.0")
        print(f"Comparing: {comparison['base_tag']} → {comparison['head_tag']}")
        print(f"Total commits: {comparison['total_commits']}")
        print(f"Files changed: {comparison['files_changed']}")
        print(f"Status: {comparison['status']}")
        print(f"\nFirst 3 commits:")
        for commit in comparison['commits'][:3]:
            print(f"  {commit['short_sha']}: {commit['message'].split(chr(10))[0][:60]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 70)
import os
import json
import base64
import urllib.request
import urllib.error

# Set up environment variables to limit OpenBLAS threads to 1 (just in case)
os.environ["OPENBLAS_NUM_THREADS"] = "1"

def create_github_repo(username, token, repo_name):
    """
    Creates a new public repository on GitHub using the REST API.
    """
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": "A Data Cleaning & Visualization Project built in Python",
        "private": False,
        "auto_init": False
    }
    
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "Python-GitHub-AutoUploader")
    req.add_header("Content-Type", "application/json")
    
    data = json.dumps(payload).encode("utf-8")
    
    try:
        with urllib.request.urlopen(req, data=data) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            print(f"Successfully created repository: {res_data['html_url']}")
            return res_data["html_url"]
    except urllib.error.HTTPError as e:
        response_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(response_body)
            # If repo already exists, we can still push to it
            if "name already exists" in err_json.get("errors", [{}])[0].get("message", ""):
                repo_url = f"https://github.com/{username}/{repo_name}"
                print(f"Repository '{repo_name}' already exists at: {repo_url}")
                return repo_url
            print(f"API Error ({e.code}): {err_json.get('message')}")
        except Exception:
            print(f"Error ({e.code}): {response_body}")
        return None
    except Exception as e:
        print(f"Network error: {e}")
        return None

def upload_file_to_github(username, token, repo_name, local_path, github_path):
    """
    Uploads a single file to GitHub contents API.
    """
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{github_path}"
    
    try:
        with open(local_path, "rb") as f:
            content = f.read()
            
        # Encode file content to Base64
        base64_content = base64.b64encode(content).decode("utf-8")
        
        payload = {
            "message": f"Upload {github_path} via automatic pipeline",
            "content": base64_content
        }
        
        # Check if file already exists to get its SHA (required for updating)
        check_req = urllib.request.Request(url, method="GET")
        check_req.add_header("Authorization", f"token {token}")
        check_req.add_header("User-Agent", "Python-GitHub-AutoUploader")
        
        try:
            with urllib.request.urlopen(check_req) as res:
                file_info = json.loads(res.read().decode("utf-8"))
                payload["sha"] = file_info["sha"]
        except urllib.error.HTTPError as e:
            if e.code != 404: # If not found, it's a new file, which is fine
                raise
                
        # Send upload request
        req = urllib.request.Request(url, method="PUT")
        req.add_header("Authorization", f"token {token}")
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "Python-GitHub-AutoUploader")
        req.add_header("Content-Type", "application/json")
        
        data = json.dumps(payload).encode("utf-8")
        
        with urllib.request.urlopen(req, data=data) as res:
            return True
    except Exception as e:
        print(f"Failed to upload {github_path}: {e}")
        return False

def get_files_to_upload(base_dir):
    """
    Returns list of files to upload while respecting gitignore-like patterns manually.
    """
    files_to_upload = []
    # Directories/files to exclude
    ignored_dirs = {"__pycache__", ".ipynb_checkpoints", ".git", ".vscode", ".idea", "venv", ".venv"}
    
    for root, dirs, files in os.walk(base_dir):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        for file in files:
            # Skip python compiled files
            if file.endswith((".pyc", ".pyo", ".pyd")):
                continue
            
            full_path = os.path.join(root, file)
            # Make path relative to base_dir
            rel_path = os.path.relpath(full_path, base_dir)
            files_to_upload.append((full_path, rel_path.replace("\\", "/")))
            
    return files_to_upload

def main():
    print("========================================================================")
    # Get user credentials
    username = input("Enter your GitHub Username: ").strip()
    token = input("Enter your GitHub Personal Access Token (PAT): ").strip()
    
    if not username or not token:
        print("Error: Username and Personal Access Token are required.")
        return
        
    repo_name = "Data-Cleaning-Project"
    
    print(f"\n[1/3] Creating repository '{repo_name}' on GitHub...")
    repo_url = create_github_repo(username, token, repo_name)
    
    if not repo_url:
        print("Failed to initialize repository on GitHub. Please check your token and try again.")
        return
        
    print("\n[2/3] Scanning local files...")
    base_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = get_files_to_upload(base_project_dir)
    print(f"Found {len(files)} files to upload.")
    
    print("\n[3/3] Uploading files to GitHub...")
    success_count = 0
    for local_path, github_path in files:
        print(f"  Uploading {github_path}...", end="", flush=True)
        if upload_file_to_github(username, token, repo_name, local_path, github_path):
            print(" Done")
            success_count += 1
        else:
            print(" Failed")
            
    print("\n========================================================================")
    print(f"AUTOMATIC UPLOAD COMPLETE: {success_count}/{len(files)} files uploaded successfully!")
    print(f"Repository Link: {repo_url}")
    print("========================================================================")

if __name__ == "__main__":
    main()

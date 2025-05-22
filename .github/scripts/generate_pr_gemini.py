import os
import subprocess
import requests
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Get diff from this branch vs main
diff = subprocess.getoutput("git diff origin/main...HEAD")

# Ask Gemini to summarize the changes
model = genai.GenerativeModel("gemini-pro")
response = model.generate_content(f"Summarize this code diff:\n\n{diff}")
summary = response.text.strip()

# Get branch name and repo
branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
repo = os.getenv("GITHUB_REPOSITORY")
token = os.getenv("GITHUB_TOKEN")

# Create pull request payload
payload = {
    "title": f"[AI] Summary for {branch}",
    "head": branch,
    "base": "main",
    "body": summary,
}

# Make the GitHub API call
res = requests.post(
    f"https://api.github.com/repos/{repo}/pulls",
    headers={"Authorization": f"token {token}"},
    json=payload,
)

if res.status_code == 201:
    print("✅ Pull request created successfully!")
else:
    print("❌ Error creating PR:", res.status_code, res.text)

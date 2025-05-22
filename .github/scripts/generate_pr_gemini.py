# import os
# import subprocess
# import requests
# import google.generativeai as genai
#
# # Configure Gemini API key
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#
# # Get diff from this branch vs main
# diff = subprocess.getoutput("git diff origin/main...HEAD")
#
# # Ask Gemini to summarize the changes
# model = genai.GenerativeModel("gemini-2.0-flash")
# response = model.generate_content(f"Summarize this code diff:\n\n{diff}")
# summary = response.text.strip()
#
# # Get branch name and repo
# branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
# repo = os.getenv("GITHUB_REPOSITORY")
# token = os.getenv("GITHUB_TOKEN")
#
# # Create pull request payload
# payload = {
#     "title": f"[AI] Summary for {branch}",
#     "head": branch,
#     "base": "main",
#     "body": summary,
# }
#
# # Make the GitHub API call
# res = requests.post(
#     f"https://api.github.com/repos/{repo}/pulls",
#     headers={"Authorization": f"token {token}"},
#     json=payload,
# )
#
# if res.status_code == 201:
#     print("✅ Pull request created successfully!")
# else:
#     print("❌ Error creating PR:", res.status_code, res.text)

import os
import subprocess
from github import Github
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# Get changed files from git diff
files_changed = subprocess.check_output(["git", "diff", "--name-only", "origin/main...HEAD"]).decode("utf-8").strip().split("\n")

# Read the content of each changed file
code_blocks = []
for file in files_changed:
    if file.endswith(".py"):  # Or .js, .ts, .java, etc
        try:
            with open(file, "r") as f:
                content = f.read()
                code_blocks.append(f"### File: {file}\n{content}")
        except FileNotFoundError:
            continue

# Join and send to Gemini
combined_code = "\n\n".join(code_blocks)
prompt = f"""
You are a code reviewer. Analyze the following files.

1. Explain what the code is doing.
2. Detect if there are any obvious bugs, bad practices, or improvements.
3. Generate a pull request description.

Code:
{combined_code}
"""

response = model.generate_content(prompt)
summary = response.text

print("Generated Review:\n", summary)

# Create Pull Request
g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
head_branch = os.environ["GITHUB_REF"].split("/")[-1]

pr = repo.create_pull(
    title="AI-reviewed PR: " + head_branch,
    body=summary,
    head=head_branch,
    base="main"
)

print(f"✅ Pull Request created: {pr.html_url}")

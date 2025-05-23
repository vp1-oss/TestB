import os
import subprocess
from github import Github
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# Get changed files
files_changed = subprocess.check_output(
    ["git", "diff", "--name-only", "origin/main...HEAD"]
).decode("utf-8").strip().split("\n")

# Read and summarize each file
summaries = []

for file in files_changed:
    if not os.path.isfile(file):
        continue  # Skip deleted or non-existent files

    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    prompt = f"""
You are a code reviewer. Summarize the contents of the file below in 1–2 short sentences.

Respond in this format:
File: {file}
Summary: <your summary>

File content:
{content}
"""

    try:
        response = model.generate_content(prompt)
        summaries.append(response.text.strip())
    except Exception as e:
        summaries.append(f"File: {file}\nSummary: Failed to generate summary: {e}")

# Join all summaries
summary = "\n\n".join(summaries)

# Authenticate with GitHub
g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
head_branch = os.environ["GITHUB_REF"].split("/")[-1]

# Check if PR already exists
prs = repo.get_pulls(state='open', head=f"{repo.owner.login}:{head_branch}")
if prs.totalCount > 0:
    pr = prs[0]
    pr.edit(body=summary)
    print(f"✅ Updated existing PR: {pr.html_url}")
else:
    pr = repo.create_pull(
        title=f"AI-reviewed PR: {head_branch}",
        body=summary,
        head=head_branch,
        base="main"
    )
 print(f"✅ Created new PR: {pr.html_url}")


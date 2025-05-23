# import os
# import subprocess
# from github import Github
# import google.generativeai as genai
#
# # Configure Gemini
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# model = genai.GenerativeModel("gemini-2.0-flash")
#
# # Get changed files
# files_changed = subprocess.check_output(
#     ["git", "diff", "--name-only", "origin/main...HEAD"]
# ).decode("utf-8").strip().split("\n")
#
# # Read and summarize each file
# summaries = []
#
# for file in files_changed:
#     if not os.path.isfile(file):
#         continue  # Skip deleted or non-existent files
#
#     with open(file, "r", encoding="utf-8", errors="ignore") as f:
#         content = f.read()
#
#     prompt = f"""
# You are a code reviewer. Summarize the contents of the file below in 1–2 short sentences.
#
# Respond in this format:
# File: {file}
# Summary: <your summary>
#
# File content:
# {content}
# """
#
#     try:
#         response = model.generate_content(prompt)
#         summaries.append(response.text.strip())
#     except Exception as e:
#         summaries.append(f"File: {file}\nSummary: Failed to generate summary: {e}")
#
# # Join all summaries
# summary = "\n\n".join(summaries)
#
# # Authenticate with GitHub
# g = Github(os.environ["GITHUB_TOKEN"])
# repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
# head_branch = os.environ["GITHUB_REF"].split("/")[-1]
#
# # Check if PR already exists
# prs = repo.get_pulls(state='open', head=f"{repo.owner.login}:{head_branch}")
# if prs.totalCount > 0:
#     pr = prs[0]
#     pr.edit(body=summary)
#     print(f"✅ Updated existing PR: {pr.html_url}")
# else:
#     pr = repo.create_pull(
#         title=f"AI-reviewed PR: {head_branch}",
#         body=summary,
#         head=head_branch,
#         base="main"
#     )
#     print(f"✅ Created new PR: {pr.html_url}")
import os
import subprocess
import re
from github import Github
import google.generativeai as genai

# === Configure Gemini ===
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# === Utility: Detect file type ===
def detect_file_type(file):
    if file.endswith(".py"):
        return "Python"
    elif file.endswith(".go"):
        return "Go"
    elif file.endswith(".sh"):
        return "Shell"
    elif file.endswith(".json"):
        return "JSON"
    elif file.endswith(".xml"):
        return "XML"
    else:
        return "Other"

# === Utility: Add checks based on content ===
def get_review_suggestions(file, content):
    suggestions = []

    file_type = detect_file_type(file)

    if file_type in ["Python", "Go", "Shell"]:
        if "os.system" in content or "subprocess" in content:
            suggestions.append("⚠️ Consider secure subprocess usage.")
        if "print(" in content and file_type != "Shell":
            suggestions.append("🪵 Use structured logging instead of print.")
        if re.search(r"\bTODO\b", content, re.IGNORECASE):
            suggestions.append("📝 Found TODOs; ensure they're resolved.")

    if "docker" in content.lower() or "kubernetes" in content.lower():
        suggestions.append("🐳 Check containerization and deployment scripts.")

    if "log4j" in content.lower():
        suggestions.append("🚨 Use latest Log4j version to avoid vulnerabilities.")

    if "cassandra" in content.lower():
        suggestions.append("🗃️ Validate Cassandra schema and connection configs.")

    if file_type == "JSON":
        try:
            import json
            json.loads(content)
        except Exception:
            suggestions.append("❌ Invalid JSON structure.")

    # Architecture patterns
    if "http" in content.lower():
        if "frontend" in file.lower():
            suggestions.append("🎨 Check if frontend calls backend cleanly.")
        elif "backend" in file.lower():
            suggestions.append("🛠️ Validate backend APIs and DB access.")

    # Memory / coupling
    if "malloc" in content or "free" in content:
        suggestions.append("🧠 Manual memory management detected; ensure proper release.")
    if "import" in content and file_type in ["Python", "Go"]:
        if len(set(re.findall(r"import\s+(\w+)", content))) > 10:
            suggestions.append("🔗 High coupling detected; consider modular design.")

    return suggestions

# === Main: Collect changed files and generate summary + review ===
files_changed = subprocess.check_output(
    ["git", "diff", "--name-only", "origin/main...HEAD"]
).decode("utf-8").strip().split("\n")

summaries = []

for file in files_changed:
    if not os.path.isfile(file):
        continue

    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    review_points = get_review_suggestions(file, content)
    review_notes = "\n".join(review_points)

    prompt = f"""
You are a senior software engineer. Summarize the file and suggest improvements.

Respond in this format:
File: {file}
Summary: <summary>
Review Notes:
- <bullet points>

File content:
{content}
"""

    try:
        response = model.generate_content(prompt)
        ai_summary = response.text.strip()
        final_summary = f"{ai_summary}\n{review_notes if review_notes else ''}"
        summaries.append(final_summary)
    except Exception as e:
        summaries.append(f"File: {file}\nSummary: Failed to generate summary: {e}")

# === GitHub PR Summary Update/Create ===
summary = "\n\n".join(summaries)
g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
head_branch = os.environ["GITHUB_REF"].split("/")[-1]

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

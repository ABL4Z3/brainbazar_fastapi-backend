import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY")
_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={_API_KEY}"
)


# ──────────────────────────────────────────────
# Shared helper: builds the base project context
# ──────────────────────────────────────────────
def _build_project_context(project: dict) -> str:
    return (
        f"Project Title : {project['title']}\n"
        f"Difficulty    : {project['level']}\n"
        f"Summary       : {project['summary']}\n"
        f"Technologies  : {', '.join(project['technology'])}\n"
        f"Total Milestones: {len(project.get('milestones', []))}\n"
    )


def _call_gemini(prompt: str) -> str:
    if not _API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        error_msg = response.json().get("error", {}).get("message", str(e))
        raise ConnectionError(f"Gemini API request failed: {error_msg}") from e
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise ValueError(f"Unexpected Gemini API response: {response.text}") from e


# ──────────────────────────────────────────────
# 1. Project Overview
# ──────────────────────────────────────────────
def get_project_overview(project: dict) -> str:
    milestones_text = "\n".join(
        f"  Milestone {i+1} — {m['name']}: {m['description']}"
        for i, m in enumerate(project.get("milestones", []))
    )

    prompt = f"""
You are an expert coding mentor. A {project['level'].lower()} developer wants to build the following project.

{_build_project_context(project)}

Project Milestones:
{milestones_text}

Please provide a structured overview with these sections:

## What You Will Build
Describe the final product in simple terms.

## What You Will Learn
List the key skills and concepts the developer will gain.

## Prerequisites
What the user should already know before starting (keep it realistic for a {project['level'].lower()} level).

## Setup Checklist
All tools, software, and libraries to install before writing a single line of code.

## Project Roadmap
A brief one-line summary of each of the 5 milestones and how they connect.

Be encouraging, clear, and practical. Use markdown formatting.
""".strip()

    return _call_gemini(prompt)


# ──────────────────────────────────────────────
# 2. Milestone Step-by-Step Guide
# ──────────────────────────────────────────────
def get_milestone_guide(project: dict, milestone_number: int, milestone: dict) -> str:
    total = len(project.get("milestones", []))

    prompt = f"""
You are an expert coding mentor helping a {project['level'].lower()} developer build "{project['title']}" using {', '.join(project['technology'])}.

{_build_project_context(project)}

The user is currently on:
**Milestone {milestone_number} of {total}: {milestone['name']}**
Goal: {milestone['description']}

Provide a full step-by-step guide for this milestone with these sections:

## Overview
What this milestone achieves and why it matters.

## Step-by-Step Instructions
Numbered steps. Include code snippets (with language tags) where helpful. Be specific — assume the user has completed all previous milestones.

## How to Test This Milestone
Exactly how the user can verify everything is working before moving on.

## Common Mistakes to Avoid
Top 3 pitfalls specific to this milestone.

## ✅ Done Checklist
5 bullet points the user can tick off to confirm this milestone is complete.

Be detailed, patient, and use proper markdown with code blocks.
""".strip()

    return _call_gemini(prompt)


# ──────────────────────────────────────────────
# 3. Hint (nudge without spoiling)
# ──────────────────────────────────────────────
def get_milestone_hint(project: dict, milestone_number: int, milestone: dict) -> str:
    prompt = f"""
You are a coding mentor. A {project['level'].lower()} developer building "{project['title']}" is stuck on:

Milestone {milestone_number}: {milestone['name']}
Goal: {milestone['description']}

Give them ONE helpful hint that nudges them in the right direction WITHOUT giving away the full solution or writing the code for them.
Keep it to 2-3 sentences. Be encouraging and brief.
""".strip()

    return _call_gemini(prompt)


# ──────────────────────────────────────────────
# 4. Ask a Question (contextual Q&A)
# ──────────────────────────────────────────────
def ask_milestone_question(
    project: dict, milestone_number: int, milestone: dict, question: str
) -> str:
    prompt = f"""
You are an expert coding mentor. A {project['level'].lower()} developer is building "{project['title']}" using {', '.join(project['technology'])}.

They are on Milestone {milestone_number}: {milestone['name']}
Milestone goal: {milestone['description']}

Their question:
"{question}"

Answer their question clearly and specifically in the context of this project and this milestone.
- If relevant, include a code example with proper syntax highlighting.
- If the question is about an error, explain the cause and the fix.
- Stay focused — don't go beyond the scope of this milestone unless necessary.
""".strip()

    return _call_gemini(prompt)


# ──────────────────────────────────────────────
# 5. Milestone Completion Message
# ──────────────────────────────────────────────
def get_milestone_completion(project: dict, milestone_number: int, milestone: dict) -> str:
    total = len(project.get("milestones", []))
    is_last = milestone_number == total

    next_info = ""
    if not is_last:
        next_m = project["milestones"][milestone_number]  # 1-indexed → next item
        next_info = f"Next up — Milestone {milestone_number + 1}: {next_m['name']}\nGoal: {next_m['description']}"

    prompt = f"""
You are a coding mentor. A developer just completed Milestone {milestone_number} of {total} for "{project['title']}".

Completed: {milestone['name']}
What they did: {milestone['description']}

{"🎉 This was the FINAL milestone — the project is complete!" if is_last else next_info}

Please write a short motivating response that:
1. Congratulates them genuinely on completing this milestone.
2. Summarizes in 2-3 sentences what they just built/achieved.
3. {"Tells them the project is fully done and suggests next steps (deploy it, add to portfolio, share it, extend it)." if is_last else f"Gives a short exciting preview of what Milestone {milestone_number + 1} involves and what they'll learn."}

Keep it warm, brief, and energizing. Use markdown.
""".strip()

    return _call_gemini(prompt)

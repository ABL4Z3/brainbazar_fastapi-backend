# SRMS AI Project Guide — FastAPI Backend

An AI-powered backend that acts as a **coding mentor**. Given a project ID, it uses the **Gemini API** to guide users through building a project step-by-step, milestone by milestone.

---

## Tech Stack

| | |
|---|---|
| Framework | FastAPI |
| AI | Google Gemini 2.5 Flash (via REST API) |
| Language | Python 3.11+ |
| Config | python-dotenv |
| HTTP Client | requests |

---

## Project Structure

```
fastapi_backend/
├── main.py                  # App entry point + CORS + router registration
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
├── data/
│   └── demoProjects.json    # Project catalog with milestones
├── models/
│   └── schemas.py           # Pydantic request/response models
├── routers/
│   ├── projects.py          # /projects endpoints
│   └── milestones.py        # /milestones endpoints
└── services/
    ├── data_service.py      # Reads and queries demoProjects.json
    └── gemini_service.py    # All Gemini API calls + prompt builders
```

---

## Setup & Installation

### 1. Clone / navigate to the folder
```bash
cd fastapi_backend
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key
```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and fill in your key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

> Get a free API key at: https://aistudio.google.com/app/apikey

### 5. Start the server
```bash
python -m uvicorn main:app --reload --port 8080
```

The API is now live at: **http://127.0.0.1:8080**

Interactive docs (Swagger UI): **http://127.0.0.1:8080/docs**

---

## API Endpoints

### Base URL
```
http://127.0.0.1:8080
```

---

### Projects

#### `GET /projects`
Returns all projects as lightweight cards (no milestones).

**Response example:**
```json
[
  {
    "id": "demo1",
    "title": "E-commerce Website",
    "level": "Intermediate",
    "summary": "A full-stack e-commerce platform...",
    "technology": ["React", "Node.js", "MongoDB", "Stripe"],
    "tags": ["Web Development", "Full-Stack"],
    "price": "499",
    "isOnSale": false
  }
]
```

---

#### `GET /projects/{project_id}`
Returns full project details including all milestones.

**Example:** `GET /projects/demo1`

**Response example:**
```json
{
  "id": "demo1",
  "title": "E-commerce Website",
  "level": "Intermediate",
  "milestones": [
    { "name": "Milestone 1", "description": "Project setup..." },
    ...
  ]
}
```

---

#### `GET /projects/{project_id}/overview`
**[AI Call]** Returns an AI-generated project overview including:
- What you will build
- What you will learn
- Prerequisites
- Setup checklist
- Project roadmap

**Example:** `GET /projects/demo1/overview`

**Response example:**
```json
{
  "project_id": "demo1",
  "title": "E-commerce Website",
  "content": "## What You Will Build\n..."
}
```

> `content` is markdown formatted — render it on the frontend.

---

### Milestones

#### `GET /projects/{project_id}/milestones/{milestone_number}/guide`
**[AI Call]** Returns a full step-by-step guide for the given milestone including:
- Overview of the milestone
- Numbered steps with code snippets
- How to test before moving on
- Common mistakes to avoid
- Done checklist

**Example:** `GET /projects/demo1/milestones/1/guide`

**Response example:**
```json
{
  "project_id": "demo1",
  "milestone_number": 1,
  "milestone_name": "Milestone 1",
  "content": "## Overview\n..."
}
```

---

#### `GET /projects/{project_id}/milestones/{milestone_number}/hint`
**[AI Call]** Returns a single small hint to nudge the user without giving away the answer.

**Example:** `GET /projects/demo1/milestones/2/hint`

**Response example:**
```json
{
  "project_id": "demo1",
  "milestone_number": 2,
  "milestone_name": "Milestone 2",
  "hint": "Try breaking the layout into smaller reusable components first..."
}
```

---

#### `POST /projects/{project_id}/milestones/{milestone_number}/ask`
**[AI Call]** Ask a specific question in the context of the current milestone.

**Example:** `POST /projects/demo1/milestones/2/ask`

**Request body:**
```json
{
  "question": "I'm getting a CORS error, how do I fix it?"
}
```

**Response example:**
```json
{
  "project_id": "demo1",
  "milestone_number": 2,
  "question": "I'm getting a CORS error, how do I fix it?",
  "answer": "CORS errors happen when..."
}
```

---

#### `POST /projects/{project_id}/milestones/{milestone_number}/complete`
**[AI Call]** Mark a milestone as complete. Returns a congratulations message and a preview of the next milestone (or project completion message if it's the last one).

**Example:** `POST /projects/demo1/milestones/1/complete`

**No request body needed.**

**Response example:**
```json
{
  "project_id": "demo1",
  "milestone_number": 1,
  "message": "🎉 Great work! You've just set up the entire project foundation..."
}
```

---

## Frontend Integration Guide

### Typical User Flow

```
1. Load project list          → GET /projects
2. User picks a project       → GET /projects/{id}
3. Show AI overview           → GET /projects/{id}/overview
4. User starts Milestone 1    → GET /projects/{id}/milestones/1/guide
5. User is stuck              → GET /projects/{id}/milestones/1/hint
                              → POST /projects/{id}/milestones/1/ask  { question }
6. User finishes milestone    → POST /projects/{id}/milestones/1/complete
7. Move to next milestone     → GET /projects/{id}/milestones/2/guide
... repeat until milestone 5
```

### Rendering AI Responses
All `content`, `answer`, `hint`, and `message` fields return **Markdown**. Use a markdown renderer on the frontend:
- React: [`react-markdown`](https://github.com/remarkjs/react-markdown)
- Vue: [`vue-markdown-it`](https://github.com/JanGuillermo/vue3-markdown-it)

### Example fetch (JavaScript)
```js
// Get milestone guide
const res = await fetch('http://127.0.0.1:8080/projects/demo1/milestones/1/guide');
const data = await res.json();
console.log(data.content); // markdown string

// Ask a question
const res = await fetch('http://127.0.0.1:8080/projects/demo1/milestones/1/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: "How do I connect MongoDB?" })
});
const data = await res.json();
console.log(data.answer);
```

### CORS
CORS is already enabled for all origins (`*`) in `main.py`. For production, update `allow_origins` to your frontend's domain:
```python
allow_origins=["https://your-frontend-domain.com"]
```

---

## Error Responses

All endpoints return standard HTTP errors:

| Status | Meaning |
|---|---|
| `404` | Project ID or milestone number not found |
| `500` | Gemini API call failed (check your API key) |

**Example 404:**
```json
{ "detail": "Project 'xyz' not found" }
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |

---

## Available Project IDs

The following project IDs are currently in `demoProjects.json`:

| ID | Title | Level |
|---|---|---|
| `demo1` | E-commerce Website | Intermediate |
| `demo2` | Task Management App | Beginner |
| `demo3` | Weather Dashboard | Beginner |
| `demo4` | Blog Platform | Advanced |
| `demo5` | Portfolio Website | Beginner |
| `demo6` | Chat Application | Intermediate |
| `demo7` | Data Visualization Dashboard | Advanced |

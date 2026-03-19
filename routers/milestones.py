from fastapi import APIRouter, HTTPException
from services import data_service, gemini_service
from models.schemas import (
    AskRequest,
    MilestoneAIResponse,
    MilestoneAskResponse,
    MilestoneQuizResponse,
    StepAskResponse,
    CompletionResponse,
    StepResponse,
    StepGuidanceResponse,
    StepCompleteResponse,
)

router = APIRouter()


def _get_project_and_milestone(project_id: str, milestone_number: int):
    """Shared validation — raises 404 if project or milestone doesn't exist."""
    project = data_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    total = data_service.get_total_milestones(project_id)
    if milestone_number < 1 or milestone_number > total:
        raise HTTPException(
            status_code=404,
            detail=f"Milestone {milestone_number} not found. Project '{project_id}' has {total} milestones.",
        )

    milestone = data_service.get_milestone(project_id, milestone_number)
    return project, milestone


def _get_project_milestone_step(project_id: str, milestone_number: int, step_number: int):
    """Shared validation — raises 404 if project, milestone, or step doesn't exist."""
    project, milestone = _get_project_and_milestone(project_id, milestone_number)

    total_steps = data_service.get_total_steps(project_id, milestone_number)
    if step_number < 1 or step_number > total_steps:
        raise HTTPException(
            status_code=404,
            detail=f"Step {step_number} not found. Milestone {milestone_number} has {total_steps} steps.",
        )

    step = data_service.get_step(project_id, milestone_number, step_number)
    return project, milestone, step


# ──────────────────────────────────────────────
# Milestone-level endpoints (legacy support)
# ──────────────────────────────────────────────


@router.get("/{project_id}/milestones/{milestone_number}/guide", response_model=MilestoneAIResponse)
def get_milestone_guide(project_id: str, milestone_number: int):
    """
    AI-generated step-by-step guide for a specific milestone.
    Includes: overview, steps with code, how to test, common mistakes, done checklist.
    """
    project, milestone = _get_project_and_milestone(project_id, milestone_number)
    content = gemini_service.get_milestone_guide(project, milestone_number, milestone)
    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "milestone_name": milestone["name"],
        "content": content,
    }


@router.get("/{project_id}/milestones/{milestone_number}/hint")
def get_milestone_hint(project_id: str, milestone_number: int):
    """
    Returns a single small hint to nudge the user without giving away the solution.
    """
    project, milestone = _get_project_and_milestone(project_id, milestone_number)
    hint = gemini_service.get_milestone_hint(project, milestone_number, milestone)
    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "milestone_name": milestone["name"],
        "hint": hint,
    }


@router.post("/{project_id}/milestones/{milestone_number}/ask", response_model=MilestoneAskResponse)
def ask_question(project_id: str, milestone_number: int, body: AskRequest):
    """
    Ask the AI a specific question in the context of the current milestone.
    Example: 'I'm getting a CORS error, how do I fix it?'
    """
    project, milestone = _get_project_and_milestone(project_id, milestone_number)
    answer = gemini_service.ask_milestone_question(
        project, milestone_number, milestone, body.question
    )
    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "question": body.question,
        "answer": answer,
    }


@router.post("/{project_id}/milestones/{milestone_number}/complete", response_model=CompletionResponse)
def complete_milestone(project_id: str, milestone_number: int):
    """
    Mark a milestone as complete. Returns an AI-generated congratulations message
    and a preview of the next milestone (or project completion message if it's the last one).
    """
    project, milestone = _get_project_and_milestone(project_id, milestone_number)
    message = gemini_service.get_milestone_completion(project, milestone_number, milestone)
    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "message": message,
    }


@router.get("/{project_id}/milestones/{milestone_number}/quiz", response_model=MilestoneQuizResponse)
def get_milestone_quiz(project_id: str, milestone_number: int, num_questions: int = 5):
    """
    AI-generated quiz focused on one milestone.
    """
    if num_questions < 1 or num_questions > 20:
        raise HTTPException(status_code=400, detail="num_questions must be between 1 and 20")

    project, milestone = _get_project_and_milestone(project_id, milestone_number)
    quiz = gemini_service.generate_milestone_quiz(project, milestone_number, milestone, num_questions)

    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "milestone_name": milestone["name"],
        "total_questions": len(quiz),
        "quiz": quiz,
    }


# ──────────────────────────────────────────────
# Step-level endpoints (NEW)
# ──────────────────────────────────────────────


@router.get("/{project_id}/milestones/{milestone_number}/steps")
def list_steps(project_id: str, milestone_number: int):
    """
    Return all steps in a milestone with their basic info.
    """
    project, milestone = _get_project_and_milestone(project_id, milestone_number)
    steps = data_service.list_steps(project_id, milestone_number) or []

    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "milestone_name": milestone["name"],
        "total_steps": len(steps),
        "steps": [
            {
                "stepNumber": s["stepNumber"],
                "title": s["title"],
                "description": s["description"],
            }
            for s in steps
        ],
    }


@router.get("/{project_id}/milestones/{milestone_number}/steps/{step_number}", response_model=StepResponse)
def get_step(project_id: str, milestone_number: int, step_number: int):
    """
    Get full details of a specific step including code blocks, verification, and hints.
    """
    project, milestone, step = _get_project_milestone_step(project_id, milestone_number, step_number)

    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "step_number": step_number,
        "step_title": step["title"],
        "step_description": step["description"],
        "codeBlocks": step.get("codeBlocks", []),
        "verificationSteps": step["verificationSteps"],
        "hints": step["hints"],
    }


@router.get(
    "/{project_id}/milestones/{milestone_number}/steps/{step_number}/guide",
    response_model=StepGuidanceResponse,
)
def get_step_guide(project_id: str, milestone_number: int, step_number: int):
    """
    [AI CALL] Get detailed guidance for a specific step.
    Explains the code, context, and how to complete it.
    """
    project, milestone, step = _get_project_milestone_step(project_id, milestone_number, step_number)

    content = gemini_service.explain_step_code(project, milestone_number, step)

    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "step_number": step_number,
        "step_title": step["title"],
        "content": content,
    }


@router.post("/{project_id}/milestones/{milestone_number}/steps/{step_number}/ask", response_model=StepAskResponse)
def ask_step_question(project_id: str, milestone_number: int, step_number: int, body: AskRequest):
    """
    [AI CALL] Ask a question about a specific step.
    """
    project, milestone, step = _get_project_milestone_step(project_id, milestone_number, step_number)

    answer = gemini_service.ask_step_question(project, milestone_number, step, body.question)

    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "step_number": step_number,
        "question": body.question,
        "answer": answer,
    }


@router.post("/{project_id}/milestones/{milestone_number}/steps/{step_number}/complete", response_model=StepCompleteResponse)
def complete_step(project_id: str, milestone_number: int, step_number: int):
    """
    [AI CALL] Mark a step as complete.
    Returns a congratulations message and preview of next step.
    """
    project, milestone, step = _get_project_milestone_step(project_id, milestone_number, step_number)

    total_steps = data_service.get_total_steps(project_id, milestone_number)
    message = gemini_service.get_step_completion_message(project, milestone_number, step, total_steps)

    next_preview = None
    if step_number < total_steps:
        next_step = data_service.get_step(project_id, milestone_number, step_number + 1)
        if next_step:
            next_preview = f"Next: Step {step_number + 1} — {next_step['title']}"

    return {
        "project_id": project_id,
        "milestone_number": milestone_number,
        "step_number": step_number,
        "message": message,
        "next_step_preview": next_preview,
    }

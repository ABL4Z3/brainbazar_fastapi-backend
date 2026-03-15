from fastapi import APIRouter, HTTPException
from services import data_service, gemini_service
from models.schemas import AskRequest, MilestoneAIResponse, AskResponse, CompletionResponse

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


@router.post("/{project_id}/milestones/{milestone_number}/ask", response_model=AskResponse)
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

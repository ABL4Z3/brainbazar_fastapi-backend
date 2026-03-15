from fastapi import APIRouter, HTTPException
from services import data_service, gemini_service
from models.schemas import ProjectSummary, AIResponse

router = APIRouter()


@router.get("/", response_model=list[ProjectSummary])
def list_projects():
    """Return all projects as lightweight cards (no milestones)."""
    projects = data_service.load_projects()
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "level": p["level"],
            "summary": p["summary"],
            "technology": p["technology"],
            "tags": p["tags"],
            "price": p["price"],
            "isOnSale": p.get("isOnSale", False),
            "originalPrice": p.get("originalPrice"),
        }
        for p in projects
    ]


@router.get("/{project_id}")
def get_project(project_id: str):
    """Return full project details including all milestones."""
    project = data_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return project


@router.get("/{project_id}/overview", response_model=AIResponse)
def get_project_overview(project_id: str):
    """
    AI-generated overview of the project:
    what you'll build, what you'll learn, prerequisites, setup checklist, and roadmap.
    """
    project = data_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    content = gemini_service.get_project_overview(project)
    return {"project_id": project_id, "title": project["title"], "content": content}

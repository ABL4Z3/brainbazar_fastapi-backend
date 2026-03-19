import json
import os
from typing import Optional

# Path to the data file — relative to this file's location
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/demoProjects.json")


def load_projects() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_project_by_id(project_id: str) -> Optional[dict]:
    for project in load_projects():
        if project["id"] == project_id:
            return project
    return None


def get_milestone(project_id: str, milestone_number: int) -> Optional[dict]:
    project = get_project_by_id(project_id)
    if not project:
        return None
    milestones = project.get("milestones", [])
    index = milestone_number - 1  # Convert 1-based to 0-based
    if 0 <= index < len(milestones):
        return milestones[index]
    return None


def get_total_milestones(project_id: str) -> int:
    project = get_project_by_id(project_id)
    if not project:
        return 0
    return len(project.get("milestones", []))


def get_step(project_id: str, milestone_number: int, step_number: int) -> Optional[dict]:
    """Get a specific step from a milestone."""
    milestone = get_milestone(project_id, milestone_number)
    if not milestone:
        return None
    steps = milestone.get("steps", [])
    # Steps are 1-indexed in the JSON
    for step in steps:
        if step.get("stepNumber") == step_number:
            return step
    return None


def get_total_steps(project_id: str, milestone_number: int) -> int:
    """Get total number of steps in a milestone."""
    milestone = get_milestone(project_id, milestone_number)
    if not milestone:
        return 0
    return len(milestone.get("steps", []))


def list_steps(project_id: str, milestone_number: int) -> Optional[list[dict]]:
    """Get all steps in a milestone."""
    milestone = get_milestone(project_id, milestone_number)
    if not milestone:
        return None
    return milestone.get("steps", [])

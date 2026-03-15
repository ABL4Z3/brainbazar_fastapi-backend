from pydantic import BaseModel
from typing import Optional, List


class Milestone(BaseModel):
    name: str
    description: str


class Project(BaseModel):
    id: str
    title: str
    level: str
    summary: str
    technology: List[str]
    tags: List[str]
    price: str
    isOnSale: Optional[bool] = False
    originalPrice: Optional[str] = None
    image: Optional[str] = None
    youtube: Optional[str] = None
    milestones: List[Milestone]
    contextReadmeLink: Optional[str] = None


class ProjectSummary(BaseModel):
    """Lightweight project card — no milestones, used for list view"""
    id: str
    title: str
    level: str
    summary: str
    technology: List[str]
    tags: List[str]
    price: str
    isOnSale: Optional[bool] = False
    originalPrice: Optional[str] = None


class AskRequest(BaseModel):
    question: str


class AIResponse(BaseModel):
    project_id: str
    title: str
    content: str


class MilestoneAIResponse(BaseModel):
    project_id: str
    milestone_number: int
    milestone_name: str
    content: str


class AskResponse(BaseModel):
    project_id: str
    milestone_number: int
    question: str
    answer: str


class CompletionResponse(BaseModel):
    project_id: str
    milestone_number: int
    message: str

from pydantic import BaseModel
from typing import Optional, List


class CodeBlock(BaseModel):
    fileName: str
    language: str  # javascript, python, json, bash, sql, etc.
    code: str


class Step(BaseModel):
    stepNumber: int
    title: str
    description: str
    verificationSteps: str
    hints: str
    codeBlocks: List[CodeBlock] = []


class Milestone(BaseModel):
    name: str
    description: str
    steps: Optional[List[Step]] = None  # New structure with steps


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


class StepResponse(BaseModel):
    project_id: str
    milestone_number: int
    step_number: int
    step_title: str
    step_description: str
    codeBlocks: List[CodeBlock]
    verificationSteps: str
    hints: str
    guidance: Optional[str] = None  # AI-generated explanation


class StepGuidanceResponse(BaseModel):
    project_id: str
    milestone_number: int
    step_number: int
    step_title: str
    content: str  # Markdown explanation from Gemini


class MilestoneAskResponse(BaseModel):
    """Milestone-level ask response (no step)"""
    project_id: str
    milestone_number: int
    question: str
    answer: str


class StepAskResponse(BaseModel):
    """Step-level ask response (with step)"""
    project_id: str
    milestone_number: int
    step_number: int
    question: str
    answer: str


class StepCompleteResponse(BaseModel):
    project_id: str
    milestone_number: int
    step_number: int
    message: str
    next_step_preview: Optional[str] = None


class CompletionResponse(BaseModel):
    project_id: str
    milestone_number: int
    message: str

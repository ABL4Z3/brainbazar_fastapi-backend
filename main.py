from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import projects, milestones

app = FastAPI(
    title="SRMS AI Project Guide API",
    description="AI-powered project mentor using Gemini. Guides users through building projects milestone by milestone.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(milestones.router, prefix="/projects", tags=["Milestones"])


@app.get("/", tags=["Health"])
def root():
    return {"message": "SRMS AI Project Guide API is running", "docs": "/docs"}

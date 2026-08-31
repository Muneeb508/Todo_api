"""
Task API — a small in-memory CRUD API built with FastAPI.

FlyRank Internship · Backend Track · Week 2 · Assignment A1

Run with:
    uvicorn main:app --reload

Then visit:
    http://localhost:8000/          -> API description
    http://localhost:8000/health    -> health check
    http://localhost:8000/docs      -> Swagger UI (interactive docs)
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A tiny in-memory to-do list API — full CRUD, no database (yet).",
)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    """Body accepted by POST /tasks — id and done are set by the server."""
    title: str = Field(default="", description="Title of the task")


class TaskUpdate(BaseModel):
    """Body accepted by PUT /tasks/{id}. Both fields optional so a client
    can update just the title, just done, or both."""
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# In-memory "database" — just a Python list. Resets whenever the server
# restarts. That's intentional for Week 2 — databases show up in Week 3.
# ---------------------------------------------------------------------------

def seed_tasks() -> List[dict]:
    return [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Write README", "done": False},
        {"id": 3, "title": "Learn FastAPI", "done": True},
    ]


tasks: List[dict] = seed_tasks()
next_id: int = 4


# ---------------------------------------------------------------------------
# Stage 1 — root and health endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["meta"], summary="Describe this API")
def read_root():
    """Returns basic info about the API — the front door."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", tags=["meta"], summary="Health check")
def health_check():
    """Returns 200 + {status: ok} if the server is alive."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Stage 2 — Read: list and single task
# ---------------------------------------------------------------------------

@app.get("/tasks", tags=["tasks"], summary="List tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None,
                limit: Optional[int] = None, offset: int = 0):
    """
    Returns all tasks.

    Optional query parameters (stretch goals):
    - done: filter by completion status (?done=true)
    - search: only tasks whose title contains this text (?search=milk)
    - limit / offset: pagination (?limit=2&offset=2)
    """
    result = tasks

    if done is not None:
        result = [t for t in result if t["done"] == done]

    if search:
        needle = search.lower()
        result = [t for t in result if needle in t["title"].lower()]

    if offset:
        result = result[offset:]
    if limit is not None:
        result = result[:limit]

    return result


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------------------------------------------------------------------------
# Stage 3 — Create: POST a new task
# ---------------------------------------------------------------------------

@app.post("/tasks", tags=["tasks"], status_code=status.HTTP_201_CREATED,
           summary="Create a task")
def create_task(payload: TaskCreate):
    """
    Creates a new task from { "title": "..." }.
    Validates that title is present and non-empty -> 400 if not.
    """
    global next_id

    title = (payload.title or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    new_task = {"id": next_id, "title": title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


# ---------------------------------------------------------------------------
# Stage 4 — Update & Delete
# ---------------------------------------------------------------------------

@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """
    Replaces title and/or done for a task.
    404 if the task doesn't exist. 400 if the body is empty/invalid
    (i.e. neither title nor done was provided, or title is blank).
    """
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Provide at least one of: title, done")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="title cannot be empty")
        task["title"] = title

    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", tags=["tasks"], status_code=status.HTTP_204_NO_CONTENT,
             summary="Delete a task")
def delete_task(task_id: int):
    """Removes a task. Returns 204 with no body. 404 if it doesn't exist."""
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------------------------------------------------------------------------
# Extras (optional stretch goals)
# ---------------------------------------------------------------------------

@app.get("/stats", tags=["extras"], summary="Task stats")
def get_stats():
    """Returns counts instead of raw data — the server computing something."""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset", tags=["extras"], summary="Reset to seed data")
def reset_tasks():
    """Restores the original 3 example tasks. Handy for demos."""
    global tasks, next_id
    tasks = seed_tasks()
    next_id = 4
    return {"status": "reset", "tasks": tasks}


# ---------------------------------------------------------------------------
# Make sure every error still comes back as { "error": "..." } as the
# assignment spec asks for, on top of FastAPI's default {"detail": "..."}.
# ---------------------------------------------------------------------------

from fastapi.exception_handlers import http_exception_handler
from fastapi.requests import Request
from fastapi.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def seed():
    return [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Write README", "done": False},
        {"id": 3, "title": "Learn FastAPI", "done": True},
    ]


tasks: List[dict] = seed()
next_id = 4


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"error": exc.errors()})


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "description": "A simple in-memory to-do list API",
        "endpoints": ["/tasks", "/tasks/{id}", "/stats", "/reset", "/health"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None,
               limit: Optional[int] = None, offset: Optional[int] = 0):
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        result = [t for t in result if search.lower() in t["title"].lower()]
    result = result[offset:]
    if limit is not None:
        result = result[:limit]
    return result


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    global next_id
    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    for t in tasks:
        if t["id"] == task_id:
            if update.title is not None:
                t["title"] = update.title
            if update.done is not None:
                t["done"] = update.done
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/stats")
def stats():
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done, "pending": total - done}


@app.post("/reset")
def reset():
    global tasks, next_id
    tasks = seed()
    next_id = 4
    return {"status": "reset"}

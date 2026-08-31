# Task API

A small in-memory to-do list API built with **FastAPI** for the FlyRank
Internship — Backend Track, Week 2, Assignment A1. Full CRUD (Create, Read,
Update, Delete) on tasks, interactive docs via Swagger UI, no database yet —
data lives in memory and resets when the server restarts.

## How to install & run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The server starts on **http://localhost:8000**.

- API root: http://localhost:8000/
- Health check: http://localhost:8000/health
- Swagger UI (interactive docs): **http://localhost:8000/docs**

## Endpoints

| Method | Path          | Description                          | Success | Errors        |
|--------|---------------|---------------------------------------|---------|---------------|
| GET    | `/`           | API description                       | 200     | —             |
| GET    | `/health`     | Health check                          | 200     | —             |
| GET    | `/tasks`      | List all tasks (supports `?done=`, `?search=`, `?limit=`, `?offset=`) | 200 | — |
| GET    | `/tasks/{id}` | Get a single task                     | 200     | 404 not found |
| POST   | `/tasks`      | Create a task (`{"title": "..."}`)    | 201     | 400 invalid body |
| PUT    | `/tasks/{id}` | Update a task's title and/or done     | 200     | 400 invalid body, 404 not found |
| DELETE | `/tasks/{id}` | Delete a task                         | 204     | 404 not found |
| GET    | `/stats`      | Task counts (extra)                   | 200     | — |
| POST   | `/reset`      | Restore the 3 example tasks (extra)   | 200     | — |

Every error response is JSON in the form `{ "error": "..." }`.

## Example curl output

```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

```
$ curl -i http://localhost:8000/tasks/99
HTTP/1.1 404 Not Found
content-type: application/json

{"error":"Task 99 not found"}
```

## Swagger screenshot

![Swagger UI](swagger.png)

## The mortality experiment

Create a few tasks, restart the server, then `GET /tasks` again — the tasks
you added are gone and only the 3 seeded tasks remain. That's because the
"database" is just a Python list living in the server's memory: it only
exists while the process is running. This is exactly why Week 3 introduces
a real database — to make data survive a restart.

## Notes on this submission

This repo was built stage-by-stage (Stages 0–6) following the assignment.
Commit history should have one commit per stage:

```
git init
git add main.py requirements.txt README.md
git commit -m "Stage 0: hello server"
# ...repeat for each stage as you build it...
git remote add origin <your-repo-url>
git push -u origin main
```

### AI vs me (Stage 7 — bonus)

_Fill this in after you complete Stage 7 yourself: your own prompt to an AI
assistant, the AI's code in `ai-version/`, and at least three concrete
differences you found between its output and this hand-built version._

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import asyncio, json
from pathlib import Path

from storage import init_storage, read_books
from models import BookUpsert, PaginatedBooks, BookOut
from crud import upsert_book, delete_book, get_books

connected_clients: list[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_storage()
    asyncio.create_task(watch_books())
    yield

app = FastAPI(title="Books API", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Return clean, human-readable validation errors instead of FastAPI's raw 422 format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for e in exc.errors():
        field = " -> ".join(str(loc) for loc in e["loc"] if loc != "body")
        errors.append(f"{field}: {e['msg']}" if field else e["msg"])
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation failed.", "errors": errors},
    )

# Background task that polls for changes and broadcasts the updated list to all WS clients
async def watch_books():
    last_snapshot = None
    while True:
        try:
            books = read_books()
            snapshot = json.dumps(books, sort_keys=True)
            if snapshot != last_snapshot:
                last_snapshot = snapshot
                if connected_clients:
                    message = json.dumps({"type": "update", "books": books})
                    dead = []
                    for ws in connected_clients:
                        try:
                            await ws.send_text(message)
                        except Exception:
                            dead.append(ws)
                    for ws in dead:
                        connected_clients.remove(ws)
        except Exception:
            pass
        await asyncio.sleep(1)

# Serve the frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = Path("static/index.html")

    if not html_path.exists():
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)

    return HTMLResponse(
        content=html_path.read_text(encoding="utf-8")
    )
# Create a new book (201) or update an existing one (200) matched by ISBN or title+author+year
@app.post("/books")
async def create_or_update_book(data: BookUpsert):
    book, created = upsert_book(data)
    if created:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": f"Book '{book.title}' created successfully.",
                "book": book.model_dump(),
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": f"Book '{book.title}' updated successfully.",
            "book": book.model_dump(),
        },
    )

# Retrieve books with optional filtering, sorting, and pagination
@app.get("/books", response_model=PaginatedBooks)
async def list_books(
    genre: str | None = Query(default=None),
    author: str | None = Query(default=None),
    sort_by: str | None = Query(default=None, description="title | author | publication_year"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    return get_books(genre, author, sort_by, sort_order, page, page_size)

# Delete a book by ID and return what was deleted
@app.delete("/books/{book_id}")
async def remove_book(book_id: int):
    book = delete_book(book_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": f"Book '{book.title}' by {book.author} has been deleted.",
            "deleted_book": book.model_dump(),
        },
    )

# WebSocket endpoint - sends full book list on connect and on every detected change
@app.websocket("/ws/books")
async def websocket_books(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        initial = json.dumps({"type": "update", "books": read_books()})
        await websocket.send_text(initial)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
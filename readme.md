Bookshelf
A full-stack book management app built with FastAPI and vanilla JS. Books are stored in a local JSON file with no database required. The UI updates in real time via WebSocket whenever the data changes.

Features

Add, update, and delete books
Filter by genre and author
Sort by title, author, or publication year
Pagination with configurable page size
Real-time sync across browser tabs via WebSocket
Duplicate detection by ISBN or title + author + year
Input validation on both client and server


Project Structure
.
├── main.py          # FastAPI app, routes, WebSocket, lifespan
├── crud.py          # Business logic: upsert, delete, query
├── models.py        # Pydantic schemas and field validators
├── storage.py       # Thread-safe JSON read/write
├── books.json       # Auto-created on first run
└── static/
    └── index.html   # Frontend (HTML + CSS + JS, no framework)

Requirements

Python 3.11+
FastAPI
Uvicorn

Install dependencies:
bashpip install fastapi uvicorn pydantic

Running the App
bashuvicorn main:app --reload
Open http://localhost:8000 in your browser.

API Reference
POST /books
Create a new book or update an existing one. Matches by ISBN or title + author + year. Returns 201 on create, 200 on update.
Request body:
json{
  "title": "Dune",
  "author": "Frank Herbert",
  "publication_year": 1965,
  "genre": "Sci-Fi",
  "isbn": "978-0-441-17271-9"
}
Response:
json{
  "success": true,
  "message": "Book 'Dune' created successfully.",
  "book": { "id": 1, "title": "Dune", "..." : "..." }
}

GET /books
Retrieve books with optional filtering, sorting, and pagination.
Query paramTypeDefaultDescriptiongenrestring—Exact genre match (case-insensitive)authorstring—Partial author match (case-insensitive)sort_bystring—title, author, or publication_yearsort_orderstringascasc or descpageinteger1Page number (min 1)page_sizeinteger10Results per page (1–100)
Example:
GET /books?genre=Sci-Fi&sort_by=title&sort_order=asc&page=1&page_size=10
Response:
json{
  "total": 42,
  "page": 1,
  "page_size": 10,
  "books": [ { "id": 1, "title": "Dune", "..." : "..." } ]
}

DELETE /books/{book_id}
Delete a book by ID. Returns 404 if not found.
Response:
json{
  "success": true,
  "message": "Book 'Dune' by Frank Herbert has been deleted.",
  "deleted_book": { "id": 1, "title": "Dune", "..." : "..." }
}

WebSocket /ws/books
Connect to receive real-time book list updates. Sends the full book list on connect, then pushes an update on every change.
Message format:
json{ "type": "update", "books": [ ] }

Validation Rules
FieldRulestitleRequired, non-blankauthorRequired, non-blankpublication_yearInteger, 4 digits, range 1450 to current yeargenreRequired, non-blankisbnValid ISBN-10 or ISBN-13, hyphens allowed
Validation errors return HTTP 422:
json{
  "success": false,
  "message": "Validation failed.",
  "errors": ["publication_year: Earliest supported year is 1450."]
}

Error Reference
StatusMeaning200OK — book updated or deleted201Created — new book added400Bad request — invalid sort_by value404Book not found409ISBN already used by another book422Validation failed


License
MIT

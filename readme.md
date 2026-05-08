# Bookshelf

A full-stack book management application built with FastAPI and vanilla JavaScript.  
Books are stored in a local JSON file, so no database setup is required.  
The frontend updates in real time using WebSockets whenever the dataset changes.

---

## Features

- Add, update, and delete books
- Filter books by genre and author
- Sort by title, author, or publication year
- Pagination with configurable page size
- Real-time synchronization across browser tabs via WebSocket
- Duplicate detection using:
  - ISBN
  - Title + author + publication year
- Client-side and server-side validation
- JSON file persistence (no database required)

---

## Project Structure

```text
.
├── main.py          # FastAPI app, routes, WebSocket, lifespan
├── crud.py          # Business logic: upsert, delete, query
├── models.py        # Pydantic schemas and validators
├── storage.py       # Thread-safe JSON read/write utilities
├── books.json       # Auto-created on first run
└── static/
    └── index.html   # Frontend (HTML + CSS + JS)Requirements
Python 3.11+
FastAPI
Uvicorn
Pydantic
Installation

Install dependencies:

pip install fastapi uvicorn pydantic
Running the Application

Start the FastAPI server:

uvicorn main:app --reload

Open the app in your browser:

http://localhost:8000

API documentation:

http://localhost:8000/docs
API Reference
POST /books

Create a new book or update an existing one.

A book is considered existing if:

The ISBN matches, or
The combination of title + author + publication year matches
Request Body
{
  "title": "Dune",
  "author": "Frank Herbert",
  "publication_year": 1965,
  "genre": "Sci-Fi",
  "isbn": "978-0-441-17271-9"
}
Success Response (201 Created)
{
  "success": true,
  "message": "Book 'Dune' created successfully.",
  "book": {
    "id": 1,
    "title": "Dune"
  }
}
Success Response (200 Updated)
{
  "success": true,
  "message": "Book 'Dune' updated successfully.",
  "book": {
    "id": 1,
    "title": "Dune"
  }
}
GET /books

Retrieve books with optional filtering, sorting, and pagination.

Query Parameters
Parameter	Type	Default	Description
genre	string	—	Exact genre match (case-insensitive)
author	string	—	Partial author match (case-insensitive)
sort_by	string	—	title, author, or publication_year
sort_order	string	asc	asc or desc
page	integer	1	Page number
page_size	integer	10	Results per page (1–100)
Example Request
GET /books?genre=Sci-Fi&sort_by=title&sort_order=asc&page=1&page_size=10
Response
{
  "total": 42,
  "page": 1,
  "page_size": 10,
  "books": [
    {
      "id": 1,
      "title": "Dune"
    }
  ]
}
DELETE /books/{book_id}

Delete a book using its ID.

Success Response
{
  "success": true,
  "message": "Book 'Dune' by Frank Herbert has been deleted.",
  "deleted_book": {
    "id": 1,
    "title": "Dune"
  }
}
Error Response
{
  "detail": "Book not found"
}
WebSocket /ws/books

Provides real-time updates whenever the dataset changes.

Behavior
Sends the complete book list immediately after connection
Pushes updates automatically whenever books are added, updated, or deleted
Message Format
{
  "type": "update",
  "books": []
}
Validation Rules
Field	Rules
title	Required, non-empty
author	Required, non-empty
publication_year	Integer, 4 digits, range 1450 to current year
genre	Required, non-empty
isbn	Valid ISBN-10 or ISBN-13 (hyphens allowed)
Validation Error Example

HTTP 422 Unprocessable Entity

{
  "success": false,
  "message": "Validation failed.",
  "errors": [
    "publication_year: Earliest supported year is 1450."
  ]
}
Error Reference
Status Code	Meaning
200	OK — book updated or deleted
201	Created — new book added
400	Bad Request — invalid sort_by value
404	Book not found
409	ISBN already used by another book
422	Validation failed
Tech Stack
FastAPI
Pydantic
Uvicorn
Vanilla JavaScript
WebSockets
JSON File Storage
License

MIT License

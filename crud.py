from storage import read_books, write_books
from models import BookUpsert, BookOut
from fastapi import HTTPException

VALID_SORT_FIELDS = {"title", "author", "publication_year"}

# Find a book that matches by isbn OR by title+author+year combination
def _find_existing(books: list[dict], data: BookUpsert) -> dict | None:
    for book in books:
        if book["isbn"] == data.isbn:
            return book
        same_combo = (
            book["title"].lower() == data.title.lower()
            and book["author"].lower() == data.author.lower()
            and book["publication_year"] == data.publication_year
        )
        if same_combo:
            return book
    return None

# Get the next available integer ID
def _next_id(books: list[dict]) -> int:
    return max((b["id"] for b in books), default=0) + 1

# Upsert a book: update if exists, create if not; raises on duplicate ISBN across different records
def upsert_book(data: BookUpsert) -> tuple[BookOut, bool]:
    books = read_books()
    existing = _find_existing(books, data)

    if existing:
        isbn_conflict = next(
            (b for b in books if b["isbn"] == data.isbn and b["id"] != existing["id"]),
            None
        )
        if isbn_conflict:
            raise HTTPException(status_code=409, detail="ISBN already used by another book")
        existing.update(data.model_dump())
        write_books(books)
        return BookOut(**existing), False
    else:
        isbn_taken = any(b["isbn"] == data.isbn for b in books)
        if isbn_taken:
            raise HTTPException(status_code=409, detail="ISBN already exists")
        new_book = {"id": _next_id(books), **data.model_dump()}
        books.append(new_book)
        write_books(books)
        return BookOut(**new_book), True

# Delete a book by ID; raises 404 if not found
def delete_book(book_id: int) -> BookOut:
    books = read_books()
    match = next((b for b in books if b["id"] == book_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Book not found")
    books = [b for b in books if b["id"] != book_id]
    write_books(books)
    return BookOut(**match)

# Retrieve books with optional filtering, sorting, and pagination
def get_books(
    genre: str | None,
    author: str | None,
    sort_by: str | None,
    sort_order: str,
    page: int,
    page_size: int,
) -> dict:
    if sort_by and sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {VALID_SORT_FIELDS}")

    books = read_books()

    if genre:
        genre_clean = genre.strip().lower()
        books = [b for b in books if b.get("genre", "").lower() == genre_clean]
    if author:
        author_clean = author.strip().lower()
        books = [b for b in books if author_clean in b.get("author", "").lower()]

    if sort_by:
        reverse = sort_order.lower() == "desc"
        books = sorted(books, key=lambda b: b.get(sort_by, ""), reverse=reverse)

    total = len(books)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = books[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "books": [BookOut(**b) for b in paginated],
    }
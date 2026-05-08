from pydantic import BaseModel, field_validator
from datetime import datetime

MIN_YEAR = 1450
MAX_YEAR = datetime.now().year

class BookUpsert(BaseModel):
    title: str
    author: str
    publication_year: int
    genre: str
    isbn: str

    # Reject negative years, years before printing era, and future years
    @field_validator("publication_year")
    @classmethod
    def validate_year(cls, v):
        if v < 0:
            raise ValueError("Publication year cannot be negative.")
        if v < MIN_YEAR:
            raise ValueError(f"Publication year is too far back. Earliest supported year is {MIN_YEAR} (Gutenberg printing era).")
        if v > MAX_YEAR:
            raise ValueError(f"Publication year {v} is in the future. Max allowed is {MAX_YEAR}.")
        return v

    # Reject blank or whitespace-only ISBNs
    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("ISBN cannot be empty or whitespace.")
        digits_only = re.sub(r"[-\s]", "", v)
        is_isbn10 = bool(re.fullmatch(r"\d{9}[\dXx]", digits_only))
        is_isbn13 = bool(re.fullmatch(r"\d{13}", digits_only))
        if not is_isbn10 and not is_isbn13:
            raise ValueError(
                "ISBN must be a valid ISBN-10 (9 digits + check digit/X) "
                "or ISBN-13 (13 digits). Hyphens are allowed as separators."
            )
        return v 

    # Reject blank title
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty.")
        return v.strip()

    # Reject blank author
    @field_validator("author")
    @classmethod
    def validate_author(cls, v):
        if not v.strip():
            raise ValueError("Author cannot be empty.")
        return v.strip()

    # Reject blank genre
    @field_validator("genre")
    @classmethod
    def validate_genre(cls, v):
        if not v.strip():
            raise ValueError("Genre cannot be empty.")
        return v.strip()

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    publication_year: int
    genre: str
    isbn: str

class PaginatedBooks(BaseModel):
    total: int
    page: int
    page_size: int
    books: list[BookOut]
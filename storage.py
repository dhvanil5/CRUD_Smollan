import json
import threading
from pathlib import Path

DATA_FILE = Path("books.json")
_lock = threading.RLock()

# Initialize the JSON file if it doesn't exist
def init_storage():
    with _lock:
        if not DATA_FILE.exists():
            DATA_FILE.write_text(json.dumps([]))

# Read all books from the JSON file safely
def read_books() -> list[dict]:
    with _lock:
        try:
            return json.loads(DATA_FILE.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return []

# Write the full books list to the JSON file safely
def write_books(books: list[dict]) -> None:
    with _lock:
        DATA_FILE.write_text(json.dumps(books, indent=2))
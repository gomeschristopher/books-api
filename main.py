from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    rating: int
    description: str

    def __init__(self, id: int, title: str, author: str, rating: int, description: str):
        self.id = id
        self.title = title
        self.author = author
        self.rating = rating
        self.description = description
    
class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not need on create', default=None)
    title: str = Field(..., min_length=3)
    author: str = Field(..., min_length=3)
    rating: int = Field(..., gt=0, lt=6)
    description: str = Field(..., min_length=3)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "My First Book",
                "author": "Christopher",
                "rating": 5,
                "description": "A book about love"
            }
        }
    }

books = [
    Book(1, "Book 1", "Author 1", 1, "Description 1"),
    Book(2, "Book 2", "Author 2", 2, "Description 2"),
    Book(3, "Book 3", "Author 3", 3, "Description 3"),
    Book(4, "Book 4", "Author 4", 4, "Description 4"),
    Book(5, "Book 5", "Author 5", 5, "Description 5"),
    Book(6, "Book 6", "Author 6", 6, "Description 6")
]

@app.get("/books", status_code=status.HTTP_200_OK)
def read_all_books():
    return books

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
def read_item(book_id: int = Path(gt=0)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/")
def read_title_by_query(title: str = Query(min_length=3, max_length=100)):
    requested_books = []
    for book in books:
        if book.title == title:
            requested_books.append(book)
    return requested_books

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookRequest):
    new_book = Book(**book.dict())
    books.append(find_book_id(new_book))
    return new_book

@app.put("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_book(book_id: int, book_data: BookRequest):
    for book in books:
        if book.get("id") == book_id:
            book.update(book_data)
            return book
    return {"message": "Book not found"}
        
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for book in books:
        if book.get("id") == book_id:
            books.remove(book)
            return {"message": "Book deleted successfully"}
    return {"message": "Book not found"}


def find_book_id(book: Book):
    if len(books) > 0:
        book.id = books[-1].id + 1
    else:
        book.id = 1
    return book
    

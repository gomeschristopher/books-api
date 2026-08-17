from fastapi import FastAPI

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
    

books = [
    Book(1, "Book 1", "Author 1", 1, "Description 1"),
    Book(2, "Book 2", "Author 2", 2, "Description 2"),
    Book(3, "Book 3", "Author 3", 3, "Description 3"),
    Book(4, "Book 4", "Author 4", 4, "Description 4"),
    Book(5, "Book 5", "Author 5", 5, "Description 5"),
    Book(6, "Book 6", "Author 6", 6, "Description 6")
]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/books")
def read_all_books():
    return books

@app.get("/books/{book_id}")
def read_item(book_id: int):
    for book in books:
        if book.get("id") == book_id:
            return book
    return {"message": "Book not found"}

@app.get("/books/")
def read_title_by_query(title: str):
    requested_books = []
    for book in books:
        if book.get("title") == title:
            requested_books.append(book)
    return requested_books

@app.post("/books")
def create_book(book: dict):
    books.append(book)

@app.put("/books/{book_id}")
def update_book(book_id: int, book_data: dict):
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

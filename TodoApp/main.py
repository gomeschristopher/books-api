from fastapi import FastAPI, Depends, Path
from pydantic import BaseModel, Field
import models 
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3)
    complete: bool = Field(default=False)
    priority: int = Field(..., gt=0, lt=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "My First Todo",
                "description": "A todo about love",
                "complete": False,
                "priority": 3
            }
        }
    }

@app.get("/")
def read_items(db: db_dependency):
    items = db.query(Todos).all()
    return items

@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        return {"error": "Todo not found"}
    return todo

@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoRequest, db: db_dependency):
    new_todo = Todos(
        **todo.model_dump()
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo 

@app.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(todo_id: int, todo: TodoRequest, db: db_dependency):
    todo_to_update = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_to_update is None:
        return {"error": "Todo not found"}
    todo_to_update.title = todo.title
    todo_to_update.description = todo.description
    todo_to_update.complete = todo.complete
    todo_to_update.priority = todo.priority
    db.add(todo_to_update)
    db.commit() 

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: db_dependency):
    todo_to_delete = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_to_delete is None:
        return {"error": "Todo not found"}
    db.delete(todo_to_delete)
    db.commit()
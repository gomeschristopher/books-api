from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

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

@router.get("/")
def read_items(user: user_dependency, db: db_dependency):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    items = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    return items

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo is None:
        return {"error": "Todo not found"}
    return todo

@router.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependency, todo: TodoRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    new_todo = Todos(
        title=todo.title,
        description=todo.description,
        complete=todo.complete,
        priority=todo.priority,
        owner_id=user.get("id")
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo 

@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(user: user_dependency, todo_id: int, todo: TodoRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    todo_to_update = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    todo_to_update.title = todo.title
    todo_to_update.description = todo.description
    todo_to_update.complete = todo.complete
    todo_to_update.priority = todo.priority
    db.add(todo_to_update)
    db.commit() 

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: user_dependency, todo_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    todo_to_delete = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo_to_delete)
    db.commit()
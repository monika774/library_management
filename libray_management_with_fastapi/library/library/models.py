from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str
    is_admin: bool = Field(default=False)
    # Relationships
    borrow_requests: List["BorrowRequest"] = Relationship(back_populates="user")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_name: str = Field(index=True)
    author_name: str
    publish_date: datetime
    total_copies: int
    # Relationships
    borrow_requests: List["BorrowRequest"] = Relationship(back_populates="book")

class BorrowRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    start_date: datetime
    end_date: datetime
    # is_admin: bool = Field(default=True)
    status: str = Field(default="PENDING")  # PENDING, APPROVED, DENIED, RETURNED
    # Relationships
    user: User = Relationship(back_populates="borrow_requests")
    book: Book = Relationship(back_populates="borrow_requests")

class UserCreate(SQLModel):
    email: str
    password: str

class BookCreate(SQLModel):
    book_name: str
    author_name: str
    publish_date: datetime
    total_copies: int

class BorrowRequestCreate(SQLModel):
    user_id : int
    book_id: int
    start_date: datetime
    end_date: datetime
    status: str = Field(default="PENDING")

class BorrowRequestStatusUpdate(SQLModel):
    status : str
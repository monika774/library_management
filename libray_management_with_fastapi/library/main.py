from fastapi import  FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi import  Path, Query, Body
from datetime import date
from models import  User,UserCreate, Book, BookCreate, BorrowRequest, BorrowRequestCreate, BorrowRequestStatusUpdate
from models import TokenRequest
from database import engine
from database import create_db_and_tables, get_db, get_session
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from auth import get_hashed_password, create_refresh_token, verify_password, create_access_token
from sqlmodel import Session, select

app = FastAPI(title="Library Management System")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()



@app.post("/create/users")
async def add_new_user(user: UserCreate):
     """API for creating new user """
     with Session(engine) as session:
        # if user exists
        statement = select(User).where(User.email == user.email)
        user_exist = session.exec(statement).first()
        if user_exist:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        new_user = User(email=user.email, password=user.password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"msg": f"User created successfully","user_id": new_user.id }

@app.post("/token")  
async def login_for_access_token(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(subject=db_user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/bookadd")
async def add_book(book:BookCreate):
   """API for add new book in the book list"""
   with Session(engine) as session:
        new_book = Book(
            book_name=book.book_name,
            author_name=book.author_name,
            publish_date=book.publish_date,
            total_copies=book.total_copies,
        )
        session.add(new_book)
        session.commit()
        session.refresh(new_book)  
        return {"msg": f"Book added successfully: {new_book.book_name}"}

@app.put("/book/{book_id}/")
async def update_book(book_id: int, book_update: Book):
    "API for updating book data"
    with Session(engine) as session:
        statement = select(Book).where(Book.id == book_id)
        book = session.exec(statement).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        book.book_name = book_update.book_name or book.book_name    # update book data
        book.author_name = book_update.author_name or book.author_name
        book.publish_date = book_update.publish_date or book.publish_date
        book.total_copies = book_update.total_copies or book.total_copies
        session.add(book) # save book
        session.commit()
        session.refresh(book)
        return {"msg": "Book updated successfully", "book": book}
    
@app.delete("/book/{book_id}/")
async def delete_book(book_id: int):
    """API for delete book data from database """
    with Session(engine) as session:
        statement = select(Book).where(Book.id == book_id)
        book = session.exec(statement).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(book)
        session.commit()
        return {"msg": f"Book with ID {book_id} has been deleted successfully"}
    
    
@app.post("/create-borrow-request")
async def create_borrow_request(borrow_request: BorrowRequestCreate):
    """API for create borrow request """
    print(borrow_request)
    if borrow_request.start_date >= borrow_request.end_date:
        raise HTTPException(status_code=400, detail="Please note start date must be before end date!")
    with Session(engine) as session:
        book = session.get(Book, borrow_request.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found") # find book exist or not
        user_id = borrow_request.user_id  
        print("Borrow request =", borrow_request)
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found") #find user exist or not 
        #check same request existing for purticular duration 
        request_duration = session.exec(
            select(BorrowRequest).where(
                BorrowRequest.book_id == borrow_request.book_id,
                BorrowRequest.status == "APPROVED",
                BorrowRequest.end_date >= borrow_request.start_date,
                BorrowRequest.start_date <= borrow_request.end_date
            )
        ).first()
        if request_duration:
            raise HTTPException(status_code=400, detail="Book is already borrowed during the requested period")
        new_borrow_request = BorrowRequest(
            user_id=user_id,  
            book_id=borrow_request.book_id,
            start_date=borrow_request.start_date,
            end_date=borrow_request.end_date,
            status="PENDING"   # Default status is PENDING
        )
        session.add(new_borrow_request)# Add the new borrow request to the session and commit the transaction
        try:
            session.commit()
            session.refresh(new_borrow_request)  # Refresh the newly added data
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail="Error creating borrow request: " + str(e))
        return {
            "msg": "Borrow request created successfully",
            "borrow_request": {
                "id": new_borrow_request.id,
                "book_id": new_borrow_request.book_id,
                "user_id": new_borrow_request.user_id,
                "start_date": new_borrow_request.start_date,
                "end_date": new_borrow_request.end_date,
                "status": new_borrow_request.status
            }
        }
    
@app.get("/borrow-requests")
async def get_all_borrow_requests():
    """ API for View all book borrow requests"""
    with Session(engine) as session:
        # Fetching  all borrow requests with user and book details
        statement = select(BorrowRequest).join(User).join(Book)
        borrow_requests = session.exec(statement).all()
        if not borrow_requests:
            raise HTTPException(status_code=404, detail="No borrow requests found")
        # response with (user and book details)
        return [
            {
                "id": borrow_request.id,
                "book_id" : borrow_request.book_id,
                "user_id": borrow_request.user_id,
                "start_date": borrow_request.start_date,
                "end_date": borrow_request.end_date,
                "status": borrow_request.status
            }
            for borrow_request in borrow_requests
        ]
    
@app.put("/borrow-requests/{borrow_request_id}")
async def update_borrow_request_status(borrow_request_id: int, update_request: BorrowRequestStatusUpdate):
    """API for 'APPROVED' or 'DENIED' request and added database"""
    print(borrow_request_id)
    if update_request.status not in ["APPROVED", "DENIED"]:
        raise HTTPException(status_code=400, detail="Status must be 'APPROVED' or 'DENIED'")
    with Session(engine) as session:
        borrow_request = session.get(BorrowRequest, borrow_request_id) # Fetch the borrow request by ID
        print(borrow_request)
        if not borrow_request:
            raise HTTPException(status_code=404, detail="Borrow request not found")
        borrow_request.status = update_request.status
        session.commit()  
        session.refresh(borrow_request)  
        return {
            "msg": f"Borrow request {borrow_request_id} has been {update_request.status}",
            "borrow_request": {
                "id": borrow_request.id,
                "status": borrow_request.status
            }
        }

@app.get("/users/{user_id}/borrow-history")
async def get_user_borrow_history(user_id: int):
    """API for View a user’s book borrow history i.e Fetch borrow requests for a specific user """
    with Session(engine) as session:
        statement = select(BorrowRequest).where(BorrowRequest.user_id == user_id).join(Book)
        borrow_requests = session.exec(statement).all()
        if not borrow_requests:
            raise HTTPException(status_code=404, detail="No borrow history found for this user")
        #response with book and borrow request details
        return [
            {
                "borrow_request_id": borrow_request.id,
                "book": {
                    "book_id": borrow_request.book.id,
                    "book_name": borrow_request.book.book_name,
                    "author_name": borrow_request.book.author_name
                },
                "start_date": borrow_request.start_date,
                "end_date": borrow_request.end_date,
                "status": borrow_request.status
            }
            for borrow_request in borrow_requests
        ]

@app.get("/books_view")
async def get_books():
    """API forGet list of books """
    with Session(engine) as session:
        # Fetch all books from the database
        statement = select(Book)
        books = session.exec(statement).all()
        if not books:
            raise HTTPException(status_code=404, detail="No books found")
        # response with book details
        return [
            {
                "book_id": book.id,
                "book_name": book.book_name,
                "author_name": book.author_name,
                "publish_date": book.publish_date,
                "total_copies": book.total_copies
            }
            for book in books
        ]

@app.post("/borrow-requests-for-book")
async def borrow_book(borrow_request: BorrowRequestCreate):
    """API for Submit a request to borrow a book for specific dates (date1 to date2)"""
    print(borrow_request)
    if borrow_request.start_date >= borrow_request.end_date:
        raise HTTPException(status_code=400, detail="Please note start date must be before end date!")
    with Session(engine) as session:
        book = session.get(Book, borrow_request.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        # Check if there are any existing borrow requests for this book and date range
        existing_request = session.exec(
            select(BorrowRequest).where(
                BorrowRequest.book_id == borrow_request.book_id,
                BorrowRequest.status == "APPROVED",
                BorrowRequest.end_date >= borrow_request.start_date,
                BorrowRequest.start_date <= borrow_request.end_date
            )
        ).first()
        print("hello",existing_request)
        if existing_request:
            raise HTTPException(status_code=400, detail="Book is already borrowed during the requested period")
        new_borrow_request = BorrowRequest(
            user_id=borrow_request.user_id,  
            book_id=borrow_request.book_id,
            start_date=borrow_request.start_date,
            end_date=borrow_request.end_date,
            status="PENDING"  # Default status
        )
        session.add(new_borrow_request)
        session.commit()
        session.refresh(new_borrow_request)  
        return {
            "msg": "Borrow request submitted successfully",
            "borrow_request": {
                "id": new_borrow_request.id,
                "book_id": new_borrow_request.book_id,
                "user_id": new_borrow_request.user_id,
                "start_date": new_borrow_request.start_date,
                "end_date": new_borrow_request.end_date,
                "status": new_borrow_request.status
            }
        }

@app.get("/users/{user_id}/borrow-history")
async def get_personal_borrow_history(user_id: int):
    """API for View personal book borrow history. i.e # check borrow requests for a specific user"""
    with Session(engine) as session:
        statement = select(BorrowRequest).where(BorrowRequest.user_id == user_id).join(Book)
        borrow_requests = session.exec(statement).all()
        if not borrow_requests:
            raise HTTPException(status_code=404, detail="No borrow history found for this user")
        return [
            {
                "borrow_request_id": borrow_request.id,
                "book": {
                    "book_id": borrow_request.book.id,
                    "book_name": borrow_request.book.book_name,
                    "author_name": borrow_request.book.author_name
                },
                "start_date": borrow_request.start_date,
                "end_date": borrow_request.end_date,
                "status": borrow_request.status
            }
            for borrow_request in borrow_requests
        ]
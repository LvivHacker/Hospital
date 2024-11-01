import logging
import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated, List

from database import engine, SessionLocal
import crud
import models
import schemas

app = FastAPI()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 10

db_dependency = Annotated[Session, Depends(lambda: SessionLocal())]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def register_user(user: schemas.UserCreate, db: db_dependency) -> schemas.User:
    db_user = crud.get_user(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db=db, user=user)


def authenticate_user(username: str, password: str, db: db_dependency):
    user = crud.get_user(db=db, username=username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid")


@app.get("/verify-token/{token}")
async def verify_user_token(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token=token)
    username = payload.get("sub")
    user = crud.get_user(db, username=username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_token = create_access_token({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {
        "message": "Token is valid",
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
        "access_token": new_token
    }


@app.middleware("http")
async def refresh_access_on_activity(request: Request, call_next):
    token = request.headers.get("Authorization")
    if token:
        token = token.split(" ")[1]  # remove 'Bearer' prefix
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                request.state.user = username
                new_access_token = create_access_token(
                    data={"sub": username},
                    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                )
                response = await call_next(request)
                response.headers["x-new-access-token"] = new_access_token
                return response
        except JWTError:
            pass

    return await call_next(request)

@app.get("/users", response_model=List[schemas.User],tags=["Users"])
async def list_users(db: db_dependency):
    users = crud.get_users(db=db)
    return users


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_username: str = payload.get("sub")
        if user_username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_id = crud.get_user_id(db, user_username)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

@app.put("/user/{user_id}", response_model=schemas.User,tags=["Users"])
async def update_user(user_id: int, user: schemas.UserCreate, db: db_dependency):
    db_user = crud.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/user/{user_id}", response_model=dict,tags=["Users"])
async def delete_user(user_id: int, db: db_dependency):
    result = crud.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# #### Exam Routes ####

# @app.post("/exam/", response_model=schemas.Exam, status_code=status.HTTP_201_CREATED, tags=["Exams"])
# def create_exam(
#     exam: schemas.ExamCreate,
#     db: db_dependency,
#     current_user: models.User = Depends(get_current_user)
# ):
#     if current_user.role not in ["teacher", "admin"]:
#         raise HTTPException(status_code=403, detail="You do not have permission to create an exam")

#     new_exam = models.Exam(
#         title=exam.title,
#         description=exam.description,
#         owner_id=current_user.id
#     )
#     db.add(new_exam)
#     db.commit()
#     db.refresh(new_exam)
#     return new_exam


# @app.get("/exam/{exam_id}", response_model=schemas.Exam,tags=["Exams"])
# async def read_exam(exam_id: int, db: db_dependency):
#     db_exam = crud.read_exam(db=db, exam_id=exam_id)
#     if db_exam is None:
#         raise HTTPException(status_code=404, detail="Exam not found")
#     return db_exam


# @app.put("/exam/{exam_id}", response_model=schemas.Exam, tags=["Exams"])
# async def update_exam(
#         exam_id: int,
#         exam: schemas.ExamCreate,
#         db: db_dependency,
#         current_user: models.User = Depends(get_current_user)
# ):
#     db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if db_exam is None:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if current_user.role != "admin" and db_exam.owner_id != current_user.id:
#         raise HTTPException(status_code=403, detail="You do not have permission to update this exam")

#     return crud.update_exam(db, exam_id, exam)


# @app.delete("/exam/{exam_id}",
#             response_model=dict,
#             tags=["Exams"])
# async def delete_exam(
#         exam_id: int,
#         db: db_dependency,
#         current_user: models.User = Depends(get_current_user)
# ):
#     db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if db_exam is None:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if current_user.role != "admin" and db_exam.owner_id != current_user.id:
#         raise HTTPException(status_code=403, detail="You do not have permission to delete this exam")

#     crud.delete_exam(db, exam_id)
#     return {"message": "Exam deleted successfully"}

# @app.get("/exams/",
#          tags=["Exams"])
# async def read_exams(db: db_dependency):
#     db_exams = crud.read_exams(db=db)
#     return db_exams


# ### Question Routes ###


# @app.post("/exam/{exam_id}/question/",
#           response_model=schemas.Question,
#           status_code=status.HTTP_201_CREATED,
#           tags=["Questions"])
# async def create_question(
#         question: schemas.QuestionCreate,
#         exam_id: int,
#         db: Session = Depends(get_db),
#         current_user: models.User = Depends(get_current_user)
# ):
#     db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not db_exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if db_exam.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="You do not have permission to create a question for this exam")

#     try:
#         db_question = crud.create_question(db=db, question=question, exam_id=exam_id)
#         return db_question
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create question: {str(e)}")


# @app.get("/exam/{exam_id}/question/{question_id}",tags=["Questions"])
# async def read_question(exam_id: int,question_id: int, db: Session = Depends(get_db)):
#     db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not db_exam:
#         raise HTTPException(status_code=404, detail="Exam not found")
#     result = db.query(models.Question).filter(models.Question.id == question_id).first()
#     if not result:
#         raise HTTPException(status_code=404, detail="Question not found")
#     return result


# @app.put("/exam/{exam_id}/question/{question_id}", response_model=schemas.Question, tags=["Questions"])
# async def update_question(
#         exam_id: int,
#         question_id: int,
#         question: schemas.QuestionCreate,
#         db: Session = Depends(get_db),
#         current_user: models.User = Depends(get_current_user)
# ):

#     db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()

#     if not db_exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if db_exam.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="You do not have permission to update this question")

#     db_question = crud.update_question(db, question_id, question)
#     if db_question is None:
#         raise HTTPException(status_code=404, detail="Question not found")

#     return db_question


# @app.post("/image/",tags=["Images"])
# async def upload_image(file: UploadFile = File(...)):
#     file_location = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_location, "wb") as f:
#         f.write(await file.read())
#     return {"filename": file.filename}


# @app.get("/image/{filename}",tags=["Images"])
# async def get_image(filename: str):
#     file_path = os.path.join(UPLOAD_DIR, filename)
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(file_path)

# @app.delete("/image/{filename}",tags=["Images"])
# async def delete_image(filename: str):
#     file_path = os.path.join(UPLOAD_DIR, filename)
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         return {"detail": "Image deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Image not found")


# @app.delete("/exam/{exam_id}/question/{question_id}", response_model=dict, tags=["Questions"])
# async def delete_question(
#         exam_id: int,
#         question_id: int,
#         db: db_dependency,
#         current_user: models.User = Depends(get_current_user)
# ):
#     db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()

#     if not db_exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if db_exam.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="You do not have permission to delete this question")

#     result = crud.delete_question(db, question_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Question not found")

#     return {"message": "Question deleted successfully"}


# @app.get("/exams/{exam_id}/questions", response_model=List[schemas.Question],tags=["Questions"])
# async def list_questions_by_exam(exam_id: int, db: db_dependency):

#     exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     questions = crud.get_questions_by_exam(db=db, exam_id=exam_id)

#     if not questions:
#         raise HTTPException(status_code=404, detail="No questions found for this exam")

#     return questions

# ### Choice Routes ###


# @app.post("/exam/{exam_id}/question/{question_id}/choice/", response_model=schemas.Choice,
#           status_code=status.HTTP_201_CREATED, tags=["Choices"])
# async def create_choice(
#         choice: schemas.ChoiceCreate,
#         exam_id: int,
#         question_id: int,
#         db: db_dependency,
#         current_user: models.User = Depends(get_current_user)
# ):
#     exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if exam.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="You do not have permission to create choices for this question")

#     question = db.query(models.Question).filter(models.Question.id == question_id).first()
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")

#     db_choice = crud.create_choice(db=db, choice=choice, question_id=question_id)
#     return db_choice


# @app.get("/exam/{exam_id}/question/{question_id}/choice/{choice_id}", response_model=schemas.Choice,tags=["Choices"])
# async def read_choice(exam_id: int, question_id: int,choice_id: int, db: Session = Depends(get_db)):
#     exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not exam:
#         raise HTTPException(status_code=404, detail="Exam not found")
#     question = db.query(models.Question).filter(models.Question.id == question_id).first()
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")
#     result = db.query(models.Choice).filter(models.Choice.id == choice_id).first()
#     if not result:
#         raise HTTPException(status_code=404, detail="Choice not found")
#     return result


# @app.put("/exam/{exam_id}/question/{question_id}/choice/{choice_id}", response_model=schemas.Choice, tags=["Choices"])
# async def update_choice(
#         exam_id: int,
#         question_id: int,
#         choice_id: int,
#         choice: schemas.ChoiceCreate,
#         db: db_dependency,
#         current_user: models.User = Depends(get_current_user)
# ):
#     exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if exam.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="You do not have permission to update choices for this question")

#     question = db.query(models.Question).filter(models.Question.id == question_id).first()
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")

#     db_choice = crud.update_choice(db=db, choice_id=choice_id, choice=choice)
#     if db_choice is None:
#         raise HTTPException(status_code=404, detail="Choice not found")

#     return db_choice


# @app.delete("/exam/{exam_id}/question/{question_id}/choice/{choice_id}", response_model=dict, tags=["Choices"])
# async def delete_choice(
#         exam_id: int,
#         question_id: int,
#         choice_id: int,
#         db: db_dependency,
#         current_user: models.User = Depends(get_current_user)
# ):
#     exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not exam:
#         raise HTTPException(status_code=404, detail="Exam not found")

#     if exam.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="You do not have permission to delete choices for this question")

#     question = db.query(models.Question).filter(models.Question.id == question_id).first()
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")

#     result = crud.delete_choice(db, choice_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Choice not found")

#     return {"message": "Choice deleted successfully"}


# @app.get("/exam/{exam_id}/question/{question_id}/choices",tags=["Choices"])
# async def list_choices_by_question(exam_id: int, question_id: int, db: Session = Depends(get_db)):
#     # Check if the exam exists
#     exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
#     if not exam:
#         logger.warning(f"Exam with ID {exam_id} not found")
#         raise HTTPException(status_code=404, detail="Exam not found")

#     # Check if the question belongs to the specified exam
#     question = db.query(models.Question).filter(
#         models.Question.id == question_id,
#         models.Question.exam_id == exam_id
#     ).first()

#     if not question:
#         logger.warning(f"Question with ID {question_id} not found for Exam ID {exam_id}")
#         raise HTTPException(status_code=404, detail="Question not found or does not belong to the specified exam")

#     # Retrieve the choices for the question
#     choices = db.query(models.Choice).filter(models.Choice.question_id == question_id).all()

#     if not choices:
#         logger.warning(f"No choices found for Question ID {question_id}")
#         raise HTTPException(status_code=404, detail="Choices not found for the specified question")

#     # Format the choices to match the expected response model
#     return [{"id": choice.id, "choice_text": choice.choice_text, "is_correct": choice.is_correct} for choice in choices]
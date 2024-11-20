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
SECRET_KEY = os.environ.get("SECRET_KEY", "sdh433423sd342345lklvb99034")
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

# Helper functions to check user role
def is_patient(user: models.User) -> bool:
    return user.role == "patient"

def is_doctor(user: models.User) -> bool:
    return user.role == "doctor"

def is_admin(user: models.User) -> bool:
    return user.role == "admin"

# ----------------
# User Endpoints
# ----------------
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def register_user(user: schemas.UserCreate, db: db_dependency) -> schemas.User:
    db_user = crud.get_user(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db=db, user=user)

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

# ---------------
# Admin Endpoints
# ---------------
@app.put("/doctors/{doctor_id}/confirm", response_model=schemas.User)
async def confirm_doctor_registration(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin privilege required")
    doctor = crud.get_user_by_id(db, user_id)
    if not is_doctor(doctor):
        raise HTTPException(status_code=403, detail="This user is not a doctor")
    return crud.confirm_doctor(db, user_id)

@app.get("/users", response_model=List[schemas.User])
async def list_all_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin privilege required")
    return crud.get_users(db)

# -----------------
# Patient Endpoints
# -----------------
@app.get("/doctors", response_model=List[schemas.User], tags=["Patients"])
async def list_doctors(db: Session = Depends(get_db)):
    return crud.get_doctors(db)

@app.post("/patients/{patient_id}/appointments/{doctor_id}", response_model=schemas.Meeting, tags=["Patients"])
async def request_appointment(patient_id: int, doctor_id: int, meeting_data: schemas.MeetingCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not is_patient(current_user) or current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Only patients can request appointments")
    return crud.create_meeting_request(db, meeting_data, patient_id, doctor_id)

# -----------------
# Doctor Endpoints
# -----------------
@app.put("/meetings/{meeting_id}/{status}", tags=["Doctors"])
async def confirm_meeting(meeting_id: int, status: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not is_doctor(current_user):
        raise HTTPException(status_code=403, detail="Only doctors can confirm meetings")
    request = crud.confirm_meeting(db=db, meeting_id=meeting_id, status=status)
    if isinstance(request, bool):
        return "Wrong status code!"
    return request

@app.post("/meetings/{meeting_id}/records", response_model=schemas.MedicalRecord, tags=["Doctors"])
async def create_medical_record(meeting_id: int, record_data: schemas.MedicalRecordCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not is_doctor(current_user):
        raise HTTPException(status_code=403, detail="Only doctors can create medical records")
    return crud.create_medical_record(db, meeting_id, record_data)

# ---------------
# Token Endpoints
# ---------------
def authenticate_user(username: str, password: str, db: db_dependency):
    user = crud.get_user(db=db, username=username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, role: str, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        'exp': expire,
        'iat': datetime.now(timezone.utc),  # Issued-at timestamp
        'role': role  # Add the user's role to the payload
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token", tags=['Tokens'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Pass the user's role to include it in the token payload
    access_token = create_access_token(
        data={"sub": user.username, "name": user.name, "surname": user.surname},
        role=user.role,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
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


@app.get("/verify-token/{token}", tags=['Tokens'])
async def verify_user_token(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token=token)
    username = payload.get("sub")
    user = crud.get_user(db, username=username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Pass role and name in data without using timedelta here
    new_token = create_access_token(
        data={"sub": user.username, "name": user.name, "surname": user.surname},
        role = user.role,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Pass timedelta only as an argument here
    )

    return {
        "message": "Token is valid",
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
        "surname": user.surname,
        "access_token": new_token
    }


@app.post("/refresh-token", tags=['Tokens'])
async def refresh_access_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        # if user_id is None or username is None or role is None:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        access_token = create_access_token(data={"sub": username}, role={"role": user.role})

        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")

# ---------------------
# Appointmnet Endpoints
# ---------------------
@app.get("/meetings", response_model=List[schemas.Meeting], tags=["Appointments"])
async def list_meetings(db: db_dependency):
    return crud.get_meetings(db)

@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting, tags=["Appointments"])
async def get_meeting(appointment_id: int, db: db_dependency):
    appointment = crud.get_meeting(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.put("/meetings/{meeting_id}", response_model=schemas.Meeting, tags=["Appointments"])
async def update_meeting(appointment_id: int, appointment_update: schemas.MeetingCreate, db: db_dependency):
    updated_appointment = crud.update_meeting(db, appointment_id, appointment_update)
    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment

@app.delete("/appointments/{appointment_id}", response_model=dict, tags=["Appointments"])
async def delete_meeting(appointment_id: int, db: db_dependency):
    result = crud.delete_meeting(db, appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}


# -------------------------
# Mediacl Records Endpoints
# -------------------------
@app.get("/medical_records", response_model=List[schemas.MedicalRecord], tags=["Medical Records"])
async def list_medical_records(db: db_dependency):
    return crud.get_medical_records(db)

@app.get("/medical_records/{medical_record_id}", response_model=schemas.MedicalRecord, tags=["Medical Records"])
async def get_medical_record(medical_record_id: int, db: db_dependency):
    medical_record = crud.get_medical_record(db, medical_record_id)
    if not medical_record:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    return medical_record

@app.put("/medical_records/{medical_record_id}", response_model=schemas.MedicalRecord, tags=["Medical Records"])
async def update_medical_record(
    medical_record_id: int, 
    medical_record_update: schemas.MedicalRecordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_medical_record = crud.update_medical_record(db, medical_record_id, medical_record_update)
    if not is_doctor(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can update medical records.")
    if not updated_medical_record:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    return updated_medical_record

@app.delete("/medical_records/{medical_record_id}", response_model=dict, tags=["Medical Records"])
async def delete_medical_record(medical_record_id: int, db: db_dependency):
    result = crud.delete_medical_record(db, medical_record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    return {"message": "Medical Record deleted successfully"}

# -------------------------
# Medicone Endpoints
# -------------------------
@app.post("/medical_records/{mediacl_record_id}/medicines",response_model=schemas.Medicine, tags=["Medicines"])
async def add_medicine(
    medical_record_id: int, 
    medicine_data: schemas.MedicineCreate, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not is_doctor(current_user):
        raise HTTPException(
            status_code=403, 
            detail="Only doctors can create medical records"
        )
    medical_record = crud.get_medical_record(db, medical_record_id)
    meeting = crud.get_meeting(db, medical_record.meeting_id)
    if not meeting or meeting.doctor_id != current_user.id:
        raise HTTPException(
            status_code = 403,
            detail = "You can only prescribe medicines for your own meetings."
        )
    return crud.create_medicine(db, medicine_data, medical_record_id)

@app.put("/medicines/{medicine_id}", response_model=schemas.Medicine, tags=["Medicines"])
async def update_medicine(
    medicine_id: int,
    medicine_update: schemas.Medicine,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure the current user is a doctor
    if not is_doctor(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update medicines."
        )
    
    # Validate the doctor is linked to the medicine's medical record
    medicine = crud.get_medicine_by_id(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found.")
    
    medical_record = crud.get_medical_record(db, medicine.medical_record_id)
    appointment = crud.get_meeting(db, medical_record.meeting_id)
    if appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this medicine."
        )
    # Update the medicine
    return crud.update_medicine(db, medicine_id, medicine_update)

@app.delete("/medicines/{medicine_id}", response_model=dict, tags=["Medicines"])
async def delete_medicine(
    medicine_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure the current user is a doctor
    if not is_doctor(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete medicines."
        )
    
    # Validate the doctor is linked to the medicine's medical record
    medicine = crud.get_medicine_by_id(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found.")
    
    medical_record = crud.get_medical_record(db, medicine.medical_record_id)
    appointment = crud.get_meeting(db, medical_record.meeting_id)
    if appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this medicine."
        )
    
    # Delete the medicine
    result = crud.delete_medicine(db, medicine_id)
    return {"message": "Medicine deleted successfully"}
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


# -----------------
# Patient Endpoints
# -----------------
@app.post("/patients", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED, tags=["Patients"])
async def create_patient(patient: schemas.PatientCreate, user_id: int, db: db_dependency):
    db_patient = crud.create_patient(db, patient, user_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="User not found")
    return db_patient

@app.get("/patients", response_model=List[schemas.Patient], tags=["Patients"])
async def list_patients(db: db_dependency):
    return crud.get_patients(db)

@app.get("/patients/{patient_id}", response_model=schemas.Patient, tags=["Patients"])
async def get_patient(patient_id: int, db: db_dependency):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/patients/{patient_id}", response_model=schemas.Patient, tags=["Patients"])
async def update_patient(patient_id: int, patient_update: schemas.PatientCreate, db: db_dependency):
    updated_patient = crud.update_patient(db, patient_id, patient_update)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@app.delete("/patients/{patient_id}", response_model=dict, tags=["Patients"])
async def delete_patient(patient_id: int, db: db_dependency):
    result = crud.delete_patient(db, patient_id)
    if not result:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}



# ----------------
# Doctor Endpoints
# ----------------
@app.post("/doctors", response_model=schemas.Doctor, status_code=status.HTTP_201_CREATED, tags=["Doctors"])
async def create_doctor(doctor: schemas.DoctorCreate, user_id: int, db: db_dependency):
    db_doctor = crud.create_doctor(db, doctor, user_id)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="User not found")
    return db_doctor

@app.get("/doctors", response_model=List[schemas.Doctor], tags=["Doctors"])
async def list_doctors(db: db_dependency):
    return crud.get_doctors(db)

@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor, tags=["Doctors"])
async def get_doctor(doctor_id: int, db: db_dependency):
    doctor = crud.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.put("/doctors/{doctor_id}", response_model=schemas.Doctor, tags=["Doctors"])
async def update_doctor(doctor_id: int, doctor_update: schemas.DoctorCreate, db: db_dependency):
    updated_doctor = crud.update_doctor(db, doctor_id, doctor_update)
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated_doctor

@app.delete("/doctors/{doctor_id}", response_model=dict, tags=["Doctors"])
async def delete_doctor(doctor_id: int, db: db_dependency):
    result = crud.delete_doctor(db, doctor_id)
    if not result:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted successfully"}


# ---------------------
# Appointmnet Endpoints
# ---------------------
@app.post("/appointments", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED, tags=["Appointments"])
async def create_appointment(appointment: schemas.AppointmentCreate, db: db_dependency):
    return crud.create_appointment(db, appointment)

@app.get("/appointments", response_model=List[schemas.Appointment], tags=["Appointments"])
async def list_appointments(db: db_dependency):
    return crud.get_appointments(db)

@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment, tags=["Appointments"])
async def get_appointment(appointment_id: int, db: db_dependency):
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment, tags=["Appointments"])
async def update_appointment(appointment_id: int, appointment_update: schemas.AppointmentCreate, db: db_dependency):
    updated_appointment = crud.update_appointment(db, appointment_id, appointment_update)
    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment

@app.delete("/appointments/{appointment_id}", response_model=dict, tags=["Appointments"])
async def delete_appointment(appointment_id: int, db: db_dependency):
    result = crud.delete_appointment(db, appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}


# -------------------------
# Mediacl Records Endpoints
# -------------------------
@app.post("/medical_records", response_model=schemas.MedicalRecord, status_code=status.HTTP_201_CREATED, tags=["Medical Records"])
async def create_medical_record(medical_record: schemas.MedicalRecordCreate, db: db_dependency):
    return crud.create_medical_record(db, medical_record)

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
async def update_medical_record(medical_record_id: int, medical_record_update: schemas.MedicalRecordCreate, db: db_dependency):
    updated_medical_record = crud.update_medical_record(db, medical_record_id, medical_record_update)
    if not updated_medical_record:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    return updated_medical_record

@app.delete("/medical_records/{medical_record_id}", response_model=dict, tags=["Medical Records"])
async def delete_medical_record(medical_record_id: int, db: db_dependency):
    result = crud.delete_medical_record(db, medical_record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    return {"message": "Medical Record deleted successfully"}

# ---------------
# Token Endpoints
# ---------------
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
        "name": user.full_name,
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
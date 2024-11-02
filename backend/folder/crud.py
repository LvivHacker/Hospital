from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# User Management
# -------------------------

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_id(db: Session, username: str) -> Optional[int]:
    user = get_user(db, username)
    return user.id if user else None

def update_user(db: Session, user_id: int, user_update: schemas.UserCreate) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    db_user.username = user_update.username
    db_user.email = user_update.email
    db_user.hashed_password = pwd_context.hash(user_update.password)
    db_user.name = user_update.name
    db_user.surname = user_update.surname
    db_user.role = user_update.role

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True

def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()

# -------------------------
# Patient Management
# -------------------------

def create_patient(db: Session, patient: schemas.PatientCreate, user_id: int) -> models.Patient:
    db_patient = models.Patient(
        user_id=user_id,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        phone_number=patient.phone_number,
        address=patient.address,
        medical_history=patient.medical_history
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientCreate) -> Optional[models.Patient]:
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        return None

    db_patient.date_of_birth = patient_update.date_of_birth
    db_patient.gender = patient_update.gender
    db_patient.phone_number = patient_update.phone_number
    db_patient.address = patient_update.address
    db_patient.medical_history = patient_update.medical_history

    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int) -> bool:
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        return False

    db.delete(db_patient)
    db.commit()
    return True

# Add similar methods for Doctor, Appointment, and MedicalRecord following the same pattern.

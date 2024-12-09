from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
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
        name=user.name,
        surname=user.surname,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

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

def confirm_doctor(db: Session, doctor_id: int) -> models.User:
    db_doctor = db.query(models.User).filter(models.User.id == doctor_id).first()
    db_doctor.is_confirmed = True
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

# def get_doctor(db: Session) -> List[models.User]:
#     return db.query(models.User).all()

def get_doctors(db: Session) -> List[models.User]:
    return db.query(models.User).filter(models.User.role == "doctor").all()

def get_patients(db: Session) -> List[models.User]:
    return db.query(models.User).filter(models.User.role == "patient").all()

def get_confirmed_doctors(db: Session) -> List[models.User]:
    return db.query(models.User).filter(models.User.role == "doctor", models.User.is_confirmed == True).all()

# -------------------------
# Meeting Management
# -------------------------

def create_meeting_request(db: Session, meeting_data: schemas.MeetingCreate, patient_id: int, doctor_id: int) -> models.Meeting:
    db_meeting = models.Meeting(
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_date=meeting_data.scheduled_date,
        status="Pending",
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

def confirm_meeting(db: Session, meeting_id: int, status: int,) -> Optional[models.Meeting]:
    # Map integer status codes to string values
    status_mapping = {
        1: "Reject",
        2: "Confirmed"
    }
    # Validate the status value
    if status not in status_mapping:
        return False
    # Fetch the meeting from the database
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not db_meeting:
        return None
    # Update the meeting status
    db_meeting.status = status_mapping[status]
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def get_meeting(db: Session, meeting_id: int) -> Optional[models.Meeting]:
    return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()

def get_meetings(db: Session) -> List[models.Meeting]:
    return db.query(models.Meeting).all()

def update_meeting(db: Session, meeting_id: int, meeting_update: schemas.MeetingCreate) -> Optional[models.Meeting]:
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not db_meeting:
        return None

    db_meeting.scheduled_date = meeting_update.scheduled_date
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

def delete_meeting(db: Session, meeting_id: int) -> bool:
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not db_meeting:
        return False

    db.delete(db_meeting)
    db.commit()
    return True

# -------------------------
# Medical Record Management
# -------------------------

def create_medical_record(db: Session, meeting_id: int, record_data: schemas.MedicalRecordCreate) -> models.MedicalRecord:
    db_record = models.MedicalRecord(
        meeting_id=meeting_id,
        description=record_data.description,
        created_at=datetime.utcnow(),
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_medical_record(db: Session, record_id: int) -> Optional[models.MedicalRecord]:
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()

def get_medical_records(db: Session) -> List[models.MedicalRecord]:
    return db.query(models.MedicalRecord).all()

def update_medical_record(db: Session, record_id: int, description: str) -> Optional[models.MedicalRecord]:
    db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not db_record:
        return None

    db_record.description = description  # Update the description
    db.commit()  # Commit the transaction
    db.refresh(db_record)  # Refresh the instance with updated values
    return db_record


def delete_medical_record(db: Session, record_id: int) -> bool:
    db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not db_record:
        return False

    db.delete(db_record)
    db.commit()
    return True

# -------------------------
# Medicine Management
# -------------------------

def create_medicine(db: Session, medicine_data: schemas.MedicineCreate, medical_record_id: int) -> models.Medicine:
    db_medicine = models.Medicine(
        name=medicine_data.name,
        dosage=medicine_data.dosage,
        frequency=medicine_data.frequency,
        medical_record_id=medical_record_id,
    )
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def get_medicines_by_medical_record(db: Session, medical_record_id: int) -> List[models.Medicine]:
    return db.query(models.Medicine).filter(models.Medicine.medical_record_id == medical_record_id).all()

def get_medicine_by_id(db: Session, medicine_id: int) -> Optional[models.Medicine]:
    return db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()

def get_medicines(db: Session) -> List[models.Medicine]:
    return db.query(models.Medicine).all()

def update_medicine(db: Session, medicine_id: int, medicine_update: schemas.Medicine) -> Optional[models.Medicine]:
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        return None

    for key, value in medicine_update.dict(exclude_unset=True).items():
        setattr(db_medicine, key, value)

    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def delete_medicine(db: Session, medicine_id: int) -> bool:
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        return False

    db.delete(db_medicine)
    db.commit()
    return True

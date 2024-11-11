from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas
from datetime import datetime

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
        role=user.role,
        full_name=user.full_name
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
    db_user.full_name = user_update.full_name
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

def get_patients(db: Session) -> List[models.Patient]:
    patients = db.query(models.Patient).all()
    response = []
    for patient in patients:
        response.append({
            "id": patient.id,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "phone_number": patient.phone_number,
            "address": patient.address,
            "medical_history": patient.medical_history,
            "user_id": patient.user_id
        })
    return response

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

def get_patient_appointments(db: Session, patient_id: int) -> List[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()

# -------------------------
# Doctor Management
# -------------------------

def create_doctor(db: Session, doctor: schemas.DoctorCreate, user_id: int):
    db_doctor = models.Doctor(
        user_id=user_id,
        specialty=doctor.specialty,
        phone_number=doctor.phone_number,
        address=doctor.address
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctors(db: Session) -> List[models.Doctor]:
    return db.query(models.Doctor).all()

def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorCreate):
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        return None

    db_doctor.specialty = doctor_update.specialty
    db_doctor.phone_number = doctor_update.phone_number
    db_doctor.address = doctor_update.address

    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def delete_doctor(db: Session, doctor_id: int):
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        return None

    db.delete(db_doctor)
    db.commit()
    return True

# def confirm_doctor_registration(db: Session, doctor_id: int, doctor_update: schemas.DoctorCreate):
#     db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
#     if not db_doctor:
#         return None
#     # Placeholder for any specific actions for confirming a doctor
#     db.commit()
#     return db_doctor

# -------------------------
# Appointment Management
# -------------------------

# def create_appointment(db: Session, appointment: schemas.AppointmentCreate, doctor_id: int, patient_id: int):
#     db_appointment = models.Appointment(
#         patient_id=patient_id,
#         doctor_id=doctor_id,
#         appointment_date=appointment.appointment_date,
#         reason=appointment.reason
#     )
#     db.add(db_appointment)
#     db.commit()
#     db.refresh(db_appointment)
#     return db_appointment

def create_appointment_request(db: Session, patient_id: int, doctor_id: int, appointment_data: schemas.AppointmentCreate):
    db_appointment = models.Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_data.appointment_date,
        reason=appointment_data.reason
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def confirm_appointment(db: Session, appointment_id: int):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        return None
    # Placeholder for setting appointment confirmation details if needed
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_appointments(db: Session) -> List[models.Appointment]:
    return db.query(models.Appointment).all()

def update_appointment(db: Session, appointment_id: int, appointment_update: schemas.AppointmentCreate):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        return None

    db_appointment.patient_id = appointment_update.patient_id
    db_appointment.doctor_id = appointment_update.doctor_id
    db_appointment.appointment_date = appointment_update.appointment_date
    db_appointment.reason = appointment_update.reason

    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        return None

    db.delete(db_appointment)
    db.commit()
    return True

# -------------------------
# Medical Record Management
# -------------------------

def create_medical_record(db: Session, appointment_id: int, record_data: schemas.MedicalRecordCreate):
    db_record = models.MedicalRecord(
        appointment_id=appointment_id,
        description=record_data.description,
        doctor_id=record_data.doctor_id,
        created_at=datetime.utcnow()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_medical_record(db: Session, record_id: int):
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()

def get_medical_records(db: Session) -> List[models.MedicalRecord]:
    return db.query(models.MedicalRecord).all()

def update_medical_record(db: Session, record_id: int, description: str):
    db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not db_record:
        return None

    db_record.description = description
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_medical_record(db: Session, record_id: int):
    db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not db_record:
        return None

    db.delete(db_record)
    db.commit()
    return True

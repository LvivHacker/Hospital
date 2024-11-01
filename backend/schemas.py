from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime
import enum

# Enum for User Roles
class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

# Base Schema for User
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True  # Enables compatibility with ORMs like SQLAlchemy

# Schema for Creating a User
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole

# Base Schema for Patient
class Patient(BaseModel):
    id: int
    date_of_birth: date
    gender: str
    phone_number: str
    address: str
    medical_history: Optional[str] = None
    user_id: int  # Linking to the User model

    class Config:
        from_attributes = True

# Schema for Creating a Patient
class PatientCreate(BaseModel):
    date_of_birth: date
    gender: str
    phone_number: str
    address: str
    medical_history: Optional[str] = None

# Base Schema for Doctor
class Doctor(BaseModel):
    id: int
    specialty: str
    phone_number: str
    address: str
    user_id: int  # Linking to the User model

    class Config:
        from_attributes = True

# Schema for Creating a Doctor
class DoctorCreate(BaseModel):
    specialty: str
    phone_number: str
    address: str

# Base Schema for Appointment
class Appointment(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: str
    medical_records: List['MedicalRecord'] = []  # Linking Medical Records

    class Config:
        from_attributes = True

# Schema for Creating an Appointment
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: str

# Base Schema for Medical Record
class MedicalRecord(BaseModel):
    id: int
    appointment_id: int
    description: str
    created_at: datetime
    doctor_id: int  # Linking to the Doctor who created the record

    class Config:
        from_attributes = True

# Schema for Creating a Medical Record
class MedicalRecordCreate(BaseModel):
    appointment_id: int
    description: str
    created_at: datetime
    doctor_id: int  # Linking to the Doctor who created the record
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
    name: str  # First name
    surname: str  # Last name
    role: UserRole

    class Config:
        from_attributes = True

# Schema for Creating a User
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole
    name: str  # First name
    surname: str  # Last name

# Base Schema for Meeting
class Meeting(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_date: datetime
    status: str
    medical_records: List['MedicalRecord'] = []

    class Config:
        from_attributes = True

# Schema for Creating a Meeting
class MeetingCreate(BaseModel):
    # doctor_id: int
    scheduled_date: datetime

# Base Schema for Medical Record
class MedicalRecord(BaseModel):
    id: int
    meeting_id: int
    description: Optional[str]
    created_at: datetime
    medicines: List['Medicine'] = []

    class Config:
        from_attributes = True

# Schema for Creating a Medical Record
class MedicalRecordCreate(BaseModel):
    description: Optional[str] = None

# Base Schema for Medicine
class Medicine(BaseModel):
    id: int
    name: str
    dosage: float
    frequency: str
    medical_record_id: int

    class Config:
        from_attributes = True

# Schema for Creating Medicine
class MedicineCreate(BaseModel):
    name: str
    dosage: float
    frequency: str

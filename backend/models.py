from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

# # Enum for User Roles
# class UserRole(str, enum.Enum):
#     admin = "admin"
#     doctor = "doctor"
#     patient = "patient"

# User model with roles and active status
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)  # First Name
    surname = Column(String, nullable=False)  # Last Name
    hashed_password = Column(String)
    is_confirmed = Column(Boolean, default=False)  # Required for doctors
    role = Column(String, nullable=False)

    # Relationships
    meetings_as_patient = relationship('Meeting', back_populates='patient', foreign_keys='Meeting.patient_id',  cascade="all, delete")
    meetings_as_doctor = relationship('Meeting', back_populates='doctor', foreign_keys='Meeting.doctor_id',  cascade="all, delete")

# Meeting model linking patients and doctors
class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('users.id'))
    doctor_id = Column(Integer, ForeignKey('users.id'))
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String, default="Pending")  # Pending, Confirmed, Rescheduled, or Cancelled

    # Relationships
    patient = relationship('User', back_populates='meetings_as_patient', foreign_keys=[patient_id])
    doctor = relationship('User', back_populates='meetings_as_doctor', foreign_keys=[doctor_id])
    medical_records = relationship('MedicalRecord', back_populates='meeting', cascade="all, delete")

# Medical Record model for a meeting
class MedicalRecord(Base):
    __tablename__ = 'medical_records'

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    meeting = relationship('Meeting', back_populates='medical_records', foreign_keys=[meeting_id])
    medicines = relationship('Medicine', back_populates='medical_record', cascade="all, delete")

# Medicine model linked to a medical record
class Medicine(Base):
    __tablename__ = 'medicines'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dosage = Column(Float, nullable=False)  # Example: 250.0 (mg)
    frequency = Column(String, nullable=False)  # Example: "Twice a day"
    medical_record_id = Column(Integer, ForeignKey('medical_records.id'), nullable=False)

    # Relationships
    medical_record = relationship('MedicalRecord', back_populates='medicines', foreign_keys=[medical_record_id])

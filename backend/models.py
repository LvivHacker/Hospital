from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

# Enum for User Roles
class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

# User model with roles and active status
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))

    # Relationships to Patient and Doctor models, one-to-one
    patient = relationship('Patient', back_populates='user', uselist=False)
    doctor = relationship('Doctor', back_populates='user', uselist=False)

# Patient model with medical history and appointment relationship
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, index=True)
    date_of_birth = Column(Date)
    gender = Column(String)
    phone_number = Column(String)
    address = Column(String)
    medical_history = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    user = relationship('User', back_populates='patient')
    appointments = relationship('Appointment', back_populates='patient')

# Doctor model with confirmation and appointment/medical record relationships
class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True, index=True)
    specialty = Column(String)
    phone_number = Column(String)
    address = Column(String)
    is_confirmed = Column(Boolean, default=False)  # Added confirmation field
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    user = relationship('User', back_populates='doctor')
    appointments = relationship('Appointment', back_populates='doctor')
    medical_records = relationship('MedicalRecord', back_populates='doctor')

# Appointment model with cascade delete for related MedicalRecords
class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    appointment_date = Column(DateTime)
    reason = Column(String)

    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('Doctor', back_populates='appointments')
    medical_records = relationship('MedicalRecord', back_populates='appointment', cascade="all, delete")

# Medical Record model with doctor relationship
class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))

    appointment = relationship('Appointment', back_populates='medical_records')
    doctor = relationship('Doctor', back_populates='medical_records')

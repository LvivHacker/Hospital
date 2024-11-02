from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole))

    patient = relationship('Patient', back_populates='user', uselist=False)
    doctor = relationship('Doctor', back_populates='user', uselist=False)

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

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True, index=True)
    specialty = Column(String)
    phone_number = Column(String)
    address = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    user = relationship('User', back_populates='doctor')
    appointments = relationship('Appointment', back_populates='doctor')
    medical_records = relationship('MedicalRecord', back_populates='doctor')

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    appointment_date = Column(DateTime)
    reason = Column(String)

    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('Doctor', back_populates='appointments')
    medical_records = relationship('MedicalRecord', back_populates='appointment')

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))

    appointment = relationship('Appointment', back_populates='medical_records')
    doctor = relationship('Doctor', back_populates='medical_records')
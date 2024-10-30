from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    address = Column(String)
    date_of_birth = Column(Date)

    user = relationship("User", back_populates="patient")

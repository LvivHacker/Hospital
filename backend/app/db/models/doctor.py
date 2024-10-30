from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    specialization = Column(String)
    license_number = Column(String)

    user = relationship("User", back_populates="doctor")

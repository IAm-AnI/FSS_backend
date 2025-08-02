from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_number = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    registrations = relationship("Registration", back_populates="user", uselist=False)
    registered_courses = relationship("RegisteredCourse", back_populates="user")

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    registration_status = Column(String, default="Pending")
    abc_id = Column(String, nullable=False)
    user_enrollment_number = Column(String, ForeignKey("users.enrollment_number"), nullable=False)
    faculty_number = Column(String, unique=True, index=True, nullable=False)
    gender = Column(String, nullable=False)
    programme_name = Column(String, nullable=False)
    major_allotted_subject = Column(String, nullable=False)
    minor_allotted_subject = Column(String, nullable=False)
    generic_allotted_subject = Column(String, nullable=False)
    
    user = relationship("User", back_populates="registrations")
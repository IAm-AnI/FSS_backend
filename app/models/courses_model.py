from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import relationship
from app.config.database import Base

class RegisteredCourse(Base):
    __tablename__ = "registered_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_enrollment_number = Column(String, ForeignKey("users.enrollment_number"), nullable=False)
    semester = Column(Integer, index=True) 
    vac = Column(String, nullable=False)
    vac_papercode = Column(String, ForeignKey("vac_courses.course_code"))
    voc = Column(String, nullable=False)
    voc_papercode = Column(String, ForeignKey("voc_courses.course_code"))
    
    user = relationship("User", back_populates="registered_courses")
    voc_course = relationship("VOC")
    vac_course = relationship("VAC")
 
class VOC(Base):
    __tablename__ = "voc_courses"
    
    semester = Column(Integer)
    course_code = Column(String, primary_key=True, index=True)
    course_name = Column(String, index=True)    
    department_name = Column(String, index=True)    
    total_seats = Column(Integer)
    registered_seats = Column(Integer, default=0, server_default=text("0"))
    
class VAC(Base):
    __tablename__ = "vac_courses"
    
    semester = Column(Integer)
    course_code = Column(String, primary_key=True, index=True)
    course_name = Column(String, index=True)   
    department_name = Column(String, index=True) 
    total_seats = Column(Integer)
    registered_seats = Column(Integer, default=0, server_default=text("0"))
from pydantic import BaseModel

class UserCreate(BaseModel):
    enrollment_number: str
    phone_number: str
    otp: str
    password: str
    
class UserLogin(BaseModel):
    enrollment_number: str
    password: str

class OTPSendRequest(BaseModel):
    phone_number: str
    
class UserDetailsRequest(BaseModel):
    name: str
    abc_id: str
    faculty_number: str
    gender: str
    programme_name: str
    major_allotted_subject: str
    minor_allotted_subject: str
    generic_allotted_subject: str
    
class UserCoursesRequest(BaseModel):
    semester: int
    vac: str
    vac_papercode: str
    voc: str
    voc_papercode: str
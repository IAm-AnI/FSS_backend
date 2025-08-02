from fastapi import APIRouter, Depends, HTTPException, status, Request # Add Request here
from app.config.logger import logger
from app.schemas import user_schema
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config.db_dependency import get_db
from app.models.users_model import User
from app.config.twilio import send_sms
import random, re
from typing import Tuple, Optional

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
otp_storage = {}

def hash_password(password: str):
    return pwd_context.hash(password)

def normalize_phone_number(phone_number: str, country_code: str = "91") -> Optional[Tuple[str, str]]:
    digits = re.sub(r'\D', '', phone_number)
    
    if digits.startswith(country_code):
        base_number = digits[len(country_code):]
    elif digits.startswith('0'):
        base_number = digits[1:]
    else:
        base_number = digits

    if len(base_number) == 10:
        # Creating the E.164 format
        e164_format = f"+{country_code}{base_number}"
        return (base_number, e164_format)
        
    return None

@router.get("/")
async def hello_user():
    logger.info("Authentication route accessed")
    return {
        "status": "success",
        "message": "User can authenticate"
    }

@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(request: user_schema.OTPSendRequest, db: Session = Depends(get_db)):
    try:
        result = normalize_phone_number(request.phone_number)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check your number and try again"
            )
        base_number, normalized_phone = result
        
        existing_user = db.query(User).filter(User.phone_number == base_number).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this phone number already exists."
            )
        
        otp = str(random.randint(100000, 999999))
        otp_storage[base_number] = otp

        print(f"OTP for {normalized_phone}: {otp}")
        message_body = f"Your verification code is: {otp}. It is valid for 5 minutes."
        sms_sent = send_sms(to_number=normalized_phone, body=message_body)

        if not sms_sent:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to send OTP. Please try again later."
            )
        
        return {
            "success": True,
            "message": "OTP sent successfully. It is valid for 5 minutes."
        }
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error while generating otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Something went wrong, try again"
        )
    
@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_new_user(request: Request, user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    try:
        result = normalize_phone_number(user_data.phone_number)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check your number and try again"
            )
        base_number, _ = result
        
        stored_otp = otp_storage.get(base_number)
        if not stored_otp or stored_otp != user_data.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP."
            )

        if db.query(User).filter(User.enrollment_number == user_data.enrollment_number).first():
            del otp_storage[base_number]
            raise HTTPException(status_code=400, detail="Enrollment number already registered")
        if db.query(User).filter(User.phone_number == base_number).first():
            del otp_storage[base_number]
            raise HTTPException(status_code=400, detail="Phone number already registered")

        hashed_password = hash_password(user_data.password)

        new_user = User(
            enrollment_number=user_data.enrollment_number,
            phone_number=base_number,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        del otp_storage[base_number]
        
        request.state.session['enrollment_number'] = new_user.enrollment_number
        logger.info(f"User {new_user.enrollment_number} created successfully.")

        return {
            "success" : True,
            "message": "User created successfully."
        }
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error while generating otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Something went wrong, try again"
        )

@router.post("/login-user", status_code=status.HTTP_200_OK)
def user_login(request: Request, user_data: user_schema.UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.enrollment_number == user_data.enrollment_number).first()

        if not user or not pwd_context.verify(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect enrollment number or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        request.state.session['enrollment_number'] = user.enrollment_number
        logger.info(f"User {user.enrollment_number} logged in successfully.")

        return {
            "success": True,
            "message": "Login successful."
        }
    
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during login for {user_data.enrollment_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred. Try Again."
        )

@router.post("/logout")
def user_logout(request: Request):
    try:
        # logger.info(f"request.state.session: {request.state.session}")
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot logout because you are not logged in."
            )
        # user_identifier = request.state.session.get("enrollment_number", "Unknown user")
        request.state.session.clear()
       
        logger.info(f"User logged out successfully.")
        return {
            "success": True, 
            "message": "Successfully logged out."
        }
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )

@router.post("/update-password")
def password_update(request: Request):
    pass
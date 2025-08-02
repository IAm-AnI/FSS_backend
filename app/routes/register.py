from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.logger import logger
from app.schemas import user_schema
from app.config.db_dependency import get_db
from app.models.users_model import User, Registration
from app.models.courses_model import RegisteredCourse, VAC, VOC

router = APIRouter()

@router.get("/")
async def check_register():
    logger.info("Registration route accessed")
    return {
        "status": "success",
        "message": "User can register"
    }

@router.post("/user-details")
async def add_user_details(user_details: user_schema.UserDetailsRequest, request: Request, db: Session = Depends(get_db)):
    try:
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot register because you are not logged in."
            )
        session = request.state.session
        enrollment_number = session.get("enrollment_number")
        if enrollment_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Enrollment number not found in session."
            )
        
        existing_registration = db.query(Registration).filter(
            Registration.user_enrollment_number == enrollment_number
        ).first()

        if existing_registration:
            existing_registration.name = user_details.name
            existing_registration.abc_id = user_details.abc_id
            existing_registration.faculty_number = user_details.faculty_number
            existing_registration.gender = user_details.gender
            existing_registration.programme_name = user_details.programme_name
            existing_registration.major_allotted_subject = user_details.major_allotted_subject
            existing_registration.minor_allotted_subject = user_details.minor_allotted_subject
            existing_registration.generic_allotted_subject = user_details.generic_allotted_subject
            db.commit()
            db.refresh(existing_registration)
        else:
            details = Registration(
                name=user_details.name,
                registration_status="Partial",
                abc_id=user_details.abc_id,
                user_enrollment_number=enrollment_number,
                faculty_number=user_details.faculty_number,
                gender=user_details.gender,
                programme_name=user_details.programme_name,
                major_allotted_subject=user_details.major_allotted_subject,
                minor_allotted_subject=user_details.minor_allotted_subject,
                generic_allotted_subject=user_details.generic_allotted_subject
            )
            db.add(details)
            db.commit()
            db.refresh(details)
        
        return {
            "success": True, 
            "message": "Basic registration completed."
        }
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during basic registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )

@router.post("/user-courses")
async def add_user_courses(user_courses: user_schema.UserCoursesRequest, request: Request, db: Session = Depends(get_db)):
    try:
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot register because you are not logged in."
            )
        session = request.state.session
        enrollment_number = session.get("enrollment_number")
        if enrollment_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Enrollment number not found in session."
            )
        
        course = RegisteredCourse(
            user_enrollment_number=enrollment_number,
            semester=user_courses.semester,
            vac=user_courses.vac,
            vac_papercode=user_courses.vac_papercode,
            voc=user_courses.voc,
            voc_papercode=user_courses.voc_papercode
        )
        
        db.query(VAC).filter(
            VAC.course_code == user_courses.vac_papercode,
            VAC.semester == user_courses.semester
        ).update({
            VAC.registered_seats: VAC.registered_seats + 1
        })
        
        db.query(VOC).filter(
            VOC.course_code == user_courses.voc_papercode,
            VOC.semester == user_courses.semester
        ).update({
            VOC.registered_seats: VOC.registered_seats + 1
        })
        
        db.query(Registration).filter(
            Registration.user_enrollment_number == enrollment_number
        ).update({
            Registration.registration_status: "Completed"
        })

        db.add(course)
        db.commit()
        db.refresh(course)
        
        return {
            "success": True, 
            "message": "Courses registration completed."
        }
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during courses registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Type correct courses details"
        )
        
@router.get("/check-registration")
async def add_user_courses(request: Request, db: Session = Depends(get_db)):
    try:
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot register because you are not logged in."
            )
        session = request.state.session
        enrollment_number = session.get("enrollment_number")
        
        record = db.query(Registration).filter(Registration.user_enrollment_number == enrollment_number).first()

        if record:
            return {
                "success": True, 
                "message": record.registration_status
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Something went wrong, try again."
            )
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during courses registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, try again."
        )

@router.post("/registration-data")
async def add_user_details(request: Request, db: Session = Depends(get_db)):
    try:
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot register because you are not logged in."
            )
        session = request.state.session
        enrollment_number = session.get("enrollment_number")
        if enrollment_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Enrollment number not found in session."
            )
            
        user_registration_details = db.query(Registration).filter(
            Registration.user_enrollment_number == enrollment_number
        ).all()
        
        if not user_registration_details:
            return {}
        else:
            return user_registration_details[0]
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during courses registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, try again."
        )

@router.get("/complete-registration-data")
async def add_user_details(request: Request, db: Session = Depends(get_db)):
    try:
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot register because you are not logged in."
            )
        session = request.state.session
        enrollment_number = session.get("enrollment_number")
        if enrollment_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Enrollment number not found in session."
            )
        
        user_registration_details = db.query(Registration).filter(
            Registration.user_enrollment_number == enrollment_number
        ).first()
        
        phone_number = db.query(User).filter(
            User.enrollment_number == enrollment_number
        ).first()
        
        registered_courses = db.query(RegisteredCourse).filter(
            RegisteredCourse.user_enrollment_number == enrollment_number
        ).order_by(RegisteredCourse.semester.asc()).all()

        semester_I = 0
        vac_I = vac_papercode_I = voc_I = voc_papercode_I = ""
        semester_II = 0
        vac_II = vac_papercode_II = voc_II = voc_papercode_II = ""

        if len(registered_courses) > 0:
            first = registered_courses[0]
            semester_I = first.semester
            vac_I = first.vac
            vac_papercode_I = first.vac_papercode
            voc_I = first.voc
            voc_papercode_I = first.voc_papercode

        if len(registered_courses) > 1:
            second = registered_courses[1]
            semester_II = second.semester
            vac_II = second.vac
            vac_papercode_II = second.vac_papercode
            voc_II = second.voc
            voc_papercode_II = second.voc_papercode
        
        response_data = {
            "name": user_registration_details.name,
            "id": user_registration_details.id,
            "user_enrollment_number": user_registration_details.user_enrollment_number,
            "mobile_no": phone_number,
            "gender": user_registration_details.gender,
            "programme_name": user_registration_details.programme_name,
            "minor_allotted_subject": user_registration_details.minor_allotted_subject,
            "abc_id": user_registration_details.abc_id,
            "registration_status": user_registration_details.registration_status,
            "faculty_number": user_registration_details.faculty_number,
            "major_allotted_subject": user_registration_details.major_allotted_subject,
            "generic_allotted_subject": user_registration_details.generic_allotted_subject,
            "semester_I": semester_I,
            "vac_I": vac_I,
            "vac_papercode_I": vac_papercode_I,
            "voc_I": voc_I,
            "voc_papercode_I": voc_papercode_I,
            "semester_II": semester_II,
            "vac_II": vac_II,
            "vac_papercode_II": vac_papercode_II,
            "voc_II": voc_II,
            "voc_papercode_II": voc_papercode_II,
        }
        logger.info(response_data)
        return response_data
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during courses registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, try again."
        )
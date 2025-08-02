from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.logger import logger
from app.schemas import course_schema
from app.config.db_dependency import get_db
from app.models.courses_model import VAC, VOC

router = APIRouter()

@router.get("/")
async def check_courses():
    logger.info("Courses route accessed")
    return {
        "status": "success",
        "message": "User can choose courses"
    }

@router.post("/courses-list")
async def get_courses_list(request: Request, course_data: course_schema.CoursesListRequest, db: Session = Depends(get_db)):
    try:
        if not request.state.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot register because you are not logged in."
            )
        if course_data.courses_type == 'VAC':
            courses = db.query(VAC).filter(
                VAC.semester == course_data.semester,
                VAC.registered_seats < VAC.total_seats
            ).all()
        elif course_data.courses_type == 'VOC':
            courses = db.query(VOC).filter(
                VOC.semester == course_data.semester,
                VOC.registered_seats < VOC.total_seats
            ).all()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid courses_type. Must be 'VAC' or 'VOC'"
            )
        logger.info("It is working here")
        courses_list = []
        for course in courses:
            courses_list.append({
                "name": course.course_name,
                "papercode": course.course_code,
                "department_name": course.department_name,
                "available_seats": course.total_seats - course.registered_seats,
                "total_seats": course.total_seats
            })
        
        return courses_list
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error during courses list fetch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )
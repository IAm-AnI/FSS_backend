from pydantic import BaseModel

class CoursesListRequest(BaseModel):
    semester: int
    courses_type: str
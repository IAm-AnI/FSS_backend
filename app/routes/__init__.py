from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.register import router as register_router
from app.routes.courses import router as courses_router

def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix="/v1/api/auth")
    app.include_router(register_router, prefix="/v1/api/register")
    app.include_router(courses_router, prefix="/v1/api/courses")


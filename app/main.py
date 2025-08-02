from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.db_session_middleware import DBSessionMiddleware
# from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings
from app.config.database import engine, Base
from contextlib import asynccontextmanager
from app.config.database import db, engine, Base
from app.models.users_model import User, Registration
from app.models.courses_model import RegisteredCourse, VOC, VAC
from app.config.logger import logger
from app.routes import register_routers
from starlette.exceptions import HTTPException as StarletteHTTPException

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # On startup
#     Base.metadata.create_all(bind=engine)
#     await db.connect()
#     print("Database connection pool established.")
#     yield
#     # On shutdown
#     await db.disconnect()
#     print("Database connection pool closed.")


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
Base.metadata.create_all(bind=engine)

allowed_origins = [origin.strip() for origin in settings.FRONTEND_ORIGIN.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware)
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=settings.SESSION_SECRET,
#     session_cookie="session",
#     same_site="none" if settings.ENV == "production" else "lax",
#     https_only=(settings.ENV == "production"),
#     max_age=3600 * 24 * 7,
# )

register_routers(app)

@app.get("/")
async def read_root():
    return {"message": "Welcome!"}

@app.get("/health")
async def health():
    logger.info("Health check accessed")
    return {"status": "healthy"}

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from app.config.db_dependency import get_db
from app.models.session_model import SessionData
import uuid
from datetime import datetime, timedelta, timezone
from app.config.settings import settings

class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        db: Session = next(get_db())
        session_key = request.cookies.get(settings.SESSION_SECRET)
        
        request.state.session = {}
        initial_session_data = {}

        if session_key:
            session_record = db.query(SessionData).filter(
                SessionData.session_key == session_key,
                SessionData.expires > datetime.utcnow()
            ).first()
            if session_record:
                request.state.session = session_record.data
                initial_session_data = dict(session_record.data)

        response = await call_next(request)

        final_session_data = request.state.session
        if final_session_data != initial_session_data:
            
            if not final_session_data and session_key:
                db.query(SessionData).filter(SessionData.session_key == session_key).delete()
                response.delete_cookie(settings.SESSION_SECRET)
            
            else:
                new_key = session_key or str(uuid.uuid4())
                IST = timezone(timedelta(hours=5, minutes=30))
                expires = datetime.now(IST) + timedelta(days=1) # 7-day lifetime

                db.merge(SessionData(session_key=new_key, data=final_session_data, expires=expires))
                
                response.set_cookie(
                    key=settings.SESSION_SECRET,
                    value=new_key,
                    max_age=3600 * 24 * 7,  # 7 days
                    httponly=False if settings.ENV == 'production' else True,
                    samesite="none" if settings.ENV == 'production' else "lax",
                    secure=True if settings.ENV == 'production' else False,
                    path="/",
                )
            
            db.commit()
            
        db.close()
        return response
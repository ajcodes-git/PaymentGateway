from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories import app_client_repository
from app.utils import hashing

security = HTTPBearer()

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> bool:
    api_key = credentials.credentials
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key not provided"
        )
    
    # Query the database for the API key
    app_client = app_client_repository.get_active(db, api_key)
    
    if not app_client:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key"
        )
    
    return app_client.name
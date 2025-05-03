from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.app_client import AppClientRequest
from app.services import app_client as app_client_service
from app.db.session import get_db
from app.utils.response import response


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_app_client(
    request: Request,
    app_client_in: AppClientRequest,
    db: Session = Depends(get_db),
):
    """Create new app client"""
    return app_client_service.create_app_client(db, app_client_in)

@router.get("/{app_client_id}")
def get_app_client(
    request: Request,
    app_client_id: str,
    db: Session = Depends(get_db),
):
    """Get app client by ID"""
    return app_client_service.get_app_client(db, app_client_id)

@router.get("/")
def get_app_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of app clients with pagination"""
    return app_client_service.get_app_clients(db, skip=skip, limit=limit)

@router.get("/name/{name}")
def get_app_clients_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """Get list of app_clients in a name"""
    return app_client_service.get_app_clients_by_name(db, name)

@router.put("/{app_client_id}")
def update_app_client(
    request: Request,
    app_client_id: str,
    app_client_in: AppClientRequest = Depends(),
    db: Session = Depends(get_db),
):
    """Update app client name"""
    
    return app_client_service.update_app_client(db, app_client_in, app_client_id)

@router.delete("/{app_client_id}")
def delete_app_client(
    app_client_id: str,
    db: Session = Depends(get_db),
):
    """Delete app_client"""
    
    return app_client_service.delete_app_client(db, app_client_id) 
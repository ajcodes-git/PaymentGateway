from sqlalchemy.orm import Session
from app.models import AppClient
from app.schemas.app_client import AppClientRequest
from app.repositories import app_client_repository
from app.utils.response import response
from app.utils import hashing
from fastapi import status
import secrets
import string

def create_app_client(db: Session, app_client_in: AppClientRequest):
    try:
        if app_client_repository.get_by_name(db, app_client_in.name):
            return response(status.HTTP_400_BAD_REQUEST, "App Client with this name already exists")
        
        app_client_data = app_client_in.dict()
        app_client_data['api_key'] = generate_api_key()

        app_client = app_client_repository.create(db, app_client_data)

        return response(
            status.HTTP_201_CREATED,
            "App client created successfully.",
            app_client.to_dict()
        )
    except Exception as e:
        return response(status_code=500, message=str(e))

def get_app_client(db: Session, app_client_id: str):
    try:
        app_client = app_client_repository.get(db, app_client_id)
        if not app_client:
            return response(status.HTTP_404_NOT_FOUND, "App client not found")
        
        return response(status.HTTP_200_OK, "App client retrieved", app_client.to_dict())
    except Exception as e:
        return response(status_code=500, message=str(e))

def get_app_clients(db: Session, skip: int = 0, limit: int = 100):
    try:
        app_clients = app_client_repository.get_multi(db, skip=skip, limit=limit)
        return response(status.HTTP_200_OK, f"{len(app_clients)} App clients retrieved", [app_client.to_dict() for app_client in app_clients])
    except Exception as e:
        return response(status_code=500, message=str(e))
    
def get_app_clients_by_name(db: Session, app_name: str):
    try:
        app_clients = app_client_repository.search_by_name(db, app_name)
        return response(status.HTTP_200_OK, f"{len(app_clients)} App clients retrieved", [app_client.to_dict() for app_client in app_clients])
    except Exception as e:
        return response(status_code=500, message=str(e))
    
def update_app_client(db: Session, app_client_in: AppClientRequest, app_client_id):
    try:
        app_client = app_client_repository.get(db, app_client_id)
        if not app_client:
            return response(status.HTTP_404_NOT_FOUND, "App client not found")

        if (app_client_in.name and app_client_in.name == app_client.name):
            return response(status.HTTP_400_BAD_REQUEST, "App client with this name already exists")
    
        updated_app_client = app_client_repository.update(db, app_client, app_client_in)
        return response(
            status.HTTP_200_OK,
            "App client updated successfully",
            updated_app_client.to_dict()
        )
    except Exception as e:
        return response(status_code=500, message=str(e))

def delete_app_client(db: Session, app_client_id: str):
    try:
        app_client = app_client_repository.get(db, app_client_id)
        if not app_client:
            return response(status.HTTP_404_NOT_FOUND, "App client not found")
    
        app_client_repository.delete(db, app_client_id)
        return response(status.HTTP_200_OK, "App client deleted successfully") 
    except Exception as e:
        return response(status_code=500, message=str(e))

def generate_api_key(length: int = 32) -> str:
    """Generates a secure API key."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))
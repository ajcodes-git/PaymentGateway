from sqlalchemy.orm import Session
from app.models import AppClient
from typing import Optional, List
from app.repositories import crud_template
from datetime import date


def search_by_name(db: Session, name: str) -> List[AppClient]:
    return db.query(AppClient).filter(AppClient.name.ilike(f"%{name}%")).all()

def get_by_name(db: Session, name: str) -> AppClient:
    return db.query(AppClient).filter(AppClient.name.ilike(name)).first()

def get_active(db: Session, api_key: str):
    return db.query(AppClient).filter(AppClient.api_key == api_key,AppClient.is_active == True).first()


# Reuse base repository functions
get = lambda db, id: crud_template.get(db, AppClient, id)
get_multi = lambda db, **kwargs: crud_template.get_multi(db, AppClient, **kwargs)
create = lambda db, obj_in: crud_template.create(db, AppClient, obj_in)
update = lambda db, db_obj, obj_in: crud_template.update(db, AppClient, db_obj, obj_in)
delete = lambda db, id: crud_template.delete(db, AppClient, id) 
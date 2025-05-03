from sqlalchemy.orm import Session
from app.models import Transaction
from sqlalchemy import cast, Date
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR
from typing import Optional, List
from app.repositories import crud_template
from datetime import date

def get_by_date(db: Session, date: date) -> List[Transaction]:
    return db.query(Transaction).filter(cast(Transaction.created_at, Date) == date).all()

def get_by_email(db: Session, email: str) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.email.ilike(f"%{email}%")).all()

def get_by_user_id(db: Session, user_id: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).first()

def get_by_gateway_ref(db: Session, gateway_ref: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.gateway_ref == gateway_ref).first()


# Reuse base repository functions
get = lambda db, id: crud_template.get(db, Transaction, id)
get_multi = lambda db, **kwargs: crud_template.get_multi(db, Transaction, **kwargs)
create = lambda db, obj_in: crud_template.create(db, Transaction, obj_in)
update = lambda db, db_obj, obj_in: crud_template.update(db, Transaction, db_obj, obj_in)
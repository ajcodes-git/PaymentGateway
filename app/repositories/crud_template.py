from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

def get(db: Session, model: Type[ModelType], id: Any) -> Optional[ModelType]:
    return db.query(model).filter(model.id == id).first()

def get_multi(
    db: Session, 
    model: Type[ModelType], 
    *, 
    skip: int = 0, 
    limit: int = 100
) -> List[ModelType]:
    return db.query(model).offset(skip).limit(limit).all()

def create(db: Session, model: Type[ModelType], obj_in: Dict[str, Any]) -> ModelType:
    obj = model(**obj_in)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(
    db: Session,
    model: Type[ModelType],
    db_obj: ModelType,
    obj_in: Union[Dict[str, Any], BaseModel]
) -> ModelType:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if not value:
            continue
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, model: Type[ModelType], id: Any) -> ModelType:
    obj = db.query(model).get(id)
    db.delete(obj)
    db.commit()
    return obj 
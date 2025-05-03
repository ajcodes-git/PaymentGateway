from sqlalchemy import Column, String, Boolean
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base

class AppClient(Base):
    __tablename__ = "app_clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    api_key = Column(String, unique=True, index=True) 
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "api_key": self.api_key,
            "description": self.description,
            "is_active": self.is_active
        }

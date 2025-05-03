from pydantic import BaseModel
from typing import Optional

class AppClientRequest(BaseModel):
    name: str
    description: Optional[str]
   
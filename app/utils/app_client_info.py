from fastapi import Header, HTTPException
from typing import Optional
import json

def get_metadata(
    custom: Optional[str] = Header(default=None, alias="x-custom-data")
):
    try:
        parsed = json.loads(custom) if custom else None
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in metadata header")

    return {"custom": parsed}

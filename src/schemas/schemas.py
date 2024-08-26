from pydantic import BaseModel
from typing import List, Optional

class Content(BaseModel):
    source: str
    sections: List[str]
    url: str
    metadata: Optional[dict] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_update: Optional[bool] = False
    manual_check_required: bool = False
    
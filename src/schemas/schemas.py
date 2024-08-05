from pydantic import BaseModel
from typing import List, Optional

class TextSchema(BaseModel):
    sections: List[str]
    url: str
    metadata: Optional[dict] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
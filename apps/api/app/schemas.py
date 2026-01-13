from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Sermon(BaseModel):
    id: str
    sermonName: str
    seriesName: Optional[str] = None
    weekOrDate: Optional[str] = None
    pastorName: Optional[str] = None
    status: str
    filePath: str
    originalFilename: str
    createdAt: datetime

    class Config:
        from_attributes = True

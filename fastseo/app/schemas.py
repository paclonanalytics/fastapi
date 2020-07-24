from typing import List, Optional

from pydantic import BaseModel
from datetime import date
import uuid

class Searhvolume(BaseModel):
    ext_taskid: str = uuid.uuid1()
    date: date
    country_name: str = 'United States'
    language_name: str = 'English'
    keywords: List[str] = ['English', "New Yourk"]

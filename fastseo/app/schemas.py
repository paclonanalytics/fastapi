from typing import List

from pydantic import BaseModel
from datetime import date



class Searhvolume(BaseModel):
    userid: int
    projectid: int
    taskid: int
    date: date
    country_name: str
    language_name: str
    keywords: List

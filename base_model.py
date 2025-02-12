from pydantic import BaseModel
from typing import List

class BaseModelWithIDs(BaseModel):
    ids: List[int]

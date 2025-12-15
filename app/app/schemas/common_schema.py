from pydantic import BaseModel
from enum import Enum


class IOrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"

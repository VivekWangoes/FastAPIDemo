import uuid
from pydantic import BaseModel
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class MemberUpdate(BaseModel):
    id : Optional[str] = None
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    email : Optional[str] = None
    mobile_number : Optional[str] = None
    gender : Optional[str] = None
    date_of_birth : Optional[str] = None
    credit_points : Optional[str] = None
    debit_points : Optional[str] = None
    reward_ids : Optional[str] = None

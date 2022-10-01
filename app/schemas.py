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
    mobile: Optional[str] = None
    gender : Optional[str] = None
    date_of_birth : Optional[str] = None

class CreateRewardWallet(BaseModel):
    member_id : Optional[str] = None
    points : Optional[str] = None

class CreateRewardTransaction(BaseModel):
    wallet_id : Optional[str] = None
    inventory_id : Optional[str] = None
    member_id : Optional[str] = None
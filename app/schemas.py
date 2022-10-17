import uuid
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime

from fastapi_users import schemas  

class UserRead(schemas.BaseUser[uuid.UUID]):
   pass


class UserCreate(schemas.BaseUserCreate):
    pass

class UserRegistration(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: str
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    mobile: Optional[str] = None
    gender : Optional[str] = None
    date_of_birth : date

    @validator("date_of_birth", pre=True)
    def parse_birthdate(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()


class UserDisplay(BaseModel):
   
   email: EmailStr

   class Config:
        orm_mode = True


class UserUpdate(schemas.BaseUserUpdate):
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    email : Optional[str] = None
    mobile: Optional[str] = None
    gender : Optional[str] = None
    date_of_birth : Optional[str] = None


class MemberUpdate(BaseModel):
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    mobile: Optional[str] = None
    gender : Optional[str] = None
    date_of_birth : Optional[str] = None

class CreateRewardWallet(BaseModel):
    member_id : Optional[str] = None
    points : Optional[str] = None

class CreateRewardTransaction(BaseModel):
    reward_id : Optional[str] = None
    email : Optional[str] = None

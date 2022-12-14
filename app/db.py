from typing import AsyncGenerator, List

from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


DATABASE_URL = "sqlite+aiosqlite:///./astons_crm.db"
Base = declarative_base()

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    mobile = Column(String)
    date_of_birth = Column(String)
    gender = Column(String)
    oauth_accounts: List[OAuthAccount] = relationship("OAuthAccount", lazy="joined")


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session: 
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(String)
    fastapi_id = Column(String)
    email = Column(String)

    def dict(self):
        return {
            "odoo": self.odoo_id,
            "fastapi" : self.fastapi_id,
            "email" : self.email
        }

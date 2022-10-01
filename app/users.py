import os
import uuid
from typing import Optional
import json
from uuid import UUID
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from app.db import User, get_user_db, async_session_maker
from app.db import Member, UserRegister
from sqlalchemy import select, delete
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import load_dotenv

SECRET = "SECRET"

google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", "798436640829-3jcqbjul3bcnoq8vsvmbra8rso326e3k.apps.googleusercontent.com"),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "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"),
)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    # user_db: BaseUserDatabase[models.UP, models.ID]


    async def on_after_register(self, user: User, request: Optional[Request] = None):
        db = async_session_maker()
        qry = select(UserRegister)
        member_odoo_id = await db.execute(qry)
        objs = member_odoo_id.fetchall()
        member_id = objs[0][0].dict()['odoo']
        user = Member(odoo_member_id=member_id, fastapi_member_id=str(user.id))
        db.add(user)
        await db.commit()
        await db.refresh(user)

        for obj in objs:
            await db.delete(obj[0])
        await db.commit()
        
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        conf = ConnectionConfig(
            MAIL_SERVER = os.getenv('MAIL_SERVER'),
            MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
            MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
            MAIL_FROM = os.getenv('MAIL_FROM'),
            MAIL_PORT = os.getenv('MAIL_PORT'),
        )

        html = """
            <p>Token is %s </p> 
            """ %token

        message = MessageSchema(
        subject="Forgot password token",
        recipients=[user.email],  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

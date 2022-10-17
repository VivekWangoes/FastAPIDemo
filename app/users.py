import os
import uuid
from typing import Optional
import requests
from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, exceptions, models, schemas
import json
from uuid import UUID
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from httpx_oauth.clients.google import GoogleOAuth2
import re
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from app.db import User, get_user_db, Member, async_session_maker
from fastapi_users.db import SQLAlchemyUserDatabase

SECRET = "SECRET"

CLIENT_ID =  os.getenv("GOOGLE_OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

google_oauth_client = GoogleOAuth2(
    os.getenv('GOOGLE_OAUTH_CLIENT_ID', CLIENT_ID),
    os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', CLIENT_SECRET),
)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        if user.first_name:
            vals = {
                "first_name": user.first_name,
                "last_name" : user.last_name,
                "email" : user.email,
                "mobile" : user.mobile,
                "gender" : user.gender,
                "date_of_birth" : user.date_of_birth,
                "is_member" : True,
                "name" : user.first_name,
                "active" : False 
            }
        else:
            vals ={
                "email" : user.email,
                "name" : user.email,
                "is_member" : True,
                "active" : False 
            }

        datas = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "method": "execute",
                    "service": "object",
                    "args": [
                        os.getenv('DATABASE_NAME'),
                        os.getenv('USER_ID'),
                        os.getenv('USER_PASSWORD'),
                        os.getenv('MEMBER_MODEL'),
                        os.getenv('CREATE_METHOD'),
                        vals,
                    ] 
                }  
            }
        req = requests.post(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
        odoo_id = req.json()['result']
        fastapi_member = Member(odoo_id=odoo_id, fastapi_id=str(user.id), email = str(user.email))
        db = async_session_maker()  
        db.add(fastapi_member)
        await db.commit()
        await db.refresh(fastapi_member)
        
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
        recipients=[user.email], 
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

from fastapi import Depends, FastAPI

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate, UserRegistration, UserDisplay
from app.users import (
    SECRET,
    auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
)
from fastapi_users.authentication import Authenticator
from routers import users, reward
from fastapi.openapi.utils import get_openapi

from starlette.requests import Request
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
import os 

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserDisplay, UserRegistration),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET),
    prefix="/auth/google",
    tags=["auth"],
)
app.include_router(
    users.get_members_router(),
    prefix="/member",
    tags=["member"]
    )

app.include_router(
    reward.get_reward_router(),
    prefix="/reward",
    tags=["reward"]
    )

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

origins = [
    "http://localhost:8000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAUTHLIB_INSECURE_TRANSPORT=1
client_id = "820978601716-dm0u3d4hgvfrlmjcl3gutmm3l7rglm7v.apps.googleusercontent.com"
client_secret = "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"
call_back_url ='http://localhost:8000/google/callback'

google_sso = GoogleSSO(client_id, client_secret, call_back_url, allow_insecure_http=True)

@app.get("/google/login")
async def google_login():
    # request.headers["content-type"] = "application/json"
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect()

@app.get("/google/callback")
async def google_callback(request: Request):
    # import pdb;pdb.set_trace()
    """Process login response from Google and return user info"""
    user = await google_sso.verify_and_process(request)
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
        "provider": user.provider,
    }

call_back_url = 'http://localhost:8000/facebook/callback'

facebook_sso = FacebookSSO("1082129155820468", "b9884eae3859450e99ca0c72b69d68c3", call_back_url, allow_insecure_http=True)

@app.get("/facebook/login")
async def facebook_login():
    # request.headers["content-type"] = "application/json"
    """Generate login url and redirect"""
    return await facebook_sso.get_login_redirect()

@app.get("/facebook/callback")
async def facebook_callback(request: Request):
    # import pdb;pdb.set_trace()
    """Process login response from facebook and return user info"""
    user = await facebook_sso.verify_and_process(request)
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
        "provider": user.provider,
    }


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()

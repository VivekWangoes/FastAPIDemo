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


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()

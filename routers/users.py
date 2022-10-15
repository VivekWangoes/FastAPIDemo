from fastapi import APIRouter, Request, Response, Depends, HTTPException, Body, FastAPI, Header
from typing import Union
from operation import crud_operation
from app import schemas
from fastapi_users.authentication import Authenticator
from app.users import current_active_user
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.db import User

def get_members_router() -> APIRouter:

    router = APIRouter()

    @router.put(
        "/edit_member/", 
        dependencies=[Depends(current_active_user)], 
        include_in_schema=False
        )
    async def edit_member(req : schemas.MemberUpdate, 
        user: User = Depends(current_active_user)
        ):
        email = user.email
        vals = {}
        if req.first_name and req.first_name != "string":
            vals["first_name"] = req.first_name
        if req.last_name and req.last_name != "string":
            vals["last_name"] = req.last_name
        if req.mobile and req.mobile != "string":
            vals["mobile"] = req.mobile
        if req.gender and req.gender != "string":
            vals["gender"] = req.gender
        if req.date_of_birth and req.date_of_birth != "string":
            vals["date_of_birth"] = req.date_of_birth
        member_data =  await crud_operation.json_edit(email, vals)
        return member_data

    @router.get("/get_member/{email}", 
        dependencies=[Depends(current_active_user)],
        include_in_schema=False)
    async def get_member(email):
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        member_data = await crud_operation.json_read_delete("read", email)
        return member_data

    @router.delete("/unlink_member/{email}", 
        dependencies=[Depends(current_active_user)],
        include_in_schema=False)
    async def unlink_member(email: str):
        resp = await crud_operation.json_read_delete("unlink", email)
        return resp

    return router


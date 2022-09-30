from fastapi import APIRouter, Request, Response, Depends, HTTPException
from typing import Union
from operation import crud_operation
from app import schemas
from fastapi_users.authentication import Authenticator
from app.users import current_active_user

def get_members_router() -> APIRouter:

    router = APIRouter()

    @router.put(
        "/edit_member/{member_id}", 
        response_model=schemas.MemberUpdate, dependencies=[Depends(current_active_user)]
        )
    async def edit_member(req : schemas.MemberUpdate):
        member_id = req.id
        if member_id:
            member_id = req.id
        else:
            raise HTTPException(status_code=404, detail="Member not found")
        vals = {}
        if req.first_name != "string":
            vals["first_name"] = req.first_name
        if req.last_name != "string":
            vals["last_name"] = req.last_name
        if req.email != "string":
            vals["email"] = req.email
        if req.mobile != "string":
            vals["mobile"] = req.mobile
        if req.gender != "string":
            vals["gender"] = req.gender
        if req.date_of_birth != "string":
            vals["date_of_birth"] = req.date_of_birth

        member_data =  await crud_operation.json_edit(member_id, vals)
        return member_data

    @router.get("/get_member/{member_id}", dependencies=[Depends(current_active_user)])
    async def get_member(member_id):
        if not member_id:
            raise HTTPException(status_code=404, detail="Member not found")
        member_data = await crud_operation.json_read_delete("read", member_id)
        return member_data

    @router.delete("/unlink_member/{member_id}", dependencies=[Depends(current_active_user)])
    async def unlink_member(member_id):
        if not member_id:
            raise HTTPException(status_code=404, detail="Member not found")
        member_data = await crud_operation.json_read_delete("unlink", member_id)
        return member_data

    return router


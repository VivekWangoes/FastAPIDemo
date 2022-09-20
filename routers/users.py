from fastapi import APIRouter, Request, Response, Depends, HTTPException
from typing import Union
from python_files import crud_operation
from app import schemas
# from app.users import fastapi_users
from fastapi_users.authentication import Authenticator
from app.users import current_active_user

router = APIRouter()

@router.put("/edit_member/{member_id}", response_model=schemas.MemberUpdate, dependencies=[Depends(current_active_user)])
async def json_edit_member(req : schemas.MemberUpdate):
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
    if req.credit_points != "string" or req.debit_points != "string":
        vals["point_ids"] = [(0,0, {
            "credit_points" : req.credit_points if req.credit_points else 0,     
            "debit_points" :  req.debit_points if req.debit_points else 0
        })]
    if req.reward_ids != "string" :
        vals["reward_ids"] = [(0,0,{
                "reward": req.reward_ids
            })]
    if req.mobile_number != "string":
        vals["mobile_number"] = req.mobile_number
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



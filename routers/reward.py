from fastapi import APIRouter, Request, Response, Depends, HTTPException
from typing import Union
from app import schemas
from fastapi_users.authentication import Authenticator
from app.users import current_active_user
from operation import reward_operation
from app.db import User, get_user_db, async_session_maker
from app.db import Member
from sqlalchemy import select

def get_reward_router() -> APIRouter:
    router = APIRouter()

    async def get_member_id(email):
        db = async_session_maker()
        query = select(Member).where(Member.email == email)
        member_id = await db.execute(query)
        values = member_id.fetchall()
        if values:
            member_id = values[0][0].dict()['odoo']
            if member_id:
                member_id = int(member_id)
            return member_id
        else:
            raise HTTPException(status_code=404, detail="Member not found")

    @router.get(
        "/get_reward_inventory/{email}",
         dependencies=[Depends(current_active_user)],
         include_in_schema=False
        )
    async def reward_inventory(email: str):
        resp = await reward_operation.get_reward_inventory(email)
        return resp

    # @router.post(
    #     "/create_reward_wallet", 
    #     response_model=schemas.CreateRewardWallet,
    #     dependencies=[Depends(current_active_user)],
    # )
    # async def reward_wallet(req : schemas.CreateRewardWallet):
    #     vals = {}
    #     if req.member_id != "string" and req.member_id != "":
    #         member_id = await get_member_id(req.member_id)
    #         vals["member_id"] = member_id
    #     else:
    #         raise HTTPException(status_code=404, detail="Member id not found")

    #     if req.points != "string":
    #         vals["points"] = int(req.points)
    #     data = await reward_operation.create_reward_wallet(vals)
    #     return data

    @router.post(
        "/create_reward_transaction/",  
        dependencies=[Depends(current_active_user),
        ],include_in_schema=False)
    async def reward_transaction(req: schemas.CreateRewardTransaction):
        vals = {}
        if req.reward_id != "string" and req.reward_id != "":
            vals["reward_id"] = int(req.reward_id)
        else:
            raise HTTPException(status_code=404, detail="Reward id not found")

        if req.email != "string" and req.email != "":
            member_id = await get_member_id(req.email)
            vals["member_id"] = int(member_id)
        else:
            raise HTTPException(status_code=404, detail="Member id not found")            

        resp = await reward_operation.create_reward_transaction(vals)
        return resp

    @router.get("/get-member-points", 
        dependencies=[Depends(current_active_user)],
        include_in_schema=False)
    async def get_member_points(email: str):
        member_id = await get_member_id(email)
        resp = await reward_operation.get_points(member_id)
        return resp

    return router
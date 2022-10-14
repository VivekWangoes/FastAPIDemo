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

    async def get_member_id(member_id):
        db = async_session_maker()
        query = select(Member).where(Member.fastapi_member_id == member_id)
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
        "/get_reward_inventory/",
         dependencies=[Depends(current_active_user)],
         include_in_schema=False
        )
    async def reward_inventory():
        data = await reward_operation.get_reward_inventory()
        return data

    @router.post(
        "/create_reward_wallet", 
        response_model=schemas.CreateRewardWallet,
        dependencies=[Depends(current_active_user)],
        include_in_schema=False
    )
    async def reward_wallet(req : schemas.CreateRewardWallet):
        vals = {}
        if req.member_id != "string" and req.member_id != "":
            member_id = await get_member_id(req.member_id)
            vals["member_id"] = member_id
        else:
            raise HTTPException(status_code=404, detail="Member id not found")

        if req.points != "string":
            vals["points"] = int(req.points)
        data = await reward_operation.create_reward_wallet(vals)
        return data

    @router.post(
        "/create_reward_transaction/",
        response_model=schemas.CreateRewardTransaction,
        dependencies=[Depends(current_active_user)
        ], include_in_schema=False)
    async def reward_transaction(req: schemas.CreateRewardTransaction):
        vals = {}
        if req.wallet_id != "string" and req.wallet_id != "":
            vals["wallet_id"] = int(req.wallet_id)
        else:
            raise HTTPException(status_code=404, detail="Wallet id not found")

        if req.inventory_id != "string" and req.wallet_id != "":
            vals["inventory_id"] = int(req.inventory_id)
        else:
            raise HTTPException(status_code=404, detail="Inventory id not found")

        if req.member_id != "string" and req.member_id != "":
            member_id = await get_member_id(req.member_id)
            vals["member_id"] = member_id
        else:
            raise HTTPException(status_code=404, detail="Member id not found")            

        data = await reward_operation.create_reward_transaction(vals)
        return data

    return router
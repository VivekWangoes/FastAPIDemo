import json
import requests
import uuid
from typing import Optional

from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.db import User, get_user_db, async_session_maker
from app.models import Member, UserRegister
from sqlalchemy import select
from typing import Awaitable
from app import config
import ast


SECRET = "SECRET"


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

async def member_register(vals):
    vals = ast.literal_eval(vals)
    val_lst = []
    for key in vals:
        val_lst.append(key)

    if 'email' in val_lst:
        if vals["email"] == "":
            raise HTTPException(status_code=404, detail="Email not found")
    else:
        raise HTTPException(status_code=404, detail="Email not found")


    if "credit_points" in val_lst or "debit_points" in key:
        if vals["credit_points"] != "" or vals["debit_points"] != 0:
            val= [(0,0, {
                "credit_points" : vals["credit_points"],     
                "debit_points" :  vals["debit_points"]
            })]
            vals["point_ids"] = val

        del vals["credit_points"]
        del vals["debit_points"]

    if "date_of_birth" in val_lst:
        if vals["date_of_birth"] == "":
            del vals["date_of_birth"]

    if "reward_ids" in val_lst:
        if vals["reward_ids"] != "":
            vals["reward_ids"] = [(0,0, {  
                "reward" :  vals["reward_ids"]
            })]
        else:
            del vals["reward_ids"]

    print(vals)
    datas = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "method": "execute",
                "service": "object",
                "args": [
                    config.database,
                    config.username,
                    config.password,
                    config.models,
                    "create",
                    vals,
                ] 
            }  
        }
    req = requests.post(config.url, json=datas)
    db = async_session_maker()
    user = UserRegister(odoo_member_id=req.json()['result'])
    db.add(user)
    await db.commit()
    await db.refresh(user)

async def json_edit(member_id, vals):
    member_id = await get_member_id(member_id)
    if member_id:
        datas = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "method": "execute",
                "service": "object",
                "args": [
                    config.database,
                    config.username,
                    config.password,
                    config.models,
                    "write",
                    [member_id],
                    vals
                ]  
            }  
        }
        req = requests.put(config.url, json=datas)
        return req.json()

        

async def json_read_delete(method, member_id):
    member_id = await get_member_id(member_id)
    if member_id:
        if method == "read":
            datas = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "method": "execute",
                    "service": "object",
                    "args": [
                        config.database,
                        config.username,
                        config.password,
                        config.models,
                        "read",
                        [member_id],
                    ]   
                }  
            }
            req = requests.get(config.url, json=datas)

        if method == "unlink":
            datas = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "method": "execute",
                    "service": "object",
                    "args": [
                        config.database,
                        config.username,
                        config.password,
                        config.models,
                        "unlink",
                        [member_id],
                    ]   
                }  
            }
            req = requests.get(config.url, json=datas)
        return req.json()




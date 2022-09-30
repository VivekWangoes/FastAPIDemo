import json
import requests
import uuid
from typing import Optional
from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.db import User, get_user_db, async_session_maker
from app.db import Member, UserRegister
from sqlalchemy import select
from typing import Awaitable
import ast
import os
from dotenv import load_dotenv

load_dotenv()

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

    if "date_of_birth" in val_lst:
        if vals["date_of_birth"] == "":
            del vals["date_of_birth"]

    vals["is_member"] = True
    vals["name"] = vals["first_name"]
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
    db = async_session_maker()
    print(req)
    user = UserRegister(odoo_member_id=req.json()['result'])
    db.add(user)
    await db.commit()
    await db.refresh(user)

async def json_edit(member_id, vals):
    member_id = await get_member_id(member_id)
    count = 0
    for key in vals.keys():
        if key == "first_name":
            count = 1

    if count == 1:
        vals["name"] = vals["first_name"]

    if member_id:
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
                    os.getenv('WRITE_METHOD'),
                    [member_id],
                    vals
                ]  
            }  
        }
        req = requests.put(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
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
                        os.getenv('DATABASE_NAME'),
                        os.getenv('USER_ID'),
                        os.getenv('USER_PASSWORD'),
                        os.getenv('MEMBER_MODEL'),
                        os.getenv('READ_METHOD'),
                        [member_id],
                    ]   
                }  
            }
            req = requests.get(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)

        if method == "unlink":
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
                        os.getenv('DELETE_METHOD'),
                        [member_id],
                    ]   
                }  
            }
            req = requests.get(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
        return req.json()




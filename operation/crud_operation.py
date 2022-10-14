import json
import requests
import uuid
from typing import Optional
from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.db import User, get_user_db, async_session_maker
from app.db import Member
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


async def json_edit(member_id, vals):
    member_id = await get_member_id(member_id)
    vals["name"] = vals.get("first_name", False)
    
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




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


async def json_edit(email, vals):
    member_id = await get_member_id(email)
    if vals.get("first_name", False):
        vals["name"] = vals.get("first_name")

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
        if req.json()['result']:
            vals={
                "status" : "successfully updated"
            }
        return vals

async def json_read_delete(method, email):
    member_id = await get_member_id(email)
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
            resp = req.json()
            vals = {
                "first_name" : resp['result'][0]['first_name'],
                "last_name" : resp['result'][0]['last_name'],
                "mobile" : resp['result'][0]['mobile'],
                "date_of_birth" : resp['result'][0]['date_of_birth'],
                "gender" : resp['result'][0]['gender'],
                "points" : resp['result'][0]['points']
            }
            return vals

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
                        [
                            json.dumps(member_id)
                        ],
                    ]   
                }  
            }
            req = requests.get(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
            return req.json()['result']




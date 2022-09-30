import json
import requests
import os
from dotenv import load_dotenv

async def get_reward_inventory():
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
                os.getenv('REWARD_INVENTORY_MODEL'),
                os.getenv('SEARCH_READ_METHOD'),
                [["reward_id", "=", 1]]
            ]   
        }  
    }
    req = requests.get(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
    print(req.json())
    return req.json()['result']

async def create_reward_wallet(vals):
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
                os.getenv('REWARD_WALLET_MODEL'),
                os.getenv('CREATE_METHOD'),
                vals,
            ]   
        }  
    }
    req = requests.get(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
    return req.json()

async def create_reward_transaction(vals):
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
                os.getenv('REWARD_TRANSACTION_MODEL'),
                os.getenv('REDEMPTION_POINTS_METHOD'),
                [
                    json.dumps(vals)
                ],
            ]   
        }  
    }   
    req = requests.get(os.getenv('ODOO_URL')+"/jsonrpc", json=datas)
    print(req.json())
    return req.json()   

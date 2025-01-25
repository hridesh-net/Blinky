# app/utils/register_commands.py

import requests
from app.core.config import settings

def register_test_cmd(commands: list):
    url = "https://discord.com/api/v10/applications/1332248998802620426/commands"
    
    for cmd in commands:
        headers = {
            "Authorization": f"Bot {settings.DISCORD_TOKEN}"
        }
        
        response = requests.post(url, headers=headers, json=cmd)
        if response.status_code == 201:
            print(f"✅ Command '{cmd['name']}' registered successfully!")
        else:
            print(f"❌ Failed to register '{cmd['name']}': {response.status_code} - {response.text}")
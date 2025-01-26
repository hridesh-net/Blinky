from fastapi import APIRouter, Header, HTTPException, Request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from app.core.config import settings
import json
import requests

from app.utils.post_utilities import post_to_grp
from app.services.cmd.slash_cmd import set_team_channel, add_team_member, submit_todo, model_resp

router = APIRouter()


@router.post("/interactions")
async def interactions(
    request: Request,
    x_signature_ed25519: str = Header(...),
    x_signature_timestamp: str = Header(...),
):
    body = await request.body()
    print("=====")
    print(body)
    verify_key = VerifyKey(bytes.fromhex(settings.DISCORD_PUBLIC_KEY))

    try:
        verify_key.verify(
            x_signature_timestamp.encode() + body, bytes.fromhex(x_signature_ed25519)
        )
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="Invalid request signature")

    payload = json.loads(body)
    print("-------")
    print(payload)

    if payload["type"] == 1:  # Ping
        return {"type": 1}

    if payload["type"] == 2:  # Application Command
        command_name = payload["data"]["name"]
        guild_id = payload["guild_id"]

        if command_name == "your_command":
            # Handle your specific command
            return {"type": 4, "data": {"content": "Command received!"}}

        if command_name == "set_team_channel":
            return set_team_channel(payload, guild_id)

        if command_name == "add_team_member":
            return add_team_member(payload, guild_id)

        if command_name == "submit_todo":
            return submit_todo(payload, guild_id)

    if payload["type"] == 3:  # Message Component (e.g., button click)
        custom_id = payload["data"]["custom_id"]
        if custom_id == "add_todo":
            # Handle button interaction
            return {
                "type": 9,
                "data": {
                    "custom_id": "todos",
                    "title": "ToDo",
                    "components": [
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 4,
                                    "custom_id": "todos",
                                    "label": "Enter Your Task seperateed by '|' ",
                                    "style": 1,
                                    "min_length": 1,
                                    "max_length": 100,
                                    "placeholder": "Enter something...",
                                    "required": True,
                                }
                            ],
                        }
                    ],
                },
            }

    if payload["type"] == 5:  # Modal Submit
        return model_resp(payload)

    return {"type": 4, "data": {"content": "Unhandled interaction type."}}

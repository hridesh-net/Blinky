import json
import requests
import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from app.core.config import settings


from app.utils.post_utilities import post_to_grp
from app.services.cmd.slash_cmd import (
    set_team_channel,
    add_team_member,
    submit_todo,
    model_resp,
    manage_tasks,
    handle_task_selection,
)

router = APIRouter()


async def defer_interaction(interaction_id, interaction_token, ephemeral=True):
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    json_data = {"type": 5}  # DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
    if ephemeral:
        json_data["data"] = {"flags": 64}  # Ephemeral flag
    headers = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=json_data, headers=headers)


async def update_original_message(interaction_token, message_data):
    url = f"https://discord.com/api/v10/webhooks/{settings.APPLICATION_ID}/{interaction_token}/messages/@original"
    headers = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }
    print(f"Updating original message: {message_data}")
    async with httpx.AsyncClient() as client:
        response = await client.patch(url, json=message_data, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")


async def send_followup_message(interaction_token, message_data):
    url = f"https://discord.com/api/v10/webhooks/{settings.APPLICATION_ID}/{interaction_token}"
    headers = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }
    print(f"Sending followup message: {message_data}")
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=message_data, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")


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
        interaction_token = payload["token"]
        interaction_id = payload["id"]

        await defer_interaction(interaction_id, interaction_token)

        if command_name == "your_command":
            # Handle your specific command
            return {"type": 4, "data": {"content": "Command received!"}}

        if command_name == "set_team_channel":
            response_data = await set_team_channel(payload, guild_id)
        elif command_name == "add_team_member":
            response_data = await add_team_member(payload, guild_id)
        elif command_name == "submit_todo":
            response_data = await submit_todo(payload, guild_id)
        elif command_name == "manage_tasks":
            user_id = payload["member"]["user"]["id"]
            response_data = await manage_tasks(user_id, guild_id, payload)
            # return response_data
        else:
            response_data = {"content": "Unhandled command."}

        await update_original_message(interaction_token, response_data.get("data"))

    if payload["type"] == 3:  # Message Component (e.g., button click)
        custom_id = payload["data"]["custom_id"]
        if custom_id == "select_tasks":
            guild_id = payload["guild_id"]
            user_id = payload["member"]["user"]["id"]
            response_data = await handle_task_selection(user_id, guild_id, payload)
            return response_data

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
        return await model_resp(payload)

    return {"type": 4, "data": {"content": "Unhandled interaction type."}}

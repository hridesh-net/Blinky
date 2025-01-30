import httpx
import requests

from app.core.config import settings
from db.models.user import User


async def get_team_channel(user_id, guild_id):
    """
    Fetch the correct team channel for the user.
    """
    from db.session import SessionLocal

    db = SessionLocal()

    user = db.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()

    if user and user.team:
        channel_id = user.team.channel_id
    else:
        channel_id = None

    db.close()
    return channel_id


async def fetch_guild_members(guild_id):
    HEADERS = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000",
            headers=HEADERS,
        )
        return response.json()


async def fetch_channel_permissions(channel_id):
    HEADERS = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://discord.com/api/v10/channels/{channel_id}", headers=HEADERS
        )
        return response.json()


async def get_team_members(channel_id, guild_id):
    """Fetch members of a given channel using Discord API."""

    total_members = await fetch_guild_members(guild_id)
    channel = await fetch_channel_permissions(channel_id)

    permission_overwrites = channel.get("permission_overwrites", [])
    members_with_access = []
    for member in total_members:
        member_roles = member.get("roles", [])
        for overwrite in permission_overwrites:
            if (
                overwrite["id"] in member_roles
                or overwrite["id"] == member["user"]["id"]
            ):
                if overwrite["allow"] != "0":
                    members_with_access.append(member)
                    break

    for member in members_with_access:
        user = member["user"]
        print(
            f"User ID: {user['id']}, Username: {user['username']}#{user['discriminator']}"
        )

    return members_with_access


async def get_channel_members(channel_id):
    """Fetch members of a given channel using Discord API."""
    url = f"https://discord.com/api/v10/channels/{channel_id}/recipients"
    headers = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    print(response)
    return response.json() if response.status_code == 200 else []
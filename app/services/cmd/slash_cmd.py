import httpx
import requests
from datetime import date

from sqlalchemy.orm import Session

from db.models.team import Team
from db.models.task import Task
from db.models.user import User
from app.core.config import settings
from db.session import SessionLocal
from app.utils.post_utilities import post_to_grp


async def get_team_channel(user_id, guild_id):
    """
    Fetch the correct team channel for the user.
    """
    from db.session import SessionLocal

    db = SessionLocal()

    # Fetch the user and their team
    user = db.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()

    if user and user.team:
        channel_id = user.team.channel_id  # Get the team's assigned channel
    else:
        channel_id = None  # No team assigned

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
            f'https://discord.com/api/v10/channels/{channel_id}',
            headers=HEADERS
        )
        return response.json()


async def get_team_members(channel_id, guild_id):
    """Fetch members of a given channel using Discord API."""
    total_members = await fetch_guild_members(guild_id)
    channel = await fetch_channel_permissions(channel_id)
    
    permission_overwrites = channel.get('permission_overwrites', [])
    members_with_access = []
    for member in total_members:
        member_roles = member.get('roles', [])
        for overwrite in permission_overwrites:
            if overwrite['id'] in member_roles or overwrite['id'] == member['user']['id']:
                if overwrite['allow'] != '0':
                    members_with_access.append(member)
                    break
    
    for member in members_with_access:
        user = member['user']
        print(f"User ID: {user['id']}, Username: {user['username']}#{user['discriminator']}")
    
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


async def save_team_and_add_members(team_name, guild_id, channel_id):
    """Save team & channel in DB, then auto-assign members."""
    try:
        db: Session = SessionLocal()

        # Check if team exists
        team = db.query(Team).filter_by(name=team_name, guild_id=guild_id).first()
        if team:
            team.channel_id = channel_id
        else:
            team = Team(name=team_name, guild_id=guild_id, channel_id=channel_id)
            db.add(team)

        db.commit()

        # Fetch members from the channel
        members = await get_team_members(channel_id, guild_id)
        print(members)
        for member in members:
            user_id = member["user"]["id"]
            username = member["user"]["username"]
            name = member["user"]["global_name"]

            # Check if user exists
            user = db.query(User).filter_by(user_id=user_id, guild_id=guild_id, is_active=True).first()
            if not user:
                user = User(user_id=user_id, name=name, username=username, guild_id=guild_id, is_active=True)
                user.set_password('secure_password')
                db.add(user)
                db.commit()  # Commit to generate the user.id

            # Add user to team if not already a member
            if user not in team.members:
                team.members.append(user)

        db.commit()
        return f"✅ Team '{team_name}' is now linked to <#{channel_id}>, and members have been added!"
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def add_user_to_team(user_id, guild_id, team_name):
    """Assign a user to a specific team"""
    db: Session = SessionLocal()
    team = db.query(Team).filter_by(name=team_name, guild_id=guild_id).first()

    if not team:
        db.close()
        return f"❌ Team '{team_name}' does not exist!"

    user = db.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()
    if user:
        user.team_id = team.id
    else:
        new_user = User(
            user_id=user_id,
            username=f"User-{user_id}",
            guild_id=guild_id,
            team_id=team.id,
        )
        db.add(new_user)

    db.commit()
    db.close()

    return f"✅ User <@{user_id}> has been added to '{team_name}'!"


async def set_team_channel(payload, guild_id):
    team_name = payload["data"]["options"][0]["value"]
    channel_id = payload["data"]["options"][1]["value"]
    message = await save_team_and_add_members(team_name, guild_id, channel_id)
    return {"type": 4, "data": {"content": message}}


async def add_team_member(payload, guild_id):
    user_id = payload["data"]["options"][0]["value"]
    team_name = payload["data"]["options"][1]["value"]
    message = add_user_to_team(user_id, guild_id, team_name)
    return {"type": 4, "data": {"content": message}}


async def submit_todo(payload, guild_id):
    tasks = payload["data"]["options"][0]["value"]
    user_id = payload["member"]["user"]["id"]
    user_name = payload["member"]["user"]["username"]
    team_channel_id = get_team_channel(user_id, guild_id)
    if not team_channel_id:
        return {
            "type": 4,
            "data": {"content": "❌ Your team doesn't have a To-Do channel set!"},
        }
    post_to_grp(team_channel_id, settings.DISCORD_TOKEN, user_name, tasks, user_id)
    return {"type": 4, "data": {"content": "✅ To-Do submitted!"}}


async def model_resp(payload):
    custom_id = payload["data"]["custom_id"]
    if custom_id == "todos":
        user_input = payload["data"]["components"][0]["components"][0]["value"]
        user_name = payload["user"]["username"]
        name = payload["user"]["global_name"]

        avatar_hash = payload["user"]["avatar"]
        user_id = payload["user"]["id"]
        # Process the user's input

        db: Session = SessionLocal()
        user = db.query(User).filter_by(user_id=user_id).first()

        if not user:
            user = User(
                user_id=user_id,
                name=name,
                username=user_name,
                is_active=True,
            )
            user.set_password("secure_password")
            db.add(user)
            db.commit()
            db.refresh(user)

        for task in user_input.split("|"):
            new_task = Task(
                user_id=user.id, description=task.strip(), date=date.today()
            )
            db.add(new_task)
        db.commit()
        db.close()


        post_to_grp(
            "1332261881267879988",
            settings.DISCORD_TOKEN,
            user_name,
            user_input,
            user_id,
            avatar_hash,
        )
        return {
            "type": 4,
            "data": {"content": "✅ Your To-Do list has been saved!"},
        }

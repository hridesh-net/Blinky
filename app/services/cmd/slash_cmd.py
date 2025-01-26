import requests
from datetime import date

from sqlalchemy.orm import Session

from db.models.team import Team
from db.models.task import Task
from db.models.user import User
from app.core.config import settings
from db.session import SessionLocal
from app.utils.post_utilities import post_to_grp


def get_team_channel(user_id, guild_id):
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


def get_channel_members(channel_id):
    """Fetch members of a given channel using Discord API."""
    url = f"https://discord.com/api/v10/channels/{channel_id}/recipients"
    headers = {
        "Authorization": f"Bot {settings.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []


def save_team_and_add_members(team_name, guild_id, channel_id):
    """Save team & channel in DB, then auto-assign members."""
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
    members = get_channel_members(channel_id)
    for member in members:
        user_id = member["id"]
        username = member["username"]

        # Check if user exists
        user = db.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()
        if user:
            user.team_id = team.id
        else:
            new_user = User(
                user_id=user_id, username=username, guild_id=guild_id, team_id=team.id
            )
            db.add(new_user)

    db.commit()
    db.close()

    return f"✅ Team '{team_name}' is now linked to <#{channel_id}>, and members have been added!"


def add_user_to_team(user_id, guild_id, team_name):
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


def set_team_channel(payload, guild_id):
    team_name = payload["data"]["options"][0]["value"]
    channel_id = payload["data"]["options"][1]["value"]
    message = save_team_and_add_members(team_name, guild_id, channel_id)
    return {"type": 4, "data": {"content": message}}


def add_team_member(payload, guild_id):
    user_id = payload["data"]["options"][0]["value"]
    team_name = payload["data"]["options"][1]["value"]
    message = add_user_to_team(user_id, guild_id, team_name)
    return {"type": 4, "data": {"content": message}}


def submit_todo(payload, guild_id):
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


def model_resp(payload):
    custom_id = payload["data"]["custom_id"]
    if custom_id == "todos":
        user_input = payload["data"]["components"][0]["components"][0]["value"]
        user_name = payload["user"]["username"]
        
        avatar_hash = payload["user"]["avatar"]
        user_id = payload["user"]["id"]
        # Process the user's input

        db: Session = SessionLocal()
        user = db.query(User).filter_by(user_id=user_id).first()

        if not user:
            user = User(
                user_id=user_id,
                name=user_name,
                emp_id=f"emp_{user_id}",
                password_hash="",
                is_active=True,
            )
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

        # team_channel_id = get_team_channel(user_id, guild_id)
        # print(f"is channel id same -> {team_channel_id == "1332261881267879988"}")
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

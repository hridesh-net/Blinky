from datetime import date, datetime

from sqlalchemy.orm import Session

from db.models.team import Team
from db.models.task import Task
from db.models.user import User
from db.models.reward import Reward, RewardReason
from app.core.config import settings
from db.session import SessionLocal
from app.utils.post_utilities import post_to_grp
from app.crud.task import get_user_tasks

from app.utils.reward_audit import add_reward_transaction
from app.utils.server_utils import get_team_channel, get_team_members
from app.utils.base_utils import get_user_now


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

            user = (
                db.query(User)
                .filter_by(user_id=user_id, guild_id=guild_id, is_active=True)
                .first()
            )
            if not user:
                user = User(
                    user_id=user_id,
                    name=name,
                    username=username,
                    guild_id=guild_id,
                    is_active=True,
                )
                user.set_password("secure_password")
                db.add(user)
                db.commit()

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
                in_est=True,
            )
            user.set_password("secure_password")
            db.add(user)
            db.commit()
            db.refresh(user)

        user_now = get_user_now(user)
        today = user_now.date()

        for task in user_input.split("|"):
            new_task = Task(user_id=user.id, description=task.strip(), date=today)
            db.add(new_task)
        db.commit()
        # db.close()
        rewards = db.query(Reward).filter_by(user_id=user.id).first()
        print(f"Rewards: {rewards.kudos} and {rewards.streak}")

        kwargs = {
            "kudos": rewards.kudos if rewards else 0,
            "streak": rewards.streak if rewards else 0,
        }

        db.close()

        post_to_grp(
            "1332261881267879988",
            settings.DISCORD_TOKEN,
            user_name,
            user_input,
            user_id,
            avatar_hash,
            **kwargs,
        )
        return {
            "type": 4,
            "data": {"content": "✅ Your To-Do list has been saved!"},
        }


async def manage_tasks(user_id, guild_id, payload):
    user_id = payload["member"]["user"]["id"]
    db = SessionLocal()
    tasks = get_user_tasks(db, user_id)

    if not tasks:
        return {
            "type": 4,
            "data": {
                "content": "You have no tasks for today.",
                "flags": 64,  # Ephemeral message
            },
        }

    options = []
    for task in tasks:
        options.append(
            {
                "label": f"{task.description}",
                "value": f"{task.id}",
                "default": task.is_completed,
                "emoji": {"name": "✅" if task.is_completed else "❌"},
            }
        )

    select_menu = {
        "type": 3,
        "custom_id": "select_tasks",
        "options": options,
        "placeholder": "Select tasks you've completed",
        "min_values": 1,
        "max_values": len(options),
    }

    return {
        "data": {
            "content": "Here are your tasks for today:",
            "components": [{"type": 1, "components": [select_menu]}],
            "flags": 64,  # Ephemeral message
        }
    }


async def handle_task_selection(user_id, guild_id, payload):
    """Updates tasks in DB and manages streak/kudos logic."""

    db = SessionLocal()

    selected_task_ids = payload["data"]["values"]
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        db.close()
        return {"type": 4, "data": {"content": "❌ User not found!"}}

    user_now = get_user_now(user)
    today = user_now.date()
    user_tasks = (
        db.query(Task).filter(Task.user_id == user.id, Task.date == today).all()
    )

    if not user_tasks:
        db.close()
        return {"type": 4, "data": {"content": "❌ No tasks found for today!"}}

    completed_task_count = 0
    for task in user_tasks:
        print(f"Task ID: {task.id}, Completed: {task.is_completed}")
        if str(task.id) in selected_task_ids:
            print("full")
            if not task.is_completed:
                task.is_completed = True
                completed_task_count += 1

    db.commit()

    all_completed = all(task.is_completed for task in user_tasks)

    reward = db.query(Reward).filter_by(user_id=user.id).first()
    if not reward:
        reward = Reward(user_id=user.id, kudos=0, streak=0)
        db.add(reward)
        db.commit()

    today_weekday = today.weekday()  # Monday = 0, Sunday = 6
    is_weekend = today_weekday >= 5

    kudos_to_add = completed_task_count  # 1 kudos per completed task
    streak_bonus = 0

    if all_completed:
        reward.kudos += completed_task_count

        if not is_weekend:
            reward.streak += 1

        if completed_task_count > 0:
            if reward.streak % 7 == 0:  # Bonus every 7 days
                streak_bonus = 5  # Example bonus value
                reward.kudos += streak_bonus
                reward.streak = 0

    else:
        reward.kudos += completed_task_count

    db.commit()
    if kudos_to_add > 0:
        add_reward_transaction(
            db, user.id, kudos_to_add, "credit", RewardReason.TASK_COMPLETION
        )
    if streak_bonus > 0:
        add_reward_transaction(
            db, user.id, streak_bonus, "credit", RewardReason.STREAK_BONUS
        )

    message = f"✅ Tasks updated! You earned {completed_task_count} Kudos."
    if all_completed:
        if not is_weekend:  # Only show streak for weekdays
            message += f" Your streak is now {reward.streak} days."
        if reward.streak % 7 == 0:
            message += f" 🎉 You earned a streak bonus of 5 Kudos!"
    else:
        message += " Complete all tasks by EOD to maintain your streak."

    db.close()
    return {"type": 4, "data": {"content": message, "flags": 64}}

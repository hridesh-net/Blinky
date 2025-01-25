import json
import requests


def get_avatar_url(user_id, avatar_hash):
    return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"


def post_to_grp(channel_id, bot_token, user_name, todo_input, user_id, avatar_hash):
    tasks = [task.strip() for task in todo_input.split("|") if task.strip()]

    formatted_tasks = "\n".join(f"- {task}" for task in tasks)
    message_content = f"@{user_name} has submitted their To-Do list:\n{formatted_tasks}"

    avatar_url = get_avatar_url(user_id, avatar_hash)

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    payload = {
        "embeds": [
            {
                "title": f"@{user_name} has submitted their To-Do list",
                "description": formatted_tasks,
                "color": 5814783,  # Custom color (Optional)
                "thumbnail": {"url": avatar_url},  # User Avatar
                "fields": [
                    {
                        "name": "Total Kudos 💎",
                        "value": "0",  # Replace with actual Kudos if available
                        "inline": True,
                    },
                    {
                        "name": "Current Streak 🔥",
                        "value": "0",  # Replace with actual streak if available
                        "inline": True,
                    },
                ],
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message: {response.status_code} - {response.text}")

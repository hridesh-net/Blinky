from app.utils.register_commands import register_test_cmd

commands = [
    {
        "name": "set_team_channel",
        "description": "Set a team's To-Do posting channel",
        "type": 1,
        "options": [
            {
                "name": "team_name",
                "description": "Name of the team",
                "type": 3,
                "required": True,
            },
            {
                "name": "channel",
                "description": "Select a text channel",
                "type": 7,  # Channel type
                "required": True,
            },
        ],
    },
    {
        "name": "add_team_member",
        "description": "Add a user to a team",
        "type": 1,
        "options": [
            {
                "name": "user",
                "description": "Select a user",
                "type": 6,  # User type
                "required": True,
            },
            {
                "name": "team_name",
                "description": "Team to assign the user",
                "type": 3,
                "required": True,
            },
        ],
    },
    {
        "name": "submit_todo",
        "description": "Submit your To-Do list",
        "type": 1,
        "options": [
            {
                "name": "tasks",
                "description": "Enter tasks separated by |",
                "type": 3,
                "required": True,
            }
        ],
    },
]

register_test_cmd(commands=commands)

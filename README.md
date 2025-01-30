![header](Turons_Letter.png)

# Blinky - The Interactive Team To-Do Bot 🎯

Blinky is a **Discord bot** designed to make daily tasks more interactive and fun for teams. It encourages team members to submit their daily to-dos, track their progress, and earn rewards like kudos and streaks. **No more boring to-do lists! Blinky gamifies productivity in your Discord workspace.** 🎮✨

## 🌟 Features

- 🕒 **Automated Daily Reminders** - Sends scheduled reminders at **6:30 PM IST** (configurable).
- ✅ **To-Do Submissions** - Users submit their daily tasks through a modal input.
- 📌 **Team-Based Organization** - Automatically assigns users to teams based on Discord channels.
- 🏆 **Streaks & Kudos** - Tracks engagement with streak counters and kudos rewards.
- 📡 **FastAPI Backend** - Built on **FastAPI** for seamless API interactions.
- ⚡ **AWS Lambda Integration** - Handles scheduled reminders efficiently.
- 🔄 **Database Persistence** - Stores users, teams, and tasks in **PostgreSQL** using SQLAlchemy.
- 📊 **Real-Time Updates** - To-Do lists are posted in team channels with avatars & stats.

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.12+
- PostgreSQL
- Docker (for DB setup)
- FastAPI
- Requests (for Discord API interactions)
- Uvicorn (ASGI Server)
- SQLAlchemy & Alembic (Database ORM & Migrations)

### Directory Structure
```sh
.
├── README.md
├── alembic.ini
├── app
│   ├── api
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1
│   │       ├── __init__.py
│   │       └── endpoints
│   │           ├── __init__.py
│   │           ├── audit_log.py
│   │           ├── discord_interactions.py
│   │           ├── reward.py
│   │           ├── task.py
│   │           └── user.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── cmd
│   │   │   └── slash_cmd.py
│   │   ├── config.py
│   │   └── config_prod.py
│   ├── crud
│   │   ├── __init__.py
│   │   ├── audit_log.py
│   │   ├── reward.py
│   │   ├── role.py
│   │   ├── task.py
│   │   └── user.py
│   └── utils
│       ├── __init__.py
│       ├── post_utilities.py
│       ├── register_commands.py
│       └── security.py
├── daily_sch.py
├── datatest.py
├── db
│   ├── __init__.py
│   ├── base.py
│   ├── migrations
│   │   ├── README
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── models
│   │   ├── __init__.py
│   │   ├── audit_log.py
│   │   ├── notification.py
│   │   ├── reward.py
│   │   ├── role.py
│   │   ├── task.py
│   │   ├── team.py
│   │   └── user.py
│   └── session.py
├── main.py
├── register_cmd.py
├── requirements.txt
├── schemas
│   ├── __init__.py
│   ├── audit_log.py
│   ├── reward.py
│   ├── role.py
│   ├── task.py
│   └── user.py
└── tests
    ├── __init__.py
    ├── test_audit_log.py
    ├── test_reward.py
    ├── test_task.py
    └── test_user.py
```

### Installation

```sh
# Clone the repository
git clone https://github.com/hridesh-net/blinky.git
cd blinky

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### Setting Up the Database

```sh
# Run PostgreSQL in Docker
docker run --name postgres_db -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres:latest

# Apply migrations
alembic upgrade head
```

### Running the Bot

```sh
uvicorn main:app --reload
```

## 🎮 Usage

### 1️⃣ Register the Bot

Invite the bot to your Discord server and register the following commands:

```sh
/assign-team-channel  # Assigns a team to a specific channel
/add-todo  # Adds your daily tasks
/check-todos  # Checks all submitted To-Dos
```

### 2️⃣ Setting Up Team Channels

Run `/assign-team-channel` in a Discord channel to link it to a team.

### 3️⃣ Submitting To-Dos

Click the **Add Today's Checklist** button in your DM, enter your tasks (separated by '|'), and hit submit.

### 4️⃣ Viewing To-Dos

Blinky posts a card in the team channel with:

- ✅ Submitted Tasks
- 🏅 User Avatar & Name
- 💎 Kudos Count
- 🔥 Streak Status

## 🔧 Configuration

### Environment Variables (`.env`)

```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_PUBLIC_KEY=your_public_key
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📜 API Endpoints

| Endpoint            | Method | Description                  |
| ------------------- | ------ | ---------------------------- |
| `/interactions`     | POST   | Handles Discord interactions |
| `/set-team-channel` | POST   | Sets the team channel        |
| `/submit-todo`      | POST   | Submits user tasks           |

## 🤝 Contributors

Thank you to all the amazing contributors who helped bring Blinky to life! 🎉

👤 **Hridesh Sharma** - [GitHub](https://github.com/hridesh-net)\
👤 **Your Name Here** - [GitHub](https://github.com/your-profile)

Want to contribute? Feel free to submit a PR or open an issue! 🚀

## 📄 License

MIT License © 2025 Hridesh Sharma

---

Made with ❤️ to make teamwork **fun & productive**! 🚀


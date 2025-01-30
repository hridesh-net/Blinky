from datetime import date
from sqlalchemy import DateTime, func

from app.utils.base_utils import get_user_now
from db.models.task import Task
from db.models.user import User

def get_user_tasks(db, user_id):
    # db: Session = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id, is_active=True).first()
    if not user:
        return []

    user_now = get_user_now(user)
    today = user_now.date()

    tasks_query = db.query(Task).filter_by(user_id=user.id)

    if isinstance(Task.date.type, DateTime):
        tasks_query = tasks_query.filter(func.DATE(Task.date) == today)
    else:
        tasks_query = tasks_query.filter(Task.date == today)

    tasks = tasks_query.all()
    return tasks
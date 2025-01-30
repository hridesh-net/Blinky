import pytz
from datetime import datetime

EST = pytz.timezone("America/New_York")

def get_user_now(user):
    now = datetime.utcnow()
    return now.astimezone(EST) if user.in_est else now
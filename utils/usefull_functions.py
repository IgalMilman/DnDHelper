from datetime import datetime
import pytz

def time_now(instance=None):
    return datetime.now(pytz.utc)
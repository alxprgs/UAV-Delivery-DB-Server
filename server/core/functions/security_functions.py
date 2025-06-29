from server import app
from datetime import datetime, timedelta

def banned(ip: str) -> bool:
    until = app.state.blocked.get(ip)
    if until and until > datetime.utcnow():
        return True
    app.state.blocked.pop(ip, None)
    return False
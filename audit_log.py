from db import Session, AuditLogMessage
from config import config

PLAYER_NAME = config.get('Player', 'player_name')
LOGGING_ENABLED = config.get('Logging', 'enabled')

def log(user, message):
    if not LOGGING_ENABLED:
        return
    session = Session()
    message = AuditLogMessage(
            user=user, message=message, player_name=PLAYER_NAME)
    session.add(message)
    session.commit()

from db import Session, AuditLogMessage
from config import config

PLAYER_NAME = config.get('Player', 'player_name')

def log(user, message):
    session = Session()
    message = AuditLogMessage(
            user=user, message=message, player_name=PLAYER_NAME)
    session.add(message)
    session.commit()

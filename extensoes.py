from flask_mail import Mail
from flask_socketio import SocketIO

mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")

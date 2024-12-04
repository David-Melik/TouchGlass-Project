from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()  # Initialize the SQLAlchemy instance

from .user import User, friendship_association
from .preferences import Preferences
from .event import Event
from .notification import Notification

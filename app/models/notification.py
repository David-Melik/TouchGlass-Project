from . import db  # Import the db instance from the __init__.py
from .event import Event
from datetime import datetime


# Define Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(
        db.String(50), nullable=False
    )  # Action (Created, Updated, Deleted)
    message = db.Column(db.Text, nullable=False)  # Details about the event change
    timestamp = db.Column(db.DateTime, default=datetime.now)  # Timestamp of the change
    event_id = db.Column(
        db.Integer, db.ForeignKey("event.event_id"), nullable=True
    )  # Link to the event

    # Relationship with Event
    event = db.relationship("Event", backref=db.backref("notifications", lazy=True))

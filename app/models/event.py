from . import db
from sqlalchemy import func


# Define the Event model for the database
class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    date_event = db.Column(db.DateTime, nullable=False)
    localisation = db.Column(db.String(255), nullable=False)
    age_requirement = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rules = db.Column(db.Text, nullable=True)
    average_price = db.Column(db.String(50), nullable=True)
    student_advantages = db.Column(db.Text, nullable=True)
    event_type = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime, default=func.now()
    )  # Timestamp for when the event is created
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Timestamp for when the event is updated

    def __repr__(self):
        return f"<Event {self.title}>"  # Representation of the event object

    # Define Event Model


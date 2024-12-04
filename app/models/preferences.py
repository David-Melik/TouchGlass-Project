from . import db  # Import the db instance from the __init__.py

class Preferences(db.Model):
    __tablename__ = 'preferences'
    preferences_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    locations = db.Column(db.String(255), nullable=False)
    music_genre = db.Column(db.String(255), nullable=False)

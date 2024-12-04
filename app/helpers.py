import os
from flask import current_app
from .models import db, User, Preferences
from werkzeug.security import generate_password_hash
from datetime import datetime


def add_preference(user_id, locations, music_genre):
    new_preference = Preferences(
        user_id=user_id, locations=locations, music_genre=music_genre
    )
    db.session.add(new_preference)
    db.session.commit()


def get_user_preferences(user_id):
    return Preferences.query.filter_by(user_id=user_id).first()


def create_database(app):  # Accept the app instance as a parameter
    db_path = "database.db"  # Path to SQLite database file
    if os.path.exists(db_path):
        os.remove(
            db_path
        )  # Delete the existing database file to avoid schema mismatches
    with app.app_context():  # Use the app context passed in
        db.create_all()  # Create tables for User Preferences and Events
        print("Database created successfully.")

        # Check if any users exist (not just admin)
        if not User.query.first():
            admin_user = User(
                user_name="admin",
                surname="Admin",
                name="System",
                ddn=datetime(1970, 1, 1),  # Arbitrary date
                email="admin@example.com",
                sex="Other",
                password=generate_password_hash("admin123"),  # Default password
                is_admin=True,
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created.")

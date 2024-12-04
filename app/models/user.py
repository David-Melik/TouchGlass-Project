from sqlalchemy import func, Boolean
from . import db  # Import the db instance from the __init__.py
from sqlalchemy import Column, Integer, DateTime, String, func, ForeignKey
from sqlalchemy.orm import relationship

# To initialize the friendTable
friendship_association = db.Table(
    "friendships",  # Table name in the database
    db.Model.metadata,  # Use SQLAlchemy's metadata to define the table
    Column(
        "user_id", Integer, ForeignKey("users.user_id"), primary_key=True
    ),  # Foreign key to `User`
    Column(
        "friend_id", Integer, ForeignKey("users.user_id"), primary_key=True
    ),  # Foreign key to `User`
    Column("status", String(10), default="requested"),  # Track the friendship status
)


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    ddn = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Added is_admin attribute
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    preferences = db.relationship(
        "Preferences", backref="user", lazy=True
    )  # Establishing a many-to-many relationship with the friendship association table
    friends = relationship(
        "User",
        secondary=friendship_association,  # The association table we created
        primaryjoin=user_id
        == friendship_association.c.user_id,  # Link where the user's `user_id` matches
        secondaryjoin=user_id
        == friendship_association.c.friend_id,  # Link where the friend's `user_id` matches
        backref="friend_of",  # Allows reverse lookup (who has the user as a friend)
        lazy="dynamic",  # Allows us to add a filter later
    )

    def __repr__(self):
        return f"<User {self.user_name}>"

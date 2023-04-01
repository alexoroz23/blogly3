"""SQLAlchemy models for blogly."""

import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Default image URL for user profile
DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"

# User model
class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    # Columns in the 'users' table
    id = db.Column(db.Integer, primary_key=True) # Primary key for the user
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False, default=DEFAULT_IMAGE_URL) # Image URL for the user profile

    # Relationship between the 'users' table and the 'posts' table
    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

    @property
    def full_name(self):
        """Return full name of user."""

        return f"{self.first_name} {self.last_name}"

# Post model
class Post(db.Model):
    """Blog post."""

    __tablename__ = "posts"

    # Columns in the 'posts' table
    id = db.Column(db.Integer, primary_key=True) # Primary key for the post
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now) # Timestamp for when the post was created
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Foreign key for the user who created the post

    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p") # Format the date and time in a user-friendly way

class Tag(db.Model):
    """Tag Model"""

    __tablename__ = "tags"

    # Columns in the 'tags' table
    id = db.Column(db.Integer, primary_key=True) # Primary key for the tag
    name = db.Column(db.String(50), nullable=False, unique=True) # Name of the tag

    # Define the many-to-many relationship with posts
    posts = db.relationship("Post", secondary="post_tags", backref="tags")

# PostTag model
class PostTag(db.Model):
    """Between posts and tags."""

    __tablename__ = "posts_tags"

    # Columns in the 'posts_tags' table
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), primary_key=True) # Foreign key for the post
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), primary_key=True) # Foreign key for the tag

# Function to connect the app to the database
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

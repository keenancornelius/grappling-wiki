"""
User model for Flask wiki application.
Handles user accounts, authentication, and role management.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(db.Model, UserMixin):
    """
    User account model with authentication and role management.

    Attributes:
        id: Primary key
        username: Unique username for login
        email: Unique email address
        password_hash: Hashed password (never store plaintext)
        bio: Optional user biography
        created_at: Account creation timestamp
        is_admin: Boolean flag for admin privileges
        is_editor: Boolean flag for editor privileges
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_editor = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    articles = db.relationship(
        'Article',
        backref='author',
        lazy='dynamic',
        foreign_keys='Article.author_id'
    )
    revisions = db.relationship(
        'ArticleRevision',
        backref='editor',
        lazy='dynamic',
        foreign_keys='ArticleRevision.editor_id'
    )
    discussions = db.relationship(
        'Discussion',
        backref='author',
        lazy='dynamic',
        foreign_keys='Discussion.author_id'
    )
    discussion_replies = db.relationship(
        'DiscussionReply',
        backref='author',
        lazy='dynamic',
        foreign_keys='DiscussionReply.author_id'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        Hash and set the user's password.

        Args:
            password: Plaintext password to hash
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify a plaintext password against the stored hash.

        Args:
            password: Plaintext password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def get_articles(self, published_only=True):
        """
        Get articles authored by this user.

        Args:
            published_only: If True, only return published articles

        Returns:
            Query: SQLAlchemy query of Article objects
        """
        query = self.articles
        if published_only:
            query = query.filter_by(is_published=True)
        return query.order_by(Article.created_at.desc())

    def can_edit(self):
        """
        Check if user has editing privileges.

        Returns:
            bool: True if user is admin or editor
        """
        return self.is_admin or self.is_editor

    def can_moderate(self):
        """
        Check if user has moderation privileges.

        Returns:
            bool: True if user is admin
        """
        return self.is_admin


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.

    Args:
        user_id: User ID from session

    Returns:
        User: User object or None
    """
    return User.query.get(int(user_id))

"""
Discussion models for Flask wiki application.
Handles talk pages and community discussions about articles.
"""

from datetime import datetime
from app import db


class Discussion(db.Model):
    """
    Discussion (talk page) for article collaboration.
    Allows users to discuss changes and improvements to articles.

    Attributes:
        id: Primary key
        article_id: Foreign key to Article being discussed
        author_id: Foreign key to User who started the discussion
        title: Discussion thread title
        content: Initial discussion content
        created_at: When discussion was created
        is_resolved: Whether discussion has been resolved
    """

    __tablename__ = 'discussions'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_resolved = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # Relationships
    replies = db.relationship(
        'DiscussionReply',
        backref='discussion',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='DiscussionReply.discussion_id'
    )

    __table_args__ = (
        db.Index('idx_article_created', 'article_id', 'created_at'),
        db.Index('idx_resolved', 'is_resolved'),
    )

    def __repr__(self):
        return f'<Discussion article_id={self.article_id} title={self.title}>'

    def add_reply(self, author, content):
        """
        Add a reply to this discussion thread.

        Args:
            author: User object making the reply
            content: Text content of the reply

        Returns:
            DiscussionReply: The created reply object
        """
        reply = DiscussionReply(
            discussion_id=self.id,
            author_id=author.id,
            content=content
        )
        db.session.add(reply)
        db.session.commit()
        return reply

    def get_reply_count(self):
        """
        Get the number of replies to this discussion.

        Returns:
            int: Count of replies
        """
        return self.replies.count()

    def mark_resolved(self):
        """Mark this discussion as resolved."""
        self.is_resolved = True
        db.session.commit()

    def mark_unresolved(self):
        """Mark this discussion as unresolved."""
        self.is_resolved = False
        db.session.commit()


class DiscussionReply(db.Model):
    """
    Reply to a discussion thread.
    Allows community members to participate in article discussions.

    Attributes:
        id: Primary key
        discussion_id: Foreign key to parent Discussion
        author_id: Foreign key to User who authored the reply
        content: Text content of the reply
        created_at: When reply was created
    """

    __tablename__ = 'discussion_replies'

    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.Index('idx_discussion_created', 'discussion_id', 'created_at'),
        db.Index('idx_author_created', 'author_id', 'created_at'),
    )

    def __repr__(self):
        return f'<DiscussionReply discussion_id={self.discussion_id} author_id={self.author_id}>'

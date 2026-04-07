"""
Moderation models for content flagging and audit logging.
"""

from datetime import datetime
from app import db


class ContentFlag(db.Model):
    """
    User-submitted flag on an article or revision for mod review.

    Attributes:
        id: Primary key
        article_id: The flagged article
        revision_id: Optionally, the specific revision flagged
        reporter_id: User who submitted the flag
        reason: Category of the flag
        details: Free-text explanation
        status: pending / reviewed / dismissed / actioned
        reviewed_by_id: Mod who reviewed the flag
        reviewed_at: When it was reviewed
        resolution_note: What the mod decided
    """

    __tablename__ = 'content_flags'

    REASONS = [
        'vandalism',
        'inaccurate',
        'spam',
        'offensive',
        'copyright',
        'other',
    ]

    REASON_LABELS = {
        'vandalism': 'Vandalism / defacement',
        'inaccurate': 'Inaccurate information',
        'spam': 'Spam or advertising',
        'offensive': 'Offensive content',
        'copyright': 'Copyright violation',
        'other': 'Other',
    }

    STATUSES = ['pending', 'reviewed', 'dismissed', 'actioned']

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)
    revision_id = db.Column(db.Integer, db.ForeignKey('article_revisions.id'), nullable=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reason = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    resolution_note = db.Column(db.Text, nullable=True)

    # Relationships
    article = db.relationship('Article', foreign_keys=[article_id],
                              backref=db.backref('flags', lazy='dynamic'))
    reporter = db.relationship('User', foreign_keys=[reporter_id],
                               backref=db.backref('flags_submitted', lazy='dynamic'))
    reviewer = db.relationship('User', foreign_keys=[reviewed_by_id])
    revision = db.relationship('ArticleRevision', foreign_keys=[revision_id])

    __table_args__ = (
        db.Index('idx_flag_status_date', 'status', 'created_at'),
    )

    def __repr__(self):
        return f'<ContentFlag article={self.article_id} reason={self.reason} status={self.status}>'


class ModAction(db.Model):
    """
    Audit log entry for moderation actions.
    Every ban, suspension, article lock, rollback, etc. is recorded here.
    """

    __tablename__ = 'mod_actions'

    ACTIONS = [
        'ban_user', 'unban_user',
        'suspend_user', 'unsuspend_user',
        'promote_editor', 'demote_editor',
        'promote_admin', 'demote_admin',
        'lock_article', 'unlock_article',
        'unpublish_article', 'publish_article',
        'delete_article',
        'rollback_revision',
        'resolve_flag', 'dismiss_flag',
    ]

    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    target_article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=True)
    target_revision_id = db.Column(db.Integer, db.ForeignKey('article_revisions.id'), nullable=True)
    target_flag_id = db.Column(db.Integer, db.ForeignKey('content_flags.id'), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    moderator = db.relationship('User', foreign_keys=[moderator_id],
                                backref=db.backref('mod_actions', lazy='dynamic'))
    target_user = db.relationship('User', foreign_keys=[target_user_id])
    target_article = db.relationship('Article', foreign_keys=[target_article_id])

    __table_args__ = (
        db.Index('idx_mod_action_date', 'action_type', 'created_at'),
    )

    def __repr__(self):
        return f'<ModAction {self.action_type} by={self.moderator_id}>'

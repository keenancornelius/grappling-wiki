"""
Article models for Flask wiki application.
Handles articles, tags, revisions, and version history.
"""

from datetime import datetime
from app import db


# Association table for many-to-many relationship between Articles and Tags
article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Tag(db.Model):
    """
    Category tag for organizing articles.

    Attributes:
        id: Primary key
        name: Unique tag name (e.g., 'Guard Passing')
        slug: URL-friendly slug for tag
        description: Optional description of the tag
    """

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Tag {self.name}>'


class Article(db.Model):
    """
    Main article model for wiki content.

    Attributes:
        id: Primary key
        title: Article title
        slug: URL-friendly slug (unique and indexed for quick lookups)
        content: Markdown content of the article
        summary: Brief summary for previews
        author_id: Foreign key to User who created the article
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        is_published: Whether article is publicly visible
        is_protected: Whether article requires elevated privileges to edit
        view_count: Number of times article has been viewed
        category: Article category (technique, position, concept, person, competition, glossary, style)

    Taxonomy fields (English-from-Japanese naming convention):
        mechanism:         What kind of action — lock, choke, entanglement, throw, reap, sweep, pass, etc.
                           Maps to Japanese suffixes: Gatame→lock, Jime→choke, Garami→entanglement,
                           Nage→throw, Gari→reap, Harai→sweep, Gake→hook, Otoshi→drop, Guruma→wheel.
        target:            Body part involved — arm, leg, neck, hip, shoulder, knee, ankle, wrist, body.
                           Maps to Japanese prefixes: Ude→arm, Ashi→leg, Koshi→hip, Kata→shoulder.
        spatial_qualifier: Directional modifier — inner, outer, major, minor, forward, rear, cross,
                           triangle, naked, side. Maps to: Uchi→inner, Soto→outer, O→major, Ko→minor,
                           Mae→forward, Ushiro→rear, Juji→cross, Sankaku→triangle, Hadaka→naked.
        graph_tier:        Comma-separated sys_ node IDs from graph-engine.js indicating where this
                           article lives in the inverse tree (e.g. 'sys_close_guard,sys_mount').
                           Drives the categories page hierarchy and graph node placement.
        taxonomy_complete: True when graph_tier + mechanism are both set for Technique/Position/Concept
                           articles. False flags the article as needing taxonomy metadata.
                           Person, Competition, Style, Glossary articles default to True.
    """

    __tablename__ = 'articles'

    # Valid article categories
    VALID_CATEGORIES = ['technique', 'position', 'concept', 'person', 'competition', 'glossary', 'style']

    # Categories excluded from the knowledge graph (no taxonomy required)
    NON_GRAPH_CATEGORIES = ['person', 'competition', 'style', 'glossary']

    # Controlled vocabulary for taxonomy fields
    VALID_MECHANISMS = [
        'lock',          # Joint hyperextension (Gatame)
        'choke',         # Blood/air restriction (Jime/Shime)
        'entanglement',  # Rotational joint attack (Garami)
        'compression',   # Crushing (slicers)
        'throw',         # Projection (Nage)
        'reap',          # Leg reap takedown (Gari)
        'sweep',         # Positional reversal (Harai)
        'pass',          # Guard passing
        'hook',          # Hooking technique (Gake)
        'drop',          # Drop technique (Otoshi)
        'wheel',         # Rotation-based throw (Guruma)
        'pin',           # Holding position (Osae)
        'concept',       # Strategic/positional concept
    ]

    VALID_TARGETS = [
        'arm',       # Ude
        'leg',       # Ashi
        'neck',      # throat/neck chokes
        'hip',       # Koshi
        'shoulder',  # Kata
        'knee',
        'ankle',
        'wrist',
        'body',      # whole-body / positional
    ]

    VALID_SPATIAL = [
        'inner',     # Uchi
        'outer',     # Soto
        'major',     # O (large)
        'minor',     # Ko (small)
        'forward',   # Mae
        'rear',      # Ushiro
        'side',      # Yoko
        'cross',     # Juji
        'triangle',  # Sankaku
        'naked',     # Hadaka (exposed/bare)
    ]

    # Valid graph tier node IDs (from graph-engine.js SYSTEM_NODES)
    VALID_GRAPH_TIERS = [
        'sys_standing',
        'sys_upper_td',
        'sys_lower_td',
        'sys_far_guard',
        'sys_mid_guard',
        'sys_close_guard',
        'sys_leg_entangle',
        'sys_front_headlock',
        'sys_side_control',
        'sys_mount',
        'sys_kob',
        'sys_back_control',
    ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    is_published = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_protected = db.Column(db.Boolean, nullable=False, default=False)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(
        db.String(50),
        nullable=False,
        default='technique',
        index=True
    )

    # ── Taxonomy: English-from-Japanese naming convention ──
    mechanism = db.Column(db.String(50), nullable=True, index=True)
    target = db.Column(db.String(50), nullable=True, index=True)
    spatial_qualifier = db.Column(db.String(50), nullable=True)
    # Comma-separated sys_ tier IDs, e.g. 'sys_close_guard,sys_mount'
    graph_tier = db.Column(db.String(200), nullable=True, index=True)
    # False = article needs taxonomy metadata; flagged in UI
    taxonomy_complete = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # Relationships
    tags = db.relationship(
        'Tag',
        secondary=article_tags,
        backref=db.backref('articles', lazy='dynamic')
    )
    revisions = db.relationship(
        'ArticleRevision',
        backref='article',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='ArticleRevision.article_id'
    )
    discussions = db.relationship(
        'Discussion',
        backref='article',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='Discussion.article_id'
    )

    def __repr__(self):
        return f'<Article {self.title}>'

    def __init__(self, *args, **kwargs):
        """Validate category on initialization."""
        super().__init__(*args, **kwargs)
        if self.category and self.category not in self.VALID_CATEGORIES:
            raise ValueError(f'Invalid category. Must be one of: {", ".join(self.VALID_CATEGORIES)}')
        # Non-graph categories are always taxonomy_complete
        if self.category in self.NON_GRAPH_CATEGORIES:
            self.taxonomy_complete = True

    def compute_taxonomy_complete(self):
        """
        Recompute and set taxonomy_complete based on current fields.
        Call this after setting mechanism/graph_tier on Technique, Position, Concept articles.
        Non-graph categories (Person, Competition, Style, Glossary) are always complete.
        """
        if self.category in self.NON_GRAPH_CATEGORIES:
            self.taxonomy_complete = True
        else:
            # Require at minimum: graph_tier and mechanism
            self.taxonomy_complete = bool(self.graph_tier and self.mechanism)
        return self.taxonomy_complete

    def get_graph_tiers(self):
        """
        Return graph_tier as a list of sys_ node IDs.
        e.g. 'sys_close_guard,sys_mount' → ['sys_close_guard', 'sys_mount']
        """
        if not self.graph_tier:
            return []
        return [t.strip() for t in self.graph_tier.split(',') if t.strip()]

    def taxonomy_display_name(self):
        """
        Build the English-from-Japanese display name from taxonomy components.
        Format: '{Spatial} {Target} {Mechanism}' — omits None components.
        e.g. spatial=cross, target=arm, mechanism=lock → 'Cross Arm Lock'
        Falls back to article title if components are unset.
        """
        parts = []
        if self.spatial_qualifier:
            parts.append(self.spatial_qualifier.title())
        if self.target:
            parts.append(self.target.title())
        if self.mechanism:
            parts.append(self.mechanism.title())
        return ' '.join(parts) if parts else self.title

    def get_latest_revision(self):
        """
        Get the most recent revision of this article.

        Returns:
            ArticleRevision: Latest revision or None if no revisions exist
        """
        return self.revisions.order_by(ArticleRevision.created_at.desc()).first()

    def get_revision_diff(self, rev1, rev2):
        """
        Generate a diff between two revisions.

        Args:
            rev1: First ArticleRevision object (older)
            rev2: Second ArticleRevision object (newer)

        Returns:
            dict: Dictionary with keys 'rev1', 'rev2', 'diff_lines' containing unified diff
        """
        import difflib

        content1 = rev1.content.splitlines(keepends=True) if rev1 else []
        content2 = rev2.content.splitlines(keepends=True) if rev2 else []

        diff = list(difflib.unified_diff(content1, content2, lineterm=''))

        return {
            'rev1': rev1,
            'rev2': rev2,
            'diff_lines': diff
        }

    def increment_view_count(self):
        """Increment the article's view counter."""
        self.view_count += 1
        db.session.commit()

    def add_tag(self, tag):
        """
        Add a tag to this article.

        Args:
            tag: Tag object to add
        """
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """
        Remove a tag from this article.

        Args:
            tag: Tag object to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)


class ArticleRevision(db.Model):
    """
    Version history entry for articles.
    Allows tracking of changes and reverting to previous versions.

    Attributes:
        id: Primary key
        article_id: Foreign key to Article
        editor_id: Foreign key to User who made the revision
        content: Content at this revision
        edit_summary: Brief description of changes
        created_at: When this revision was created
        revision_number: Sequential revision number
        parent_revision_id: Self-referential FK to previous revision
    """

    __tablename__ = 'article_revisions'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    edit_summary = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    revision_number = db.Column(db.Integer, nullable=False)
    parent_revision_id = db.Column(
        db.Integer,
        db.ForeignKey('article_revisions.id'),
        nullable=True
    )

    # Self-referential relationship for revision chain
    parent_revision = db.relationship(
        'ArticleRevision',
        remote_side=[id],
        backref='child_revisions'
    )

    __table_args__ = (
        db.UniqueConstraint('article_id', 'revision_number', name='uq_article_revision_num'),
        db.Index('idx_article_editor', 'article_id', 'editor_id'),
        db.Index('idx_revision_date', 'created_at'),
    )

    def __repr__(self):
        return f'<ArticleRevision article_id={self.article_id} rev={self.revision_number}>'

    def get_next_revision(self):
        """
        Get the revision that follows this one.

        Returns:
            ArticleRevision: Next revision or None if this is the latest
        """
        return ArticleRevision.query.filter_by(
            article_id=self.article_id,
            parent_revision_id=self.id
        ).first()

    def get_previous_revision(self):
        """
        Get the revision that precedes this one.

        Returns:
            ArticleRevision: Previous revision or None if this is the first
        """
        return self.parent_revision

    def is_latest(self):
        """
        Check if this is the latest revision of the article.

        Returns:
            bool: True if no child revisions exist
        """
        return len(self.child_revisions) == 0

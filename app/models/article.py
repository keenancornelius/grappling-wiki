"""
Article models for Flask wiki application.
Handles articles, categories, revisions, relationships, and version history.
"""

from datetime import datetime
from app import db


class Category(db.Model):
    """
    User-created category with nesting support.

    Categories replace the old fixed VALID_CATEGORIES list + Tag model.
    Any logged-in user can create new categories or subcategories.
    Nesting is achieved via the parent_id self-referential foreign key.

    Examples:
        Technique (top-level)
        ├── Submission
        │   ├── Choke
        │   └── Joint Lock
        ├── Sweep
        └── Pass

    Attributes:
        id:          Primary key
        name:        Display name (e.g., 'Joint Lock')
        slug:        URL-friendly slug (unique, indexed)
        description: Optional description of the category
        parent_id:   FK to parent category (NULL = top-level)
        created_by_id: User who created this category
        created_at:  Creation timestamp
    """

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Self-referential relationship for nesting
    children = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side='Category.id'),
        lazy='dynamic',
        cascade='all, delete-orphan',
    )
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def __repr__(self):
        return f'<Category {self.name}>'

    @property
    def breadcrumb(self):
        """Return list of categories from root to self."""
        chain = [self]
        current = self
        while current.parent:
            current = current.parent
            chain.append(current)
        return list(reversed(chain))

    @property
    def breadcrumb_str(self):
        """Return 'Root > Child > Grandchild' style string."""
        return ' > '.join(c.name for c in self.breadcrumb)

    @property
    def depth(self):
        """Return nesting depth (0 = top-level)."""
        d = 0
        current = self
        while current.parent:
            current = current.parent
            d += 1
        return d

    def descendants(self):
        """Return flat list of all descendant categories (recursive)."""
        result = []
        for child in self.children.all():
            result.append(child)
            result.extend(child.descendants())
        return result


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
        category_id: Foreign key to Category
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        is_published: Whether article is publicly visible
        is_protected: Whether article requires elevated privileges to edit
        view_count: Number of times article has been viewed
    """

    __tablename__ = 'articles'

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

    # ── Category FK (replaces old string column) ──
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)

    # Keep a plain-text category column for backwards compatibility during migration.
    # Old articles have category='technique' etc. New articles set category_id.
    # Once all articles are migrated, this column can be dropped.
    category = db.Column(db.String(50), nullable=True, index=True)

    # Relationships
    category_ref = db.relationship('Category', backref=db.backref('articles', lazy='dynamic'))
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

    @property
    def category_name(self):
        """Return the category display name (from FK or legacy string)."""
        if self.category_ref:
            return self.category_ref.name
        return (self.category or '').title()

    @property
    def category_slug(self):
        """Return the category slug (from FK or legacy string)."""
        if self.category_ref:
            return self.category_ref.slug
        return self.category or ''

    def get_latest_revision(self):
        """Get the most recent revision of this article."""
        return self.revisions.order_by(ArticleRevision.created_at.desc()).first()

    def get_revision_diff(self, rev1, rev2):
        """Generate a diff between two revisions."""
        import difflib
        content1 = rev1.content.splitlines(keepends=True) if rev1 else []
        content2 = rev2.content.splitlines(keepends=True) if rev2 else []
        diff = list(difflib.unified_diff(content1, content2, lineterm=''))
        return {'rev1': rev1, 'rev2': rev2, 'diff_lines': diff}

    def increment_view_count(self):
        """Increment the article's view counter."""
        self.view_count += 1
        db.session.commit()


class ArticleRelationship(db.Model):
    """
    Typed, directional relationship between two articles.

    Instead of hardcoded graph connections, articles declare how they
    relate to each other via relationship tags. This powers the knowledge
    graph layout, the "Related" sidebar, and category-style browsing.

    Examples:
        Armbar  --submits_from-->  Mount
        Scissor Sweep  --transitions_to-->  Mount
        Turtle  --escapes_from-->  Back Control
        Kimura  --variation_of-->  Americana
        Half Guard  --counters-->  Guard Pass

    Attributes:
        id:                Primary key
        source_article_id: The article declaring the relationship (FK)
        target_article_id: The article being related to (FK)
        relationship_type: The kind of edge (see VALID_TYPES)
        notes:             Optional free-text context for the relationship
        created_at:        When this relationship was created
        created_by_id:     User who created this relationship (FK)
    """

    __tablename__ = 'article_relationships'

    # Controlled vocabulary for relationship types.
    VALID_TYPES = [
        'submits_from',
        'transitions_to',
        'escapes_from',
        'counters',
        'sets_up',
        'variation_of',
        'requires_position',
        'part_of_system',
        'related_to',
    ]

    TYPE_LABELS = {
        'submits_from':      'Submits from',
        'transitions_to':    'Transitions to',
        'escapes_from':      'Escapes from',
        'counters':          'Counters',
        'sets_up':           'Sets up',
        'variation_of':      'Variation of',
        'requires_position': 'Requires position',
        'part_of_system':    'Part of system',
        'related_to':        'Related to',
    }

    INVERSE_LABELS = {
        'submits_from':      'Has submission',
        'transitions_to':    'Reached from',
        'escapes_from':      'Escaped via',
        'counters':          'Countered by',
        'sets_up':           'Set up by',
        'variation_of':      'Has variation',
        'requires_position': 'Enables technique',
        'part_of_system':    'Contains',
        'related_to':        'Related to',
    }

    id = db.Column(db.Integer, primary_key=True)
    source_article_id = db.Column(
        db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True
    )
    target_article_id = db.Column(
        db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True
    )
    relationship_type = db.Column(db.String(50), nullable=False, index=True)
    notes = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True
    )

    # Relationships
    source_article = db.relationship(
        'Article', foreign_keys=[source_article_id],
        backref=db.backref('outgoing_relationships', lazy='dynamic', cascade='all, delete-orphan')
    )
    target_article = db.relationship(
        'Article', foreign_keys=[target_article_id],
        backref=db.backref('incoming_relationships', lazy='dynamic', cascade='all, delete-orphan')
    )
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    __table_args__ = (
        db.UniqueConstraint(
            'source_article_id', 'target_article_id', 'relationship_type',
            name='uq_article_relationship'
        ),
        db.Index('idx_rel_type', 'relationship_type'),
        db.Index('idx_rel_source_type', 'source_article_id', 'relationship_type'),
        db.Index('idx_rel_target_type', 'target_article_id', 'relationship_type'),
    )

    def __repr__(self):
        return (f'<ArticleRelationship {self.source_article_id} '
                f'--{self.relationship_type}--> {self.target_article_id}>')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.relationship_type and self.relationship_type not in self.VALID_TYPES:
            raise ValueError(
                f'Invalid relationship type "{self.relationship_type}". '
                f'Must be one of: {", ".join(self.VALID_TYPES)}'
            )

    @property
    def type_label(self):
        """Human-readable label for this relationship direction."""
        return self.TYPE_LABELS.get(self.relationship_type, self.relationship_type)

    @property
    def inverse_label(self):
        """Human-readable label for the reverse direction."""
        return self.INVERSE_LABELS.get(self.relationship_type, self.relationship_type)


class ArticleRevision(db.Model):
    """
    Version history entry for articles.
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
        return ArticleRevision.query.filter_by(
            article_id=self.article_id,
            parent_revision_id=self.id
        ).first()

    def get_previous_revision(self):
        return self.parent_revision

    def is_latest(self):
        return len(self.child_revisions) == 0

"""
API blueprint for JSON endpoints.
Provides search, article listing, and single article data.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, or_

from app import db
from app.models import Article, ArticleRelationship, Category

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/search', methods=['GET'])
def search():
    """
    JSON search results endpoint (for autocomplete and AJAX searches).
    Query parameter: ?q=search_term
    Optional: ?limit=20 (default 20)
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)

    results = []

    if query and len(query) >= 2:
        search_pattern = f'%{query}%'
        articles = Article.query.filter(
            Article.is_published == True,
            or_(
                Article.title.ilike(search_pattern),
                Article.slug.ilike(search_pattern),
                Article.summary.ilike(search_pattern)
            )
        ).order_by(
            Article.title
        ).limit(limit).all()

        results = [
            {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'summary': article.summary,
                'url': f'/wiki/{article.slug}',
                'category': article.category_name,
                'view_count': article.view_count,
                'created_at': article.created_at.isoformat()
            }
            for article in articles
        ]

    return jsonify({
        'query': query,
        'results': results,
        'total': len(results)
    })


@api_bp.route('/articles', methods=['GET'])
def articles():
    """
    List all published articles with pagination (JSON).
    Query parameters:
        ?page=1 (default 1)
        ?per_page=20 (default 20, max 100)
        ?category=slug (optional filter by category slug)
        ?sort=updated|created|views (default updated)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    category_slug = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'updated')

    query = Article.query.filter_by(is_published=True)

    # Filter by category (try FK first, then legacy string)
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
        else:
            query = query.filter_by(category=category_slug)

    # Sort
    if sort == 'created':
        query = query.order_by(desc(Article.created_at))
    elif sort == 'views':
        query = query.order_by(desc(Article.view_count))
    else:
        query = query.order_by(desc(Article.updated_at))

    pagination = query.paginate(page=page, per_page=per_page)

    articles_data = [
        {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'url': f'/wiki/{article.slug}',
            'category': article.category_name,
            'view_count': article.view_count,
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat(),
            'author': {
                'username': article.author.username,
                'url': f'/auth/profile/{article.author.username}'
            },
        }
        for article in pagination.items
    ]

    return jsonify({
        'articles': articles_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })


@api_bp.route('/article/<slug>', methods=['GET'])
def article(slug):
    """Get detailed data for a single article (JSON)."""
    article = Article.query.filter_by(slug=slug).first()

    if not article or not article.is_published:
        return jsonify({'error': 'Article not found'}), 404

    revision_count = article.revisions.count()
    discussion_count = article.discussions.count()

    article_data = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'summary': article.summary,
        'category': article.category_name,
        'view_count': article.view_count,
        'is_published': article.is_published,
        'is_protected': article.is_protected,
        'revision_count': revision_count,
        'discussion_count': discussion_count,
        'created_at': article.created_at.isoformat(),
        'updated_at': article.updated_at.isoformat(),
        'author': {
            'id': article.author.id,
            'username': article.author.username,
            'url': f'/auth/profile/{article.author.username}'
        },
        'urls': {
            'view': f'/wiki/{article.slug}',
            'edit': f'/wiki/{article.slug}/edit',
            'history': f'/wiki/{article.slug}/history',
            'talk': f'/wiki/{article.slug}/talk'
        }
    }

    return jsonify(article_data)


# ── Categories API ──

@api_bp.route('/categories', methods=['GET'])
def list_categories():
    """List all categories with nesting info."""
    cats = Category.query.order_by(Category.name).all()
    return jsonify({
        'categories': [
            {
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'description': c.description,
                'parent_id': c.parent_id,
                'article_count': c.articles.filter_by(is_published=True).count(),
            }
            for c in cats
        ]
    })


# ── Relationship CRUD ──

@api_bp.route('/article/<slug>/relationships', methods=['GET'])
def article_relationships(slug):
    """List all relationships for an article (both outgoing and incoming)."""
    article = Article.query.filter_by(slug=slug, is_published=True).first()
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    outgoing = ArticleRelationship.query.filter_by(source_article_id=article.id).all()
    incoming = ArticleRelationship.query.filter_by(target_article_id=article.id).all()

    def rel_dict(rel, direction):
        if direction == 'outgoing':
            other = rel.target_article
            label = rel.type_label
        else:
            other = rel.source_article
            label = rel.inverse_label
        return {
            'id': rel.id,
            'direction': direction,
            'relationship_type': rel.relationship_type,
            'label': label,
            'notes': rel.notes or '',
            'article': {
                'id': other.id,
                'title': other.title,
                'slug': other.slug,
                'category': other.category_name,
                'url': f'/wiki/{other.slug}',
            },
            'created_at': rel.created_at.isoformat() if rel.created_at else None,
        }

    relationships = (
        [rel_dict(r, 'outgoing') for r in outgoing] +
        [rel_dict(r, 'incoming') for r in incoming]
    )

    return jsonify({
        'article_id': article.id,
        'article_slug': article.slug,
        'relationships': relationships,
        'total': len(relationships),
    })


@api_bp.route('/relationships', methods=['POST'])
@login_required
def create_relationship():
    """Create a new relationship between two articles."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    source_slug = (data.get('source_slug') or '').strip()
    target_slug = (data.get('target_slug') or '').strip()
    rel_type = (data.get('relationship_type') or '').strip()
    notes = (data.get('notes') or '').strip() or None

    if not source_slug or not target_slug or not rel_type:
        return jsonify({'error': 'source_slug, target_slug, and relationship_type are required'}), 400

    if rel_type not in ArticleRelationship.VALID_TYPES:
        return jsonify({
            'error': f'Invalid relationship_type. Must be one of: {", ".join(ArticleRelationship.VALID_TYPES)}'
        }), 400

    source = Article.query.filter_by(slug=source_slug, is_published=True).first()
    target = Article.query.filter_by(slug=target_slug, is_published=True).first()

    if not source:
        return jsonify({'error': f'Source article "{source_slug}" not found'}), 404
    if not target:
        return jsonify({'error': f'Target article "{target_slug}" not found'}), 404
    if source.id == target.id:
        return jsonify({'error': 'Cannot create a relationship from an article to itself'}), 400

    existing = ArticleRelationship.query.filter_by(
        source_article_id=source.id,
        target_article_id=target.id,
        relationship_type=rel_type
    ).first()
    if existing:
        return jsonify({'error': 'This relationship already exists', 'id': existing.id}), 409

    rel = ArticleRelationship(
        source_article_id=source.id,
        target_article_id=target.id,
        relationship_type=rel_type,
        notes=notes,
        created_by_id=current_user.id,
    )
    db.session.add(rel)

    try:
        db.session.commit()
        return jsonify({
            'id': rel.id,
            'source_slug': source_slug,
            'target_slug': target_slug,
            'relationship_type': rel_type,
            'label': rel.type_label,
            'notes': notes,
            'message': 'Relationship created',
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/relationships/<int:rel_id>', methods=['DELETE'])
@login_required
def delete_relationship(rel_id):
    """Delete a relationship by ID."""
    rel = ArticleRelationship.query.get(rel_id)
    if not rel:
        return jsonify({'error': 'Relationship not found'}), 404

    db.session.delete(rel)
    try:
        db.session.commit()
        return jsonify({'message': 'Relationship deleted', 'id': rel_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ── Graph API ──

# Tier assignment based on subcategory/category slugs.
# Determines vertical position on the knowledge graph.
TIER_MAP = {
    # Subcategory slugs → tier
    'guard': 2, 'leg-entanglement': 2,
    'sweep': 2,
    'pass': 3,
    'dominant-position': 4,
    'submission': 5,
    'takedown': 1,
    'transitional': 3,
    'principle': -1,  # concepts float, resolved by relationships
    # Parent category slugs (fallback)
    'standing': 0,    # top-level Standing category = tier 0
    'position': 2,
    'technique': 2,
    'concept': -1,
    'person': -1,
    'competition': -1,
    'style': -1,
    'glossary': -1,
}

# Force vector classification for submission coloring
FORCE_VECTORS = {
    'arterial': [
        'rear-naked-choke', 'guillotine-choke', 'darce-choke', 'anaconda-choke',
        'triangle-choke', 'triangle-from-bottom', 'arm-triangle', 'north-south-choke',
        'ezekiel-choke', 'bow-and-arrow-choke', 'cross-collar-choke', 'loop-choke',
    ],
    'extension': [
        'armbar', 'kneebar', 'straight-ankle-lock',
    ],
    'torsion': [
        'kimura', 'americana', 'omoplata', 'heel-hook', 'toe-hold', 'wrist-lock',
    ],
    'compression': [
        'calf-slicer',
    ],
}

# Build reverse lookup: slug → force_vector
_SLUG_TO_VECTOR = {}
for vec, slugs in FORCE_VECTORS.items():
    for s in slugs:
        _SLUG_TO_VECTOR[s] = vec


def _get_article_tier(article):
    """Derive the graph tier for an article from its category hierarchy."""
    # Check subcategory slug first
    if article.category_ref:
        slug = article.category_ref.slug
        if slug in TIER_MAP:
            t = TIER_MAP[slug]
            if t >= 0:
                return t
        # Check parent category
        if article.category_ref.parent:
            parent_slug = article.category_ref.parent.slug
            if parent_slug in TIER_MAP:
                t = TIER_MAP[parent_slug]
                if t >= 0:
                    return t
    # Legacy string category
    if article.category and article.category in TIER_MAP:
        t = TIER_MAP[article.category]
        if t >= 0:
            return t
    # Special case: "standing" slug is always tier 0
    if article.slug == 'standing' or article.slug == 'standing-neutral':
        return 0
    return -1  # unplaceable


@api_bp.route('/graph', methods=['GET'])
def graph_data():
    """
    Full knowledge graph payload: all published articles with tier + all edges.
    Single request, designed to power the SVG visualization.
    """
    from sqlalchemy.orm import joinedload

    articles = Article.query.filter_by(is_published=True).options(
        joinedload(Article.category_ref).joinedload(Category.parent)
    ).all()

    rels = ArticleRelationship.query.options(
        joinedload(ArticleRelationship.source_article),
        joinedload(ArticleRelationship.target_article),
    ).all()

    nodes = []
    for a in articles:
        tier = _get_article_tier(a)
        cat_slug = a.category_ref.slug if a.category_ref else (a.category or '')
        parent_slug = ''
        if a.category_ref and a.category_ref.parent:
            parent_slug = a.category_ref.parent.slug

        node = {
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'summary': a.summary or '',
            'category': cat_slug,
            'parent_category': parent_slug,
            'tier': tier,
            'url': f'/wiki/{a.slug}',
        }
        # Add force vector for submissions
        if a.slug in _SLUG_TO_VECTOR:
            node['force_vector'] = _SLUG_TO_VECTOR[a.slug]

        nodes.append(node)

    edges = []
    published_ids = {a.id for a in articles}
    for r in rels:
        if r.source_article_id in published_ids and r.target_article_id in published_ids:
            edges.append({
                'source': r.source_article_id,
                'target': r.target_article_id,
                'type': r.relationship_type,
                'label': r.type_label,
            })

    return jsonify({
        'nodes': nodes,
        'edges': edges,
        'tiers': {
            0: 'Standing',
            1: 'Takedowns',
            2: 'Guards & Sweeps',
            3: 'Passes',
            4: 'Dominant Positions',
            5: 'Submissions',
        },
    })


@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

"""
API blueprint for JSON endpoints.
Provides search, article listing, and single article data.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import desc, or_

from app import db
from app.models import Article, Tag

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
    limit = min(limit, 100)  # Cap at 100 results

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
                'category': article.category,
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
        ?category=technique (optional filter)
        ?tag=slug (optional filter by tag)
        ?sort=updated|created|views (default updated)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Cap at 100
    category = request.args.get('category', '').strip()
    tag_slug = request.args.get('tag', '').strip()
    sort = request.args.get('sort', 'updated')

    # Build query
    query = Article.query.filter_by(is_published=True)

    # Filter by category
    if category and category in Article.VALID_CATEGORIES:
        query = query.filter_by(category=category)

    # Filter by tag
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first()
        if tag:
            query = query.filter(Article.tags.contains(tag))

    # Sort
    if sort == 'created':
        query = query.order_by(desc(Article.created_at))
    elif sort == 'views':
        query = query.order_by(desc(Article.view_count))
    else:  # default: updated
        query = query.order_by(desc(Article.updated_at))

    pagination = query.paginate(page=page, per_page=per_page)

    articles_data = [
        {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'url': f'/wiki/{article.slug}',
            'category': article.category,
            'view_count': article.view_count,
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat(),
            'author': {
                'username': article.author.username,
                'url': f'/auth/profile/{article.author.username}'
            },
            'tags': [
                {'name': tag.name, 'slug': tag.slug}
                for tag in article.tags
            ]
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
    """
    Get detailed data for a single article (JSON).
    """
    article = Article.query.filter_by(slug=slug).first()

    if not article or not article.is_published:
        return jsonify({
            'error': 'Article not found'
        }), 404

    # Get revision count
    revision_count = article.revisions.count()

    # Get discussion count
    discussion_count = article.discussions.count()

    article_data = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'summary': article.summary,
        'category': article.category,
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
        'tags': [
            {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug,
                'url': f'/category/{tag.slug}'
            }
            for tag in article.tags
        ],
        'urls': {
            'view': f'/wiki/{article.slug}',
            'edit': f'/wiki/{article.slug}/edit',
            'history': f'/wiki/{article.slug}/history',
            'talk': f'/wiki/{article.slug}/talk'
        }
    }

    return jsonify(article_data)


@api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({
        'error': 'Bad request',
        'message': str(error)
    }), 400


@api_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({
        'error': 'Not found',
        'message': str(error)
    }), 404


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

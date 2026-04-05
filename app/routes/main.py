"""
Main blueprint for wiki routes.
Handles homepage, search, categories, recent changes, and sitemaps.
"""

from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import desc, or_
from app import db
from app.models import Article, Tag, ArticleRevision, User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Homepage showing featured articles, recent changes, and random article link.
    """
    # Get featured/popular articles (most viewed)
    featured_articles = Article.query.filter_by(
        is_published=True
    ).order_by(desc(Article.view_count)).limit(5).all()

    # Get recent changes
    recent_revisions = ArticleRevision.query.order_by(
        desc(ArticleRevision.created_at)
    ).limit(10).all()

    # Get total stats
    total_articles = Article.query.filter_by(is_published=True).count()
    total_users = User.query.count()
    total_edits = ArticleRevision.query.count()

    return render_template(
        'index.html',
        featured_articles=featured_articles,
        recent_revisions=recent_revisions,
        total_articles=total_articles,
        total_users=total_users,
        total_edits=total_edits
    )


@main_bp.route('/search')
def search():
    """
    Full-text search across articles.
    GET parameter: ?q=search_query
    """
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    results = []
    if query and len(query) >= 2:
        # Search in title, slug, summary, and content
        search_pattern = f'%{query}%'
        results = Article.query.filter(
            Article.is_published == True,
            or_(
                Article.title.ilike(search_pattern),
                Article.slug.ilike(search_pattern),
                Article.summary.ilike(search_pattern),
                Article.content.ilike(search_pattern)
            )
        ).order_by(desc(Article.updated_at)).paginate(page=page, per_page=per_page)
    else:
        results = Article.query.filter_by(is_published=True).paginate(
            page=page, per_page=per_page
        )

    return render_template(
        'search.html',
        query=query,
        results=results,
        page=page
    )


@main_bp.route('/categories')
def categories():
    """
    List all categories/tags.
    """
    tags = Tag.query.order_by(Tag.name).all()

    # Get article counts per tag
    tag_data = []
    for tag in tags:
        count = tag.articles.filter_by(is_published=True).count()
        tag_data.append({
            'tag': tag,
            'count': count
        })

    return render_template('categories.html', tag_data=tag_data)


@main_bp.route('/category/<name>')
def category(name):
    """
    Show articles in a specific category.
    """
    tag = Tag.query.filter_by(slug=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    articles = tag.articles.filter_by(is_published=True).order_by(
        desc(Article.updated_at)
    ).paginate(page=page, per_page=per_page)

    return render_template(
        'category.html',
        tag=tag,
        articles=articles,
        page=page
    )


@main_bp.route('/recent-changes')
def recent_changes():
    """
    Paginated list of recent edits across all articles.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 50

    revisions = ArticleRevision.query.order_by(
        desc(ArticleRevision.created_at)
    ).paginate(page=page, per_page=per_page)

    return render_template(
        'recent_changes.html',
        revisions=revisions,
        page=page
    )


@main_bp.route('/random')
def random_article():
    """
    Redirect to a random published article.
    """
    from flask import redirect
    import random

    articles = Article.query.filter_by(is_published=True).all()
    if not articles:
        return redirect('/')

    article = random.choice(articles)
    return redirect(f'/wiki/{article.slug}')


@main_bp.route('/sitemap.xml')
def sitemap():
    """
    Generate XML sitemap for SEO.
    """
    from datetime import datetime

    articles = Article.query.filter_by(is_published=True).all()

    sitemap_entries = []

    # Add homepage
    sitemap_entries.append({
        'url': '/',
        'lastmod': datetime.utcnow().isoformat(),
        'priority': '1.0'
    })

    # Add static pages
    static_routes = ['/search', '/categories', '/recent-changes']
    for route in static_routes:
        sitemap_entries.append({
            'url': route,
            'lastmod': datetime.utcnow().isoformat(),
            'priority': '0.8'
        })

    # Add all articles
    for article in articles:
        sitemap_entries.append({
            'url': f'/wiki/{article.slug}',
            'lastmod': article.updated_at.isoformat(),
            'priority': '0.9'
        })

    return render_template('sitemap.xml', entries=sitemap_entries), 200, {
        'Content-Type': 'application/xml'
    }

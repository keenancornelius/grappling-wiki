"""
Main blueprint for wiki routes.
Handles homepage, search, categories, recent changes, sitemaps, and roadmap.
"""

from flask import Blueprint, render_template, request, jsonify, redirect
from sqlalchemy import desc, or_, func
import random
import re
import os
from app import db
from app.models import Article, Category, ArticleRelationship, ArticleRevision, User

main_bp = Blueprint('main', __name__)


def _parse_kanban_from_claude_md():
    """
    Parse CLAUDE.md task streams into kanban board data.
    Returns a list of board columns with categorized tasks.
    """
    claude_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'CLAUDE.md')
    try:
        with open(claude_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return [], {}

    stream_pattern = re.compile(
        r'### (Stream [A-Z](?:\.\d+)?) — (.+?)\n'
        r'\*\*Status:\*\* (.+?)\n'
        r'\*\*Owner:\*\* (.+?)\n',
        re.MULTILINE
    )

    sub_stream_pattern = re.compile(
        r'#### ([A-Z]\.\d+) — (.+?)\n',
        re.MULTILINE
    )

    task_pattern = re.compile(r'^- \[([ x])\] (.+)$', re.MULTILINE)

    stream_sections = re.split(r'(?=### Stream [A-Z])', content)

    streams = []
    all_tasks = []
    stats = {'total': 0, 'done': 0, 'in_progress': 0, 'todo': 0}

    category_map = {
        'A': 'Infrastructure',
        'B': 'Infrastructure',
        'C': 'Development',
        'D': 'Design & UX',
        'E': 'SEO & Performance',
        'F': 'Content & Research',
        'G': 'Community & Launch',
    }

    columns = {
        'Infrastructure': {'id': 'infrastructure', 'label': 'Infrastructure', 'icon': 'server', 'tasks': [], 'color': '#1B8A6B'},
        'Development': {'id': 'development', 'label': 'Development', 'icon': 'code', 'tasks': [], 'color': '#22c55e'},
        'Design & UX': {'id': 'design', 'label': 'Design & UX', 'icon': 'palette', 'tasks': [], 'color': '#a855f7'},
        'SEO & Performance': {'id': 'seo', 'label': 'SEO & Performance', 'icon': 'zap', 'tasks': [], 'color': '#eab308'},
        'Content & Research': {'id': 'content', 'label': 'Content & Research', 'icon': 'book', 'tasks': [], 'color': '#f97316'},
        'Community & Launch': {'id': 'community', 'label': 'Community & Launch', 'icon': 'users', 'tasks': [], 'color': '#ec4899'},
    }

    for section in stream_sections:
        stream_match = stream_pattern.search(section)
        if not stream_match:
            continue

        stream_id = stream_match.group(1)
        stream_title = stream_match.group(2).strip()
        stream_status_raw = stream_match.group(3).strip()
        stream_owner = stream_match.group(4).strip()

        stream_letter = stream_id.replace('Stream ', '')[0]
        category = category_map.get(stream_letter, 'Development')

        if '✅' in stream_status_raw and '🔧' in stream_status_raw:
            stream_status = 'in_progress'
        elif '✅' in stream_status_raw:
            stream_status = 'done'
        elif '📋' in stream_status_raw:
            stream_status = 'planning'
        else:
            stream_status = 'todo'

        sub_streams = sub_stream_pattern.findall(section)
        sub_stream_names = {ss[0]: ss[1].strip() for ss in sub_streams}

        sub_sections = re.split(r'(?=#### [A-Z]\.\d+)', section)

        for sub_section in sub_sections:
            sub_match = re.search(r'#### ([A-Z]\.\d+) — (.+)', sub_section)
            sub_label = sub_match.group(2).strip() if sub_match else None
            sub_id = sub_match.group(1) if sub_match else None

            sub_tasks = task_pattern.findall(sub_section)
            for is_done_char, task_text in sub_tasks:
                is_done = is_done_char == 'x'
                task_status = 'done' if is_done else 'todo'

                if not is_done and stream_status == 'in_progress':
                    display_status = 'active'
                elif not is_done and stream_status == 'planning':
                    display_status = 'planned'
                else:
                    display_status = task_status

                task_obj = {
                    'text': task_text.strip(),
                    'done': is_done,
                    'status': display_status,
                    'stream': stream_id,
                    'stream_title': stream_title,
                    'stream_letter': stream_letter,
                    'sub_stream': sub_label or stream_title,
                    'sub_id': sub_id or stream_id,
                    'owner': stream_owner,
                }

                columns[category]['tasks'].append(task_obj)
                all_tasks.append(task_obj)

                stats['total'] += 1
                if is_done:
                    stats['done'] += 1
                elif stream_status in ('in_progress',):
                    stats['in_progress'] += 1
                else:
                    stats['todo'] += 1

    stats['progress_pct'] = round((stats['done'] / stats['total'] * 100) if stats['total'] > 0 else 0)

    column_list = []
    for key in ['Infrastructure', 'Development', 'Design & UX', 'SEO & Performance', 'Content & Research', 'Community & Launch']:
        col = columns[key]
        col['total'] = len(col['tasks'])
        col['done_count'] = sum(1 for t in col['tasks'] if t['done'])
        col['progress_pct'] = round((col['done_count'] / col['total'] * 100) if col['total'] > 0 else 0)
        column_list.append(col)

    return column_list, stats


@main_bp.route('/')
def index():
    """
    Homepage — a discovery engine for grappling knowledge.
    Surfaces articles, relationships, categories, and recent activity
    in an information-rich layout designed for exploration.
    """
    # ── Core stats ──
    total_articles = Article.query.filter_by(is_published=True).count()
    total_users = User.query.count()
    total_edits = ArticleRevision.query.count()
    total_relationships = ArticleRelationship.query.count()

    # ── Categories with article counts ──
    categories = []
    for cat in Category.query.order_by(Category.name).all():
        count = cat.articles.filter_by(is_published=True).count()
        if count > 0:
            categories.append({
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description or '',
                'article_count': count,
            })
    # Sort by count descending so the biggest categories are first
    categories.sort(key=lambda c: c['article_count'], reverse=True)

    # ── Featured: most-viewed articles ──
    featured_articles = Article.query.filter_by(
        is_published=True
    ).order_by(desc(Article.view_count)).limit(6).all()

    # ── Most connected articles (by total relationship count) ──
    # Subquery: count outgoing + incoming relationships per article
    outgoing_count = db.session.query(
        ArticleRelationship.source_article_id.label('article_id'),
        func.count().label('cnt')
    ).group_by(ArticleRelationship.source_article_id).subquery()

    incoming_count = db.session.query(
        ArticleRelationship.target_article_id.label('article_id'),
        func.count().label('cnt')
    ).group_by(ArticleRelationship.target_article_id).subquery()

    # Get articles with most connections (outgoing only for simplicity, then combine)
    connected_articles = []
    if total_relationships > 0:
        # Simple approach: get all published articles and count their relationships in Python
        all_published = Article.query.filter_by(is_published=True).all()
        article_connections = []
        for a in all_published:
            out_count = a.outgoing_relationships.count()
            in_count = a.incoming_relationships.count()
            total = out_count + in_count
            if total > 0:
                article_connections.append((a, total))
        article_connections.sort(key=lambda x: x[1], reverse=True)
        connected_articles = article_connections[:8]

    # ── Interesting relationship pairs (for "How things connect" section) ──
    relationship_highlights = []
    if total_relationships > 0:
        rels = ArticleRelationship.query.limit(12).all()
        for rel in rels:
            if rel.source_article and rel.target_article:
                if rel.source_article.is_published and rel.target_article.is_published:
                    relationship_highlights.append({
                        'source': rel.source_article,
                        'target': rel.target_article,
                        'type': rel.relationship_type,
                        'label': rel.type_label,
                    })
            if len(relationship_highlights) >= 8:
                break

    # ── Recent edits (for activity ticker) ──
    recent_edits = db.session.query(ArticleRevision, Article).join(
        Article, ArticleRevision.article_id == Article.id
    ).filter(
        Article.is_published == True
    ).order_by(desc(ArticleRevision.created_at)).limit(10).all()

    # ── Recently added articles ──
    recent_articles = Article.query.filter_by(
        is_published=True
    ).order_by(desc(Article.created_at)).limit(8).all()

    # ── Random discovery: 3 random articles ──
    random_articles = Article.query.filter_by(is_published=True).all()
    if len(random_articles) > 3:
        random_articles = random.sample(random_articles, 3)
    else:
        random_articles = random_articles[:3]

    # ── Articles per category (for the visual breakdown) ──
    category_breakdown = []
    for cat in categories:
        if cat['article_count'] > 0:
            category_breakdown.append(cat)

    return render_template(
        'index.html',
        total_articles=total_articles,
        total_users=total_users,
        total_edits=total_edits,
        total_relationships=total_relationships,
        categories=categories,
        featured_articles=featured_articles,
        connected_articles=connected_articles,
        relationship_highlights=relationship_highlights,
        recent_edits=recent_edits,
        recent_articles=recent_articles,
        random_articles=random_articles,
    )


@main_bp.route('/search')
def search():
    """Full-text search across articles."""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    if query and len(query) >= 2:
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
    Browse all articles grouped by category.
    Uses the Category model with nesting support.
    Falls back to legacy string categories for unmigrated articles.
    """
    all_articles = Article.query.filter_by(is_published=True).order_by(Article.title).all()

    all_cats = Category.query.order_by(Category.name).all()

    cat_map = {cat.id: {
        'model': cat,
        'label': cat.name,
        'description': cat.description or '',
        'slug': cat.slug,
        'key': cat.slug,
        'depth': cat.depth,
        'parent_id': cat.parent_id,
        'articles': [],
    } for cat in all_cats}

    legacy_groups = {}

    for a in all_articles:
        if a.category_id and a.category_id in cat_map:
            cat_map[a.category_id]['articles'].append(a)
        elif a.category:
            key = a.category
            if key not in legacy_groups:
                legacy_groups[key] = {
                    'label': key.title(),
                    'description': '',
                    'slug': key,
                    'key': key,
                    'depth': 0,
                    'articles': [],
                }
            legacy_groups[key]['articles'].append(a)

    category_list = []
    for cat in all_cats:
        if cat.parent_id is None:
            entry = cat_map[cat.id]
            entry['children'] = []
            for child in cat.children.order_by(Category.name).all():
                child_entry = cat_map[child.id]
                entry['children'].append(child_entry)
            category_list.append(entry)

    existing_slugs = {c['slug'] for c in category_list}
    for key, group in sorted(legacy_groups.items()):
        if key not in existing_slugs:
            group['children'] = []
            category_list.append(group)

    total_articles = len(all_articles)

    return render_template(
        'categories.html',
        category_list=category_list,
        total_articles=total_articles,
    )


@main_bp.route('/recent-changes')
def recent_changes():
    """Paginated list of recent edits across all articles."""
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
    """Redirect to a random published article."""
    articles = Article.query.filter_by(is_published=True).all()
    if not articles:
        return redirect('/')
    article = random.choice(articles)
    return redirect(f'/wiki/{article.slug}')


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO."""
    from datetime import datetime

    articles = Article.query.filter_by(is_published=True).all()

    sitemap_entries = []

    sitemap_entries.append({
        'url': '/',
        'lastmod': datetime.utcnow().isoformat(),
        'priority': '1.0'
    })

    static_routes = ['/search', '/categories', '/recent-changes']
    for route in static_routes:
        sitemap_entries.append({
            'url': route,
            'lastmod': datetime.utcnow().isoformat(),
            'priority': '0.8'
        })

    for article in articles:
        sitemap_entries.append({
            'url': f'/wiki/{article.slug}',
            'lastmod': article.updated_at.isoformat(),
            'priority': '0.9'
        })

    return render_template('sitemap.xml', entries=sitemap_entries), 200, {
        'Content-Type': 'application/xml'
    }


@main_bp.route('/explore')
def explore():
    """Knowledge graph placeholder — being rebuilt with relationship system."""
    return render_template('explore.html')


@main_bp.route('/graph/editor')
def graph_editor():
    """Graph editor placeholder — being rebuilt."""
    return render_template('graph_editor.html')


@main_bp.route('/roadmap')
def roadmap():
    """Public kanban board showing project progress."""
    columns, stats = _parse_kanban_from_claude_md()
    return render_template(
        'roadmap.html',
        columns=columns,
        stats=stats
    )

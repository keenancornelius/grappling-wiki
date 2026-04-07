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

    # ── Categories with article counts (single query) ──
    cat_counts = db.session.query(
        Category.id, Category.name, Category.slug, Category.description,
        func.count(Article.id).label('cnt')
    ).outerjoin(Article, (Article.category_id == Category.id) & (Article.is_published == True)
    ).group_by(Category.id).having(func.count(Article.id) > 0
    ).order_by(func.count(Article.id).desc()).all()

    categories = [{
        'name': row.name, 'slug': row.slug,
        'description': row.description or '', 'article_count': row.cnt,
    } for row in cat_counts]

    # ── Featured: most-viewed articles ──
    featured_articles = Article.query.filter_by(
        is_published=True
    ).order_by(desc(Article.view_count)).limit(6).all()

    # ── Most connected articles (single SQL query with UNION) ──
    connected_articles = []
    if total_relationships > 0:
        # Union outgoing + incoming, count per article, join back to Article
        out_q = db.session.query(
            ArticleRelationship.source_article_id.label('aid')
        )
        in_q = db.session.query(
            ArticleRelationship.target_article_id.label('aid')
        )
        all_edges = out_q.union_all(in_q).subquery()
        top_connected_q = db.session.query(
            all_edges.c.aid, func.count().label('cnt')
        ).group_by(all_edges.c.aid).order_by(func.count().desc()).limit(8).subquery()

        rows = db.session.query(Article, top_connected_q.c.cnt).join(
            top_connected_q, Article.id == top_connected_q.c.aid
        ).filter(Article.is_published == True).order_by(top_connected_q.c.cnt.desc()).all()
        connected_articles = [(a, cnt) for a, cnt in rows]

    # ── Interesting relationship pairs (eager-load both articles in one query) ──
    relationship_highlights = []
    if total_relationships > 0:
        from sqlalchemy.orm import joinedload
        rels = ArticleRelationship.query.options(
            joinedload(ArticleRelationship.source_article),
            joinedload(ArticleRelationship.target_article),
        ).limit(12).all()
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

    # ── Random discovery: 3 random articles (DB-level random, not loading all) ──
    random_articles = Article.query.filter_by(
        is_published=True
    ).order_by(func.random()).limit(3).all()

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
    # Load all categories eagerly with children in 2 queries (not N+1)
    from sqlalchemy.orm import subqueryload
    all_cats = Category.query.options(
        subqueryload(Category.children)
    ).order_by(Category.name).all()

    # Build cat_map
    cat_map = {}
    for cat in all_cats:
        cat_map[cat.id] = {
            'model': cat,
            'label': cat.name,
            'description': cat.description or '',
            'slug': cat.slug,
            'key': cat.slug,
            'depth': cat.depth,
            'parent_id': cat.parent_id,
            'articles': [],
        }

    # Load articles with their category in one query
    all_articles = Article.query.filter_by(is_published=True).order_by(Article.title).all()
    legacy_groups = {}

    for a in all_articles:
        if a.category_id and a.category_id in cat_map:
            cat_map[a.category_id]['articles'].append(a)
        elif a.category:
            key = a.category
            if key not in legacy_groups:
                legacy_groups[key] = {
                    'label': key.title(), 'description': '', 'slug': key,
                    'key': key, 'depth': 0, 'articles': [],
                }
            legacy_groups[key]['articles'].append(a)

    # Build hierarchy using pre-loaded children (no extra queries)
    category_list = []
    for cat in all_cats:
        if cat.parent_id is None:
            entry = cat_map[cat.id]
            entry['children'] = []
            for child in sorted(cat.children.all(), key=lambda c: c.name):
                if child.id in cat_map:
                    entry['children'].append(cat_map[child.id])
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
    article = Article.query.filter_by(is_published=True).order_by(func.random()).first()
    if not article:
        return redirect('/')
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
    """
    Explore page — browse the entire wiki by relationships and categories.
    Shows articles organized by category with connection counts,
    filterable and sortable for discovery.
    """
    # Query params
    filter_category = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'connections')  # connections, views, recent, title
    page = request.args.get('page', 1, type=int)
    per_page = 30

    # Base query: published articles
    query = Article.query.filter_by(is_published=True)

    # Filter by category
    active_category = None
    if filter_category:
        cat = Category.query.filter_by(slug=filter_category).first()
        if cat:
            active_category = cat
            query = query.filter_by(category_id=cat.id)

    # ── Build connection counts via SQL subquery ──
    out_q = db.session.query(
        ArticleRelationship.source_article_id.label('aid')
    )
    in_q = db.session.query(
        ArticleRelationship.target_article_id.label('aid')
    )
    all_edges = out_q.union_all(in_q).subquery()
    conn_counts = db.session.query(
        all_edges.c.aid, func.count().label('cnt')
    ).group_by(all_edges.c.aid).subquery()

    # Join articles with their connection count
    base_q = db.session.query(
        Article, func.coalesce(conn_counts.c.cnt, 0).label('connection_count')
    ).outerjoin(conn_counts, Article.id == conn_counts.c.aid
    ).filter(Article.is_published == True)

    if active_category:
        base_q = base_q.filter(Article.category_id == active_category.id)

    if sort_by == 'connections':
        base_q = base_q.order_by(func.coalesce(conn_counts.c.cnt, 0).desc())
    elif sort_by == 'views':
        base_q = base_q.order_by(desc(Article.view_count))
    elif sort_by == 'recent':
        base_q = base_q.order_by(desc(Article.updated_at))
    elif sort_by == 'title':
        base_q = base_q.order_by(Article.title)
    else:
        base_q = base_q.order_by(desc(Article.view_count))

    # Paginate
    total = base_q.count()
    total_pages = (total + per_page - 1) // per_page
    rows = base_q.offset((page - 1) * per_page).limit(per_page).all()

    articles_with_counts = [{'article': a, 'connection_count': cnt} for a, cnt in rows]
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
    }

    # Categories for filter sidebar (single query)
    cat_count_rows = db.session.query(
        Category, func.count(Article.id).label('cnt')
    ).outerjoin(Article, (Article.category_id == Category.id) & (Article.is_published == True)
    ).group_by(Category.id).having(func.count(Article.id) > 0
    ).order_by(func.count(Article.id).desc()).all()
    category_counts = [{'category': cat, 'count': cnt} for cat, cnt in cat_count_rows]

    # Overall stats
    total_articles = Article.query.filter_by(is_published=True).count()
    total_relationships = ArticleRelationship.query.count()
    total_categories = len(category_counts)

    # Most connected articles (top 5, single query using the same subquery pattern)
    top_rows = db.session.query(
        Article, func.coalesce(conn_counts.c.cnt, 0).label('tc')
    ).outerjoin(conn_counts, Article.id == conn_counts.c.aid
    ).filter(Article.is_published == True
    ).order_by(func.coalesce(conn_counts.c.cnt, 0).desc()).limit(5).all()
    top_connected = [{'article': a, 'count': tc} for a, tc in top_rows if tc > 0]

    return render_template(
        'explore.html',
        articles_with_counts=articles_with_counts,
        pagination=pagination_info,
        category_counts=category_counts,
        active_category=active_category,
        sort_by=sort_by,
        filter_category=filter_category,
        total_articles=total_articles,
        total_relationships=total_relationships,
        total_categories=total_categories,
        top_connected=top_connected,
    )


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

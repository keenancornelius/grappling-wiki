"""
Main blueprint for wiki routes.
Handles homepage, search, categories, recent changes, sitemaps, and roadmap.
"""

from flask import Blueprint, render_template, request, jsonify, redirect
from sqlalchemy import desc, or_
import random
import re
import os
from app import db
from app.models import Article, Tag, ArticleRevision, User

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

    # Parse streams: find ### Stream X — Title sections
    stream_pattern = re.compile(
        r'### (Stream [A-Z](?:\.\d+)?) — (.+?)\n'
        r'\*\*Status:\*\* (.+?)\n'
        r'\*\*Owner:\*\* (.+?)\n',
        re.MULTILINE
    )

    # Parse sub-streams like #### D.1 — Animation System
    sub_stream_pattern = re.compile(
        r'#### ([A-Z]\.\d+) — (.+?)\n',
        re.MULTILINE
    )

    # Parse tasks: lines starting with - [ ] or - [x]
    task_pattern = re.compile(r'^- \[([ x])\] (.+)$', re.MULTILINE)

    # Split content into stream sections
    stream_sections = re.split(r'(?=### Stream [A-Z])', content)

    streams = []
    all_tasks = []
    stats = {'total': 0, 'done': 0, 'in_progress': 0, 'todo': 0}

    # Smart category mapping
    category_map = {
        'A': 'Infrastructure',
        'B': 'Infrastructure',
        'C': 'Development',
        'D': 'Design & UX',
        'E': 'SEO & Performance',
        'F': 'Content & Research',
        'G': 'Community & Launch',
    }

    # Kanban columns
    columns = {
        'Infrastructure': {'id': 'infrastructure', 'label': 'Infrastructure', 'icon': 'server', 'tasks': [], 'color': '#4a9eff'},
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

        # Get stream letter
        stream_letter = stream_id.replace('Stream ', '')[0]
        category = category_map.get(stream_letter, 'Development')

        # Parse status
        if '✅' in stream_status_raw and '🔧' in stream_status_raw:
            stream_status = 'in_progress'
        elif '✅' in stream_status_raw:
            stream_status = 'done'
        elif '📋' in stream_status_raw:
            stream_status = 'planning'
        else:
            stream_status = 'todo'

        # Find sub-streams within this section
        sub_streams = sub_stream_pattern.findall(section)
        sub_stream_names = {ss[0]: ss[1].strip() for ss in sub_streams}

        # Find all tasks in section
        tasks_in_section = task_pattern.findall(section)

        # Group tasks by sub-stream if applicable
        # Split by #### headers to assign tasks to sub-streams
        sub_sections = re.split(r'(?=#### [A-Z]\.\d+)', section)

        for sub_section in sub_sections:
            sub_match = re.search(r'#### ([A-Z]\.\d+) — (.+)', sub_section)
            sub_label = sub_match.group(2).strip() if sub_match else None
            sub_id = sub_match.group(1) if sub_match else None

            sub_tasks = task_pattern.findall(sub_section)
            for is_done_char, task_text in sub_tasks:
                is_done = is_done_char == 'x'
                task_status = 'done' if is_done else 'todo'

                # Determine if task is in-progress based on stream status
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

    # Build column list (preserve order)
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
    Homepage showing featured articles, recent changes, and stats.
    """
    # Get featured/popular articles (most viewed)
    featured_articles = Article.query.filter_by(
        is_published=True
    ).order_by(desc(Article.view_count)).limit(5).all()

    # Get recent articles
    recent_articles = Article.query.filter_by(
        is_published=True
    ).order_by(desc(Article.updated_at)).limit(4).all()

    # Get total stats
    total_articles = Article.query.filter_by(is_published=True).count()
    total_users = User.query.count()
    total_edits = ArticleRevision.query.count()

    # Get categories (tags with article counts)
    tags = Tag.query.order_by(Tag.name).all()
    categories = []
    for tag in tags:
        count = tag.articles.filter_by(is_published=True).count()
        categories.append({
            'name': tag.name,
            'slug': tag.slug,
            'article_count': count
        })

    # Trending edits (recent revisions for the ticker)
    recent_edits = db.session.query(ArticleRevision, Article).join(
        Article, ArticleRevision.article_id == Article.id
    ).filter(
        Article.is_published == True
    ).order_by(desc(ArticleRevision.created_at)).limit(10).all()

    # Article data for knowledge graph
    all_articles = Article.query.filter_by(is_published=True).all()
    graph_articles = [
        {'id': a.id, 'title': a.title, 'slug': a.slug,
         'summary': a.summary or '', 'category': a.category or '',
         'tags': [t.name for t in a.tags]}
        for a in all_articles
    ]

    return render_template(
        'index.html',
        featured_articles=featured_articles,
        recent_articles=recent_articles,
        total_articles=total_articles,
        total_users=total_users,
        total_edits=total_edits,
        categories=categories,
        recent_edits=recent_edits,
        graph_articles=graph_articles
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

    total_categories = len(tag_data)
    total_articles = Article.query.filter_by(is_published=True).count()
    avg_articles = round(total_articles / total_categories) if total_categories > 0 else 0

    return render_template(
        'categories.html',
        tag_data=tag_data,
        total_categories=total_categories,
        total_articles=total_articles,
        avg_articles=avg_articles
    )


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


@main_bp.route('/explore')
def explore():
    """
    Interactive neural knowledge graph visualization.
    Shows all articles as nodes in a point cloud with connections.
    """
    articles = Article.query.filter_by(is_published=True).all()
    article_data = []
    for a in articles:
        article_data.append({
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'summary': a.summary or '',
            'category': a.category or '',
            'tags': [t.name for t in a.tags],
        })
    return render_template('explore.html', article_data=article_data)


@main_bp.route('/graph/editor')
def graph_editor():
    """
    Graph editor — interactive tool for arranging nodes,
    editing labels, building connections, and saving state.
    """
    articles = Article.query.filter_by(is_published=True).all()
    article_data = []
    for a in articles:
        article_data.append({
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'summary': a.summary or '',
            'category': a.category or '',
            'tags': [t.name for t in a.tags],
        })
    return render_template('graph_editor.html', article_data=article_data)


@main_bp.route('/roadmap')
def roadmap():
    """
    Public kanban board showing project progress.
    Parses CLAUDE.md task streams in real-time.
    """
    columns, stats = _parse_kanban_from_claude_md()
    return render_template(
        'roadmap.html',
        columns=columns,
        stats=stats
    )

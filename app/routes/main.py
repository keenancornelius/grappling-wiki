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
         'tags': [t.name for t in a.tags],
         'mechanism': a.mechanism or '', 'target': a.target or '',
         'spatial': a.spatial_qualifier or '',
         'graphTier': a.graph_tier or ''}
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
    Hierarchical categories page.
    Organises articles by their graph_tier into the positional tree:
    Standing → Takedowns → Guards → Dominant Positions → Submissions.
    Uses the English-from-Japanese taxonomy convention for display.
    """
    # ── Tier definitions: ordered top-down matching the inverse tree ──
    # Each tier has a display label, the sys_ node IDs it maps to,
    # a colour from the design system, and a description.
    TIER_TREE = [
        {
            'id': 'standing',
            'label': 'Standing Neutral',
            'japanese': 'Tachi-waza',
            'description': 'Both players on feet — maximum optionality, the root of all grappling.',
            'color': 'var(--accent)',
            'sys_nodes': ['sys_standing'],
            'subcategories': None,
        },
        {
            'id': 'takedowns',
            'label': 'Takedowns',
            'japanese': 'Nage-waza / Shoot',
            'description': 'Actions that bring the fight to the ground.',
            'color': 'var(--accent)',
            'sys_nodes': ['sys_upper_td', 'sys_lower_td'],
            'subcategories': [
                {
                    'id': 'upper_td',
                    'label': 'Upper Body',
                    'japanese': 'Nage-waza',
                    'description': 'Throws, trips, and clinch-initiated takedowns attacking above the waist.',
                    'sys_nodes': ['sys_upper_td'],
                },
                {
                    'id': 'lower_td',
                    'label': 'Lower Body',
                    'japanese': 'Shots',
                    'description': 'Double leg, single leg, ankle picks — attacking below the waist.',
                    'sys_nodes': ['sys_lower_td'],
                },
            ],
        },
        {
            'id': 'guards',
            'label': 'Guards',
            'japanese': 'Ne-waza (Shita)',
            'description': 'Bottom positions — sorted close to far (leg reconnection spectrum).',
            'color': 'rgb(160, 140, 220)',
            'sys_nodes': ['sys_close_guard', 'sys_mid_guard', 'sys_leg_entangle', 'sys_far_guard', 'sys_front_headlock'],
            'subcategories': [
                {
                    'id': 'close_guard',
                    'label': 'Close Guard',
                    'japanese': 'Kumi-kata (closed)',
                    'description': 'Closed guard, rubber guard — legs locked around opponent.',
                    'sys_nodes': ['sys_close_guard'],
                },
                {
                    'id': 'mid_guard',
                    'label': 'Mid Distance Guard',
                    'japanese': 'Hantai-ashi',
                    'description': 'Half guard, butterfly, Z-guard, knee shield — one leg controlling.',
                    'sys_nodes': ['sys_mid_guard'],
                },
                {
                    'id': 'leg_entangle',
                    'label': 'Leg Entanglements',
                    'japanese': 'Ashi-garami',
                    'description': 'Ashi garami, 50/50, saddle — symmetrical leg control, gateway to leg locks.',
                    'sys_nodes': ['sys_leg_entangle'],
                },
                {
                    'id': 'far_guard',
                    'label': 'Far Distance Guard',
                    'japanese': 'Hikikomigaeshi',
                    'description': 'De La Riva, spider, lasso, X-guard — feet framing on opponent.',
                    'sys_nodes': ['sys_far_guard'],
                },
                {
                    'id': 'front_headlock',
                    'label': 'Front Headlock',
                    'japanese': 'Mae-hadaka-jime kumi-kata',
                    'description': 'Face-to-back control — guilotines, darces, anacondas, neckties.',
                    'sys_nodes': ['sys_front_headlock'],
                },
            ],
        },
        {
            'id': 'dominant',
            'label': 'Dominant Positions',
            'japanese': 'Osae-komi-waza',
            'description': 'Top positions — guard has been passed, top player controls.',
            'color': 'rgb(120, 210, 190)',
            'sys_nodes': ['sys_side_control', 'sys_mount', 'sys_kob', 'sys_back_control'],
            'subcategories': [
                {
                    'id': 'side_control',
                    'label': 'Side Control',
                    'japanese': 'Yoko-shiho-gatame',
                    'description': 'Side control, north-south, 100 kilos.',
                    'sys_nodes': ['sys_side_control'],
                },
                {
                    'id': 'knee_on_belly',
                    'label': 'Knee on Belly',
                    'japanese': 'Tate-shiho (transitional)',
                    'description': 'Knee on belly, knee on chest.',
                    'sys_nodes': ['sys_kob'],
                },
                {
                    'id': 'mount',
                    'label': 'Mount',
                    'japanese': 'Tate-shiho-gatame',
                    'description': 'Mount, S-mount, mounted crucifix.',
                    'sys_nodes': ['sys_mount'],
                },
                {
                    'id': 'back_control',
                    'label': 'Back Control',
                    'japanese': 'Ushiro-kesa-gatame',
                    'description': 'Back mount, rear body triangle, turtle.',
                    'sys_nodes': ['sys_back_control'],
                },
            ],
        },
    ]

    # Submission mechanism groupings (force vector types)
    SUBMISSION_GROUPS = [
        {
            'id': 'chokes',
            'label': 'Chokes',
            'japanese': 'Jime-waza',
            'description': 'Blood/air restriction — arterial compression.',
            'color': 'rgb(190, 100, 100)',
            'mechanism': 'choke',
        },
        {
            'id': 'locks',
            'label': 'Joint Locks',
            'japanese': 'Kansetsu-waza (Gatame)',
            'description': 'Hyperextension — armbar, kneebar, straight ankle lock.',
            'color': 'rgb(210, 140, 110)',
            'mechanism': 'lock',
        },
        {
            'id': 'entanglements',
            'label': 'Entanglements',
            'japanese': 'Kansetsu-waza (Garami)',
            'description': 'Rotational joint attack — kimura, heel hook, toe hold.',
            'color': 'rgb(200, 175, 100)',
            'mechanism': 'entanglement',
        },
        {
            'id': 'compressions',
            'label': 'Compressions',
            'japanese': 'Kansetsu-waza (Oshi)',
            'description': 'Crushing tissue against bone — calf slicer, bicep slicer.',
            'color': 'rgb(100, 180, 175)',
            'mechanism': 'compression',
        },
    ]

    all_articles = Article.query.filter_by(is_published=True).all()

    def articles_for_tiers(sys_node_list, category_filter=None):
        """Return articles that have at least one of the given sys_ nodes in their graph_tier."""
        result = []
        for a in all_articles:
            if category_filter and a.category != category_filter:
                continue
            tiers = a.get_graph_tiers()
            if any(t in sys_node_list for t in tiers):
                result.append(a)
        return sorted(result, key=lambda a: a.title)

    def articles_by_mechanism(mechanism_val, only_submissions=True):
        """Return technique articles matching a mechanism value."""
        result = []
        for a in all_articles:
            if a.category != 'technique':
                continue
            if a.mechanism == mechanism_val:
                result.append(a)
        return sorted(result, key=lambda a: a.title)

    # Build tier data with live article lists
    for tier in TIER_TREE:
        if tier.get('subcategories'):
            for sub in tier['subcategories']:
                sub['articles'] = articles_for_tiers(sub['sys_nodes'])
                sub['count'] = len(sub['articles'])
            tier['articles'] = []
            tier['count'] = sum(s['count'] for s in tier['subcategories'])
        else:
            tier['articles'] = articles_for_tiers(tier['sys_nodes'])
            tier['count'] = len(tier['articles'])

    # Build submission groups
    for group in SUBMISSION_GROUPS:
        group['articles'] = articles_by_mechanism(group['mechanism'])
        group['count'] = len(group['articles'])
    submission_total = sum(g['count'] for g in SUBMISSION_GROUPS)

    # Concept articles (appear contextually across tiers, also listed separately)
    concept_articles = sorted(
        [a for a in all_articles if a.category == 'concept'],
        key=lambda a: a.title
    )

    # Reference library (non-graph categories)
    reference_groups = {
        'person': {'label': 'People', 'japanese': 'Jinbutsu', 'articles': []},
        'competition': {'label': 'Competitions', 'japanese': 'Taikai', 'articles': []},
        'style': {'label': 'Styles', 'japanese': 'Ryū-ha', 'articles': []},
        'glossary': {'label': 'Glossary', 'japanese': 'Yōgo', 'articles': []},
    }
    for a in all_articles:
        if a.category in reference_groups:
            reference_groups[a.category]['articles'].append(a)
    for g in reference_groups.values():
        g['articles'].sort(key=lambda a: a.title)
        g['count'] = len(g['articles'])

    # Unclassified articles — graph categories without taxonomy
    unclassified = [
        a for a in all_articles
        if a.category in ('technique', 'position', 'concept')
        and not a.taxonomy_complete
    ]

    total_articles = Article.query.filter_by(is_published=True).count()
    taxonomy_gap = len(unclassified)

    return render_template(
        'categories.html',
        tier_tree=TIER_TREE,
        submission_groups=SUBMISSION_GROUPS,
        submission_total=submission_total,
        concept_articles=concept_articles,
        reference_groups=reference_groups,
        unclassified=unclassified,
        total_articles=total_articles,
        taxonomy_gap=taxonomy_gap,
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
            'mechanism': a.mechanism or '',
            'target': a.target or '',
            'spatial': a.spatial_qualifier or '',
            'graphTier': a.graph_tier or '',
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
            'mechanism': a.mechanism or '',
            'target': a.target or '',
            'spatial': a.spatial_qualifier or '',
            'graphTier': a.graph_tier or '',
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

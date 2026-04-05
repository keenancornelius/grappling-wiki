"""
Wiki blueprint for article management.
Handles viewing, editing, history, diffs, and talk pages.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import desc
import markdown
import bleach
from difflib import unified_diff

from app import db
from app.models import Article, ArticleRevision, Discussion, DiscussionReply, Tag, User

wiki_bp = Blueprint('wiki', __name__, url_prefix='/wiki')

# HTML sanitization allowed tags and attributes
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'table',
                'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'div', 'span']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
    'div': ['class'],
    'span': ['class']
}


@wiki_bp.route('/<slug>')
def view(slug):
    """
    View an article.
    Increments view count and renders markdown to HTML.
    """
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    # Increment view count
    article.increment_view_count()

    # Convert markdown to HTML and sanitize
    html_content = markdown.markdown(article.content, extensions=['extra', 'codehilite'])
    html_content = bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

    # Get revision count
    revision_count = article.revisions.count()

    # Get related articles (same tags)
    related_articles = []
    if article.tags:
        tag_ids = [tag.id for tag in article.tags]
        related_articles = Article.query.filter(
            Article.id != article.id,
            Article.is_published == True,
            Article.tags.any(Tag.id.in_(tag_ids))
        ).limit(5).all()

    # Article data for contextual knowledge graph
    all_articles = Article.query.filter_by(is_published=True).all()
    graph_articles = [
        {'id': a.id, 'title': a.title, 'slug': a.slug,
         'summary': a.summary or '', 'category': a.category or '',
         'tags': [t.name for t in a.tags]}
        for a in all_articles
    ]

    return render_template(
        'wiki/view.html',
        article=article,
        html_content=html_content,
        revision_count=revision_count,
        related_articles=related_articles,
        graph_articles=graph_articles
    )


@wiki_bp.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    """
    Edit an article.
    GET: Show edit form
    POST: Save edit and create new revision
    """
    article = Article.query.filter_by(slug=slug).first_or_404()

    # Check permissions
    if article.is_protected and not (current_user.can_edit()):
        flash('You do not have permission to edit this article.', 'danger')
        abort(403)

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        is_minor = request.form.get('is_minor') == 'on'

        if not content:
            flash('Article content cannot be empty.', 'danger')
            return redirect(url_for('wiki.edit', slug=slug))

        # Get latest revision number
        latest_revision = article.revisions.order_by(
            desc(ArticleRevision.revision_number)
        ).first()
        next_revision_num = (latest_revision.revision_number + 1) if latest_revision else 1

        # Create new revision
        new_revision = ArticleRevision(
            article_id=article.id,
            editor_id=current_user.id,
            content=content,
            edit_summary=summary,
            revision_number=next_revision_num,
            is_minor=is_minor
        )
        db.session.add(new_revision)

        # Update article
        article.content = content
        article.updated_at = db.func.now()

        try:
            db.session.commit()
            flash(f'Article updated successfully (Revision #{next_revision_num}).', 'success')
            return redirect(url_for('wiki.view', slug=slug))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving article: {str(e)}', 'danger')
            return redirect(url_for('wiki.edit', slug=slug))

    return render_template(
        'wiki/edit.html',
        article=article
    )


@wiki_bp.route('/<slug>/history')
def history(slug):
    """
    Show all revisions of an article.
    """
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    page = request.args.get('page', 1, type=int)
    per_page = 25

    revisions = article.revisions.order_by(
        desc(ArticleRevision.created_at)
    ).paginate(page=page, per_page=per_page)

    return render_template(
        'wiki/history.html',
        article=article,
        revisions=revisions,
        page=page
    )


@wiki_bp.route('/<slug>/revision/<int:rev_id>')
def view_revision(slug, rev_id):
    """
    View a specific revision of an article.
    """
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    revision = ArticleRevision.query.filter_by(
        id=rev_id,
        article_id=article.id
    ).first_or_404()

    # Convert markdown to HTML and sanitize
    html_content = markdown.markdown(revision.content, extensions=['extra', 'codehilite'])
    html_content = bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

    return render_template(
        'wiki/revision.html',
        article=article,
        revision=revision,
        html_content=html_content
    )


@wiki_bp.route('/<slug>/diff/<int:rev1>/<int:rev2>')
def diff(slug, rev1, rev2):
    """
    Compare two revisions and show diff.
    """
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    revision1 = ArticleRevision.query.filter_by(
        id=rev1,
        article_id=article.id
    ).first_or_404()

    revision2 = ArticleRevision.query.filter_by(
        id=rev2,
        article_id=article.id
    ).first_or_404()

    # Ensure rev1 is older than rev2
    if revision1.created_at > revision2.created_at:
        revision1, revision2 = revision2, revision1

    # Generate diff
    content1_lines = revision1.content.splitlines(keepends=True)
    content2_lines = revision2.content.splitlines(keepends=True)

    diff_lines = list(unified_diff(
        content1_lines,
        content2_lines,
        fromfile=f'Revision {revision1.revision_number}',
        tofile=f'Revision {revision2.revision_number}',
        lineterm=''
    ))

    return render_template(
        'wiki/diff.html',
        article=article,
        revision1=revision1,
        revision2=revision2,
        diff_lines=diff_lines
    )


@wiki_bp.route('/<slug>/talk', methods=['GET', 'POST'])
def talk(slug):
    """
    View discussion/talk page for an article.
    GET: Show discussions
    POST: Add new discussion or reply
    """
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You must be logged in to participate in discussions.', 'info')
            return redirect(url_for('auth.login'))

        action = request.form.get('action')

        if action == 'new_discussion':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()

            if not title or not content:
                flash('Discussion title and content are required.', 'danger')
                return redirect(url_for('wiki.talk', slug=slug))

            new_discussion = Discussion(
                article_id=article.id,
                author_id=current_user.id,
                title=title,
                content=content
            )
            db.session.add(new_discussion)

            try:
                db.session.commit()
                flash('Discussion created successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating discussion: {str(e)}', 'danger')

            return redirect(url_for('wiki.talk', slug=slug))

        elif action == 'reply':
            discussion_id = request.form.get('discussion_id', type=int)
            content = request.form.get('content', '').strip()

            if not content:
                flash('Reply content cannot be empty.', 'danger')
                return redirect(url_for('wiki.talk', slug=slug))

            discussion = Discussion.query.filter_by(
                id=discussion_id,
                article_id=article.id
            ).first_or_404()

            new_reply = DiscussionReply(
                discussion_id=discussion.id,
                author_id=current_user.id,
                content=content
            )
            db.session.add(new_reply)

            try:
                db.session.commit()
                flash('Reply added successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding reply: {str(e)}', 'danger')

            return redirect(url_for('wiki.talk', slug=slug))

    # Get all discussions for this article
    page = request.args.get('page', 1, type=int)
    per_page = 10

    discussions = article.discussions.order_by(
        desc(Discussion.created_at)
    ).paginate(page=page, per_page=per_page)

    return render_template(
        'wiki/talk.html',
        article=article,
        discussions=discussions,
        page=page
    )


@wiki_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new article.
    GET: Show create form
    POST: Save new article
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        category = request.form.get('category', 'technique')

        # Validate inputs
        errors = []
        if not title:
            errors.append('Title is required.')
        if not slug:
            errors.append('Slug is required.')
        if not content:
            errors.append('Content is required.')

        # Check slug uniqueness
        if slug and Article.query.filter_by(slug=slug).first():
            errors.append('An article with this slug already exists.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'wiki/create.html',
                form_data={
                    'title': title,
                    'slug': slug,
                    'content': content,
                    'summary': summary,
                    'category': category
                }
            )

        # Sanitize slug
        slug = secure_filename(slug).lower().replace('_', '-')

        # Create article
        new_article = Article(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            author_id=current_user.id,
            category=category,
            is_published=True
        )
        db.session.add(new_article)

        try:
            db.session.flush()  # Get the ID without committing

            # Create initial revision
            initial_revision = ArticleRevision(
                article_id=new_article.id,
                editor_id=current_user.id,
                content=content,
                edit_summary='Initial revision',
                revision_number=1
            )
            db.session.add(initial_revision)
            db.session.commit()

            flash('Article created successfully!', 'success')
            return redirect(url_for('wiki.view', slug=slug))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating article: {str(e)}', 'danger')
            return redirect(url_for('wiki.create'))

    # Get valid categories
    categories = Article.VALID_CATEGORIES

    return render_template(
        'wiki/create.html',
        categories=categories
    )

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
import re

from app import db
from app.models import (Article, ArticleRevision, ArticleRelationship, Category,
                        Discussion, DiscussionReply, User, ContentFlag)

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


def _get_all_categories_flat():
    """
    Return all categories as a flat list, ordered for a nested dropdown.
    Each item has a .display_depth attribute for indentation.
    Uses display_depth instead of depth to avoid conflicting with
    the Category.depth @property.
    """
    def _walk(parent_id, current_depth):
        cats = Category.query.filter_by(parent_id=parent_id).order_by(Category.name).all()
        result = []
        for cat in cats:
            cat.display_depth = current_depth
            result.append(cat)
            result.extend(_walk(cat.id, current_depth + 1))
        return result

    return _walk(None, 0)


def _get_or_create_category(category_id, new_category_name):
    """
    Resolve category from form data.
    If new_category_name is provided, create a new category
    (optionally as a child of category_id).
    Returns a Category instance or None.
    """
    if new_category_name:
        new_name = new_category_name.strip()
        if not new_name:
            return None

        # Generate slug
        slug = re.sub(r'[^a-z0-9]+', '-', new_name.lower()).strip('-')
        if not slug:
            return None

        # Check if it already exists
        existing = Category.query.filter_by(slug=slug).first()
        if existing:
            return existing

        # Determine parent
        parent_id = None
        if category_id:
            try:
                parent_id = int(category_id)
                # Verify parent exists
                if not Category.query.get(parent_id):
                    parent_id = None
            except (ValueError, TypeError):
                parent_id = None

        new_cat = Category(
            name=new_name,
            slug=slug,
            parent_id=parent_id,
            created_by_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.add(new_cat)
        db.session.flush()  # Get the ID
        return new_cat

    elif category_id:
        try:
            cat_id = int(category_id)
            return Category.query.get(cat_id)
        except (ValueError, TypeError):
            return None

    return None


@wiki_bp.route('/<slug>')
def view(slug):
    """View an article."""
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    article.increment_view_count()

    html_content = markdown.markdown(article.content, extensions=['extra', 'codehilite'])
    html_content = bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

    revision_count = article.revisions.count()

    # Get relationships with eager-loaded articles (2 queries instead of N+1)
    from sqlalchemy.orm import joinedload
    outgoing_rels = ArticleRelationship.query.filter_by(
        source_article_id=article.id
    ).options(joinedload(ArticleRelationship.target_article)).all()

    incoming_rels = ArticleRelationship.query.filter_by(
        target_article_id=article.id
    ).options(joinedload(ArticleRelationship.source_article)).all()

    relationships = []
    related_articles = []
    seen_ids = {article.id}

    for rel in outgoing_rels:
        relationships.append({
            'id': rel.id,
            'direction': 'outgoing',
            'type': rel.relationship_type,
            'label': rel.type_label,
            'notes': rel.notes or '',
            'other': rel.target_article,
        })
        a = rel.target_article
        if a and a.id not in seen_ids and a.is_published:
            related_articles.append(a)
            seen_ids.add(a.id)

    for rel in incoming_rels:
        relationships.append({
            'id': rel.id,
            'direction': 'incoming',
            'type': rel.relationship_type,
            'label': rel.inverse_label,
            'notes': rel.notes or '',
            'other': rel.source_article,
        })
        a = rel.source_article
        if a and a.id not in seen_ids and a.is_published:
            related_articles.append(a)
            seen_ids.add(a.id)

    related_articles = related_articles[:6]

    return render_template(
        'wiki/view.html',
        article=article,
        html_content=html_content,
        revision_count=revision_count,
        related_articles=related_articles,
        relationships=relationships,
        relationship_types=ArticleRelationship.VALID_TYPES,
        relationship_labels=ArticleRelationship.TYPE_LABELS,
    )


@wiki_bp.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    """Edit an article."""
    article = Article.query.filter_by(slug=slug).first_or_404()

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

        latest_revision = article.revisions.order_by(
            desc(ArticleRevision.revision_number)
        ).first()
        next_revision_num = (latest_revision.revision_number + 1) if latest_revision else 1

        new_revision = ArticleRevision(
            article_id=article.id,
            editor_id=current_user.id,
            content=content,
            edit_summary=summary,
            revision_number=next_revision_num,
            is_minor=is_minor
        )
        db.session.add(new_revision)

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
    """Show all revisions of an article."""
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
    """View a specific revision of an article."""
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    revision = ArticleRevision.query.filter_by(
        id=rev_id,
        article_id=article.id
    ).first_or_404()

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
    """Compare two revisions and show diff."""
    article = Article.query.filter_by(slug=slug).first_or_404()

    if not article.is_published:
        abort(404)

    revision1 = ArticleRevision.query.filter_by(
        id=rev1, article_id=article.id
    ).first_or_404()

    revision2 = ArticleRevision.query.filter_by(
        id=rev2, article_id=article.id
    ).first_or_404()

    if revision1.created_at > revision2.created_at:
        revision1, revision2 = revision2, revision1

    content1_lines = revision1.content.splitlines(keepends=True)
    content2_lines = revision2.content.splitlines(keepends=True)

    diff_lines = list(unified_diff(
        content1_lines, content2_lines,
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
    """View discussion/talk page for an article."""
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
                id=discussion_id, article_id=article.id
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
    """Create a new article."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        category_id = request.form.get('category_id', '').strip()
        new_category = request.form.get('new_category', '').strip()

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
            categories = _get_all_categories_flat()
            return render_template(
                'wiki/create.html',
                categories=categories,
                form_data={
                    'title': title,
                    'slug': slug,
                    'content': content,
                    'summary': summary,
                    'category_id': category_id,
                    'new_category': new_category,
                }
            )

        # Sanitize slug
        slug = secure_filename(slug).lower().replace('_', '-')

        # Resolve category
        cat = _get_or_create_category(category_id, new_category)

        # Create article
        new_article = Article(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            author_id=current_user.id,
            category_id=cat.id if cat else None,
            category=cat.slug if cat else None,  # Legacy column
            is_published=True,
        )
        db.session.add(new_article)

        try:
            db.session.flush()

            # Create initial revision
            initial_revision = ArticleRevision(
                article_id=new_article.id,
                editor_id=current_user.id,
                content=content,
                edit_summary='Initial revision',
                revision_number=1
            )
            db.session.add(initial_revision)

            # Process queued relationships from the create form
            idx = 0
            while True:
                rel_type = request.form.get(f'rel_type_{idx}', '').strip()
                rel_target = request.form.get(f'rel_target_{idx}', '').strip()
                if not rel_type or not rel_target:
                    break
                if rel_type in ArticleRelationship.VALID_TYPES:
                    target_article = Article.query.filter_by(slug=rel_target, is_published=True).first()
                    if target_article and target_article.id != new_article.id:
                        rel = ArticleRelationship(
                            source_article_id=new_article.id,
                            target_article_id=target_article.id,
                            relationship_type=rel_type,
                            created_by_id=current_user.id,
                        )
                        db.session.add(rel)
                idx += 1

            db.session.commit()

            flash('Article created successfully!', 'success')
            return redirect(url_for('wiki.view', slug=slug))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating article: {str(e)}', 'danger')
            return redirect(url_for('wiki.create'))

    # GET: show create form
    categories = _get_all_categories_flat()

    return render_template(
        'wiki/create.html',
        categories=categories
    )


@wiki_bp.route('/<slug>/flag', methods=['POST'])
@login_required
def flag_article(slug):
    """Submit a content flag on an article for moderator review."""
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()

    reason = request.form.get('reason', '').strip()
    details = request.form.get('details', '').strip()

    if reason not in ContentFlag.REASONS:
        flash('Invalid flag reason.', 'danger')
        return redirect(url_for('wiki.view', slug=slug))

    # Check if this user already flagged this article (pending)
    existing = ContentFlag.query.filter_by(
        article_id=article.id,
        reporter_id=current_user.id,
        status='pending'
    ).first()
    if existing:
        flash('You already have a pending flag on this article.', 'info')
        return redirect(url_for('wiki.view', slug=slug))

    flag = ContentFlag(
        article_id=article.id,
        reporter_id=current_user.id,
        reason=reason,
        details=details,
    )
    db.session.add(flag)

    try:
        db.session.commit()
        flash('Thank you. Your flag has been submitted for review.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not submit flag. Please try again.', 'danger')

    return redirect(url_for('wiki.view', slug=slug))

"""
Admin / moderation blueprint.
Dashboard, user management, article moderation, flags, audit log.
All routes require admin privileges.
"""

from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_

from app import db
from app.models import (
    User, Article, ArticleRevision, ArticleRelationship,
    Category, Discussion, DiscussionReply,
    ContentFlag, ModAction
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator: require admin privileges."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.can_moderate():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _log_action(action_type, reason=None, details=None,
                target_user_id=None, target_article_id=None,
                target_revision_id=None, target_flag_id=None):
    """Record a moderation action in the audit log."""
    entry = ModAction(
        action_type=action_type,
        moderator_id=current_user.id,
        target_user_id=target_user_id,
        target_article_id=target_article_id,
        target_revision_id=target_revision_id,
        target_flag_id=target_flag_id,
        reason=reason,
        details=details,
    )
    db.session.add(entry)


# ── Dashboard ──

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard — overview of site health and moderation queue."""
    # Stats
    total_users = User.query.count()
    new_users_24h = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    total_articles = Article.query.count()
    published_articles = Article.query.filter_by(is_published=True).count()
    total_edits = ArticleRevision.query.count()
    edits_24h = ArticleRevision.query.filter(
        ArticleRevision.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    banned_users = User.query.filter_by(is_banned=True).count()
    pending_flags = ContentFlag.query.filter_by(status='pending').count()

    # Recent registrations
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()

    # Recent edits
    recent_edits = db.session.query(ArticleRevision, Article).join(
        Article, ArticleRevision.article_id == Article.id
    ).order_by(desc(ArticleRevision.created_at)).limit(15).all()

    # Recent mod actions
    recent_actions = ModAction.query.order_by(
        desc(ModAction.created_at)
    ).limit(10).all()

    # Pending flags
    flags = ContentFlag.query.filter_by(status='pending').order_by(
        desc(ContentFlag.created_at)
    ).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        new_users_24h=new_users_24h,
        total_articles=total_articles,
        published_articles=published_articles,
        total_edits=total_edits,
        edits_24h=edits_24h,
        banned_users=banned_users,
        pending_flags=pending_flags,
        recent_users=recent_users,
        recent_edits=recent_edits,
        recent_actions=recent_actions,
        flags=flags,
    )


# ── User Management ──

@admin_bp.route('/users')
@admin_required
def users():
    """Paginated user list with search and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = 30
    search = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '')
    sort = request.args.get('sort', 'recent')

    query = User.query

    if search:
        pattern = f'%{search}%'
        query = query.filter(or_(
            User.username.ilike(pattern),
            User.email.ilike(pattern)
        ))

    if role_filter == 'admin':
        query = query.filter_by(is_admin=True)
    elif role_filter == 'editor':
        query = query.filter_by(is_editor=True)
    elif role_filter == 'banned':
        query = query.filter_by(is_banned=True)
    elif role_filter == 'suspended':
        query = query.filter_by(is_suspended=True)

    if sort == 'username':
        query = query.order_by(User.username)
    elif sort == 'edits':
        # Subquery for edit count
        edit_counts = db.session.query(
            ArticleRevision.editor_id,
            func.count().label('cnt')
        ).group_by(ArticleRevision.editor_id).subquery()
        query = query.outerjoin(edit_counts, User.id == edit_counts.c.editor_id) \
                     .order_by(desc(func.coalesce(edit_counts.c.cnt, 0)))
    else:
        query = query.order_by(desc(User.created_at))

    users_page = query.paginate(page=page, per_page=per_page)

    # Get edit counts for displayed users
    user_ids = [u.id for u in users_page.items]
    edit_counts_map = {}
    if user_ids:
        counts = db.session.query(
            ArticleRevision.editor_id,
            func.count().label('cnt')
        ).filter(
            ArticleRevision.editor_id.in_(user_ids)
        ).group_by(ArticleRevision.editor_id).all()
        edit_counts_map = {eid: cnt for eid, cnt in counts}

    return render_template(
        'admin/users.html',
        users=users_page,
        edit_counts=edit_counts_map,
        search=search,
        role_filter=role_filter,
        sort=sort,
        page=page,
    )


@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def user_detail(user_id):
    """View and manage a specific user."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        action = request.form.get('action', '')
        reason = request.form.get('reason', '').strip()

        if action == 'ban':
            if user.is_admin:
                flash('Cannot ban another admin.', 'danger')
            else:
                user.is_banned = True
                user.ban_reason = reason or 'No reason provided'
                user.banned_at = datetime.utcnow()
                user.banned_by_id = current_user.id
                _log_action('ban_user', reason=reason, target_user_id=user.id)
                db.session.commit()
                flash(f'User {user.username} has been banned.', 'success')

        elif action == 'unban':
            user.is_banned = False
            user.ban_reason = None
            user.banned_at = None
            user.banned_by_id = None
            _log_action('unban_user', reason=reason, target_user_id=user.id)
            db.session.commit()
            flash(f'User {user.username} has been unbanned.', 'success')

        elif action == 'suspend':
            duration_hours = request.form.get('duration', 24, type=int)
            duration_hours = max(1, min(duration_hours, 8760))  # 1h to 1 year
            user.is_suspended = True
            user.suspended_until = datetime.utcnow() + timedelta(hours=duration_hours)
            user.suspend_reason = reason or 'Temporary suspension'
            _log_action('suspend_user', reason=reason, target_user_id=user.id,
                        details=f'Duration: {duration_hours} hours')
            db.session.commit()
            flash(f'User {user.username} suspended for {duration_hours} hours.', 'success')

        elif action == 'unsuspend':
            user.is_suspended = False
            user.suspended_until = None
            user.suspend_reason = None
            _log_action('unsuspend_user', reason=reason, target_user_id=user.id)
            db.session.commit()
            flash(f'Suspension lifted for {user.username}.', 'success')

        elif action == 'promote_editor':
            user.is_editor = True
            _log_action('promote_editor', reason=reason, target_user_id=user.id)
            db.session.commit()
            flash(f'{user.username} promoted to Editor.', 'success')

        elif action == 'demote_editor':
            user.is_editor = False
            _log_action('demote_editor', reason=reason, target_user_id=user.id)
            db.session.commit()
            flash(f'{user.username} demoted from Editor.', 'success')

        elif action == 'promote_admin':
            user.is_admin = True
            _log_action('promote_admin', reason=reason, target_user_id=user.id)
            db.session.commit()
            flash(f'{user.username} promoted to Admin.', 'success')

        return redirect(url_for('admin.user_detail', user_id=user.id))

    # Get user stats
    article_count = user.articles.count()
    edit_count = user.revisions.count()
    discussion_count = user.discussions.count()
    recent_edits = user.revisions.order_by(desc(ArticleRevision.created_at)).limit(10).all()
    mod_history = ModAction.query.filter_by(target_user_id=user.id).order_by(
        desc(ModAction.created_at)
    ).limit(20).all()

    return render_template(
        'admin/user_detail.html',
        user=user,
        article_count=article_count,
        edit_count=edit_count,
        discussion_count=discussion_count,
        recent_edits=recent_edits,
        mod_history=mod_history,
    )


# ── Article Moderation ──

@admin_bp.route('/articles')
@admin_required
def articles():
    """Browse all articles (including unpublished) with mod actions."""
    page = request.args.get('page', 1, type=int)
    per_page = 30
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')

    query = Article.query

    if search:
        pattern = f'%{search}%'
        query = query.filter(or_(
            Article.title.ilike(pattern),
            Article.slug.ilike(pattern)
        ))

    if status_filter == 'published':
        query = query.filter_by(is_published=True)
    elif status_filter == 'unpublished':
        query = query.filter_by(is_published=False)
    elif status_filter == 'protected':
        query = query.filter_by(is_protected=True)

    articles_page = query.order_by(desc(Article.updated_at)).paginate(page=page, per_page=per_page)

    return render_template(
        'admin/articles.html',
        articles=articles_page,
        search=search,
        status_filter=status_filter,
        page=page,
    )


@admin_bp.route('/articles/<int:article_id>/action', methods=['POST'])
@admin_required
def article_action(article_id):
    """Perform a moderation action on an article."""
    article = Article.query.get_or_404(article_id)
    action = request.form.get('action', '')
    reason = request.form.get('reason', '').strip()

    if action == 'lock':
        article.is_protected = True
        _log_action('lock_article', reason=reason, target_article_id=article.id)
        db.session.commit()
        flash(f'"{article.title}" is now protected (editor-only editing).', 'success')

    elif action == 'unlock':
        article.is_protected = False
        _log_action('unlock_article', reason=reason, target_article_id=article.id)
        db.session.commit()
        flash(f'"{article.title}" is now open for editing.', 'success')

    elif action == 'unpublish':
        article.is_published = False
        _log_action('unpublish_article', reason=reason, target_article_id=article.id)
        db.session.commit()
        flash(f'"{article.title}" has been unpublished.', 'success')

    elif action == 'publish':
        article.is_published = True
        _log_action('publish_article', reason=reason, target_article_id=article.id)
        db.session.commit()
        flash(f'"{article.title}" has been published.', 'success')

    elif action == 'delete':
        title = article.title
        _log_action('delete_article', reason=reason, target_article_id=article.id,
                     details=f'Title: {title}, Slug: {article.slug}')
        db.session.delete(article)
        db.session.commit()
        flash(f'"{title}" has been deleted.', 'success')
        return redirect(url_for('admin.articles'))

    elif action == 'rollback':
        revision_id = request.form.get('revision_id', type=int)
        if revision_id:
            revision = ArticleRevision.query.filter_by(
                id=revision_id, article_id=article.id
            ).first()
            if revision:
                # Restore article content to this revision
                article.content = revision.content
                article.updated_at = datetime.utcnow()

                # Create a new revision recording the rollback
                latest = article.revisions.order_by(
                    desc(ArticleRevision.revision_number)
                ).first()
                next_num = (latest.revision_number + 1) if latest else 1

                rollback_rev = ArticleRevision(
                    article_id=article.id,
                    editor_id=current_user.id,
                    content=revision.content,
                    edit_summary=f'Rollback to revision #{revision.revision_number}',
                    revision_number=next_num,
                )
                db.session.add(rollback_rev)
                _log_action('rollback_revision', reason=reason,
                            target_article_id=article.id,
                            target_revision_id=revision.id,
                            details=f'Rolled back to revision #{revision.revision_number}')
                db.session.commit()
                flash(f'Article rolled back to revision #{revision.revision_number}.', 'success')
            else:
                flash('Revision not found.', 'danger')
        else:
            flash('No revision specified.', 'danger')

    return redirect(url_for('admin.articles'))


# ── Content Flags ──

@admin_bp.route('/flags')
@admin_required
def flags():
    """View content flags (moderation queue)."""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    status_filter = request.args.get('status', 'pending')

    query = ContentFlag.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    flags_page = query.order_by(desc(ContentFlag.created_at)).paginate(
        page=page, per_page=per_page
    )

    return render_template(
        'admin/flags.html',
        flags=flags_page,
        status_filter=status_filter,
        page=page,
    )


@admin_bp.route('/flags/<int:flag_id>/action', methods=['POST'])
@admin_required
def flag_action(flag_id):
    """Resolve or dismiss a content flag."""
    flag = ContentFlag.query.get_or_404(flag_id)
    action = request.form.get('action', '')
    note = request.form.get('note', '').strip()

    if action == 'dismiss':
        flag.status = 'dismissed'
        flag.reviewed_by_id = current_user.id
        flag.reviewed_at = datetime.utcnow()
        flag.resolution_note = note
        _log_action('dismiss_flag', reason=note, target_flag_id=flag.id,
                     target_article_id=flag.article_id)
        db.session.commit()
        flash('Flag dismissed.', 'info')

    elif action == 'resolve':
        flag.status = 'actioned'
        flag.reviewed_by_id = current_user.id
        flag.reviewed_at = datetime.utcnow()
        flag.resolution_note = note
        _log_action('resolve_flag', reason=note, target_flag_id=flag.id,
                     target_article_id=flag.article_id)
        db.session.commit()
        flash('Flag resolved.', 'success')

    return redirect(url_for('admin.flags'))


# ── Audit Log ──

@admin_bp.route('/log')
@admin_required
def audit_log():
    """View the moderation audit log."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    action_filter = request.args.get('action', '')

    query = ModAction.query
    if action_filter:
        query = query.filter_by(action_type=action_filter)

    log_page = query.order_by(desc(ModAction.created_at)).paginate(
        page=page, per_page=per_page
    )

    return render_template(
        'admin/audit_log.html',
        log=log_page,
        action_filter=action_filter,
        page=page,
        all_actions=ModAction.ACTIONS,
    )

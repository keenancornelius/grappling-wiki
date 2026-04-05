"""
Authentication blueprint for user registration, login, and profiles.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc

from app import db
from app.models import User, Article, ArticleRevision

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration form and handler.
    GET: Show registration form
    POST: Create new user account
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate input
        errors = []

        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif User.query.filter_by(username=username).first():
            errors.append('Username already exists.')

        if not email:
            errors.append('Email is required.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'auth/register.html',
                username=username,
                email=email
            )

        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        db.session.add(user)

        try:
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login form and handler.
    GET: Show login form
    POST: Authenticate user
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')

            # Redirect to next page if specified
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Log out the current user.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile/<username>')
def profile(username):
    """
    Display user profile with their contributions.
    """
    user = User.query.filter_by(username=username).first_or_404()

    # Get user's articles
    page = request.args.get('page', 1, type=int)
    per_page = 10

    articles = user.articles.filter_by(is_published=True).order_by(
        desc(Article.created_at)
    ).paginate(page=page, per_page=per_page)

    # Get user's recent edits
    recent_edits = user.revisions.order_by(
        desc(ArticleRevision.created_at)
    ).limit(10).all()

    # Get statistics
    article_count = user.articles.filter_by(is_published=True).count()
    edit_count = user.revisions.count()

    # Get articles edited but not created by user
    edited_article_ids = db.session.query(ArticleRevision.article_id).filter(
        ArticleRevision.editor_id == user.id
    ).distinct()
    edited_articles = Article.query.filter(
        Article.id.in_(edited_article_ids),
        Article.author_id != user.id,
        Article.is_published == True
    ).count()

    return render_template(
        'auth/profile.html',
        user=user,
        articles=articles,
        recent_edits=recent_edits,
        article_count=article_count,
        edit_count=edit_count,
        edited_articles=edited_articles,
        page=page
    )

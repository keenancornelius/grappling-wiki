"""
Authentication blueprint for user registration, login, and profiles.
Hardened against spam, bot registration, and abuse.
"""

import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc

from app import db
from app.models import User, Article, ArticleRevision

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ── Rate limiting: track registration attempts per IP ──
# { ip: [(timestamp, success_bool), ...] }
_registration_attempts = defaultdict(list)
_login_attempts = defaultdict(list)

# Limits
MAX_REGISTRATIONS_PER_IP_PER_HOUR = 3
MAX_LOGIN_ATTEMPTS_PER_IP_PER_MINUTE = 10
REGISTRATION_COOLDOWN_SECONDS = 30  # Min time between reg attempts from same IP

# Disposable/throwaway email domain blocklist (common ones)
BLOCKED_EMAIL_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', 'guerrillamail.net', 'tempmail.com',
    'throwaway.email', 'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com',
    'grr.la', 'dispostable.com', 'trashmail.com', 'trashmail.me', 'trashmail.net',
    'maildrop.cc', 'mailnesia.com', 'tempr.email', 'temp-mail.org',
    'fakeinbox.com', 'tempail.com', 'burnermail.io', 'getnada.com',
    'mohmal.com', '10minutemail.com', 'minutemail.com', 'emailondeck.com',
}

# Reserved usernames that shouldn't be registerable
RESERVED_USERNAMES = {
    'admin', 'administrator', 'mod', 'moderator', 'system', 'root', 'superuser',
    'grapplingwiki', 'wiki', 'support', 'help', 'staff', 'team', 'official',
    'api', 'www', 'mail', 'email', 'info', 'noreply', 'no-reply',
    'legionajj', 'legion', 'keenan', 'keenancornelius',
}


def _clean_old_attempts(attempts_dict, ip, max_age_seconds):
    """Remove attempts older than max_age_seconds."""
    cutoff = time.time() - max_age_seconds
    attempts_dict[ip] = [a for a in attempts_dict[ip] if a[0] > cutoff]


def _check_registration_rate(ip):
    """Returns (allowed: bool, reason: str or None)."""
    _clean_old_attempts(_registration_attempts, ip, 3600)
    attempts = _registration_attempts[ip]

    # Cooldown between attempts
    if attempts and (time.time() - attempts[-1][0]) < REGISTRATION_COOLDOWN_SECONDS:
        return False, 'Please wait a moment before trying again.'

    # Max per hour
    if len(attempts) >= MAX_REGISTRATIONS_PER_IP_PER_HOUR:
        return False, 'Too many registration attempts. Please try again later.'

    return True, None


def _check_login_rate(ip):
    """Returns (allowed: bool, reason: str or None)."""
    _clean_old_attempts(_login_attempts, ip, 60)
    attempts = _login_attempts[ip]

    if len(attempts) >= MAX_LOGIN_ATTEMPTS_PER_IP_PER_MINUTE:
        return False, 'Too many login attempts. Please wait a minute.'

    return True, None


def _validate_password_strength(password):
    """Check password meets minimum security requirements."""
    errors = []
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long.')
    if not re.search(r'[a-zA-Z]', password):
        errors.append('Password must contain at least one letter.')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain at least one number.')
    return errors


def _validate_email_domain(email):
    """Check email domain is not a known disposable provider."""
    domain = email.lower().split('@')[-1] if '@' in email else ''
    if domain in BLOCKED_EMAIL_DOMAINS:
        return False
    return True


def _validate_username(username):
    """Check username format and availability."""
    errors = []
    if not username:
        errors.append('Username is required.')
        return errors

    if len(username) < 3:
        errors.append('Username must be at least 3 characters long.')
    if len(username) > 30:
        errors.append('Username must be 30 characters or fewer.')
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        errors.append('Username can only contain letters, numbers, underscores, and hyphens.')
    if username.lower() in RESERVED_USERNAMES:
        errors.append('This username is reserved.')
    if User.query.filter(db.func.lower(User.username) == username.lower()).first():
        errors.append('Username already taken.')

    return errors


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration — hardened against bots and spam.
    Includes honeypot, rate limiting, password strength, email validation.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        ip = request.remote_addr or '0.0.0.0'

        # ── Honeypot check: if the hidden field has a value, it's a bot ──
        honeypot = request.form.get('website_url', '')
        if honeypot:
            # Silently reject — bots don't need feedback
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        # ── Timing check: if form was submitted too fast, likely a bot ──
        form_loaded_at = request.form.get('_form_ts', '')
        if form_loaded_at:
            try:
                load_time = float(form_loaded_at)
                if (time.time() - load_time) < 3.0:
                    # Submitted in under 3 seconds — suspicious
                    flash('Registration successful! You can now log in.', 'success')
                    return redirect(url_for('auth.login'))
            except (ValueError, TypeError):
                pass

        # ── Rate limit check ──
        allowed, reason = _check_registration_rate(ip)
        if not allowed:
            flash(reason, 'danger')
            return redirect(url_for('auth.register'))

        # Record the attempt
        _registration_attempts[ip].append((time.time(), False))

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # ── Validate everything ──
        errors = []

        # Username
        errors.extend(_validate_username(username))

        # Email
        if not email:
            errors.append('Email is required.')
        elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            errors.append('Please enter a valid email address.')
        elif not _validate_email_domain(email):
            errors.append('Please use a permanent email address (disposable emails are not accepted).')
        elif User.query.filter(db.func.lower(User.email) == email.lower()).first():
            errors.append('Email already registered.')

        # Password strength
        if not password:
            errors.append('Password is required.')
        else:
            errors.extend(_validate_password_strength(password))

        # Confirm password
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'auth/register.html',
                username=username,
                email=email,
                form_ts=time.time()
            )

        # ── Create the account ──
        user = User(
            username=username,
            email=email,
            registration_ip=ip
        )
        user.set_password(password)
        db.session.add(user)

        try:
            db.session.commit()
            # Update attempt record to success
            _registration_attempts[ip][-1] = (time.time(), True)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html', form_ts=time.time())


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login — with rate limiting and ban/suspension checks.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        ip = request.remote_addr or '0.0.0.0'

        # Rate limit login attempts
        allowed, reason = _check_login_rate(ip)
        if not allowed:
            flash(reason, 'danger')
            return redirect(url_for('auth.login'))

        _login_attempts[ip].append((time.time(), False))

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Check if banned
            if user.is_banned:
                flash('This account has been banned.', 'danger')
                return redirect(url_for('auth.login'))

            # Check if suspended
            if user.is_suspended and user.suspended_until and user.suspended_until > datetime.utcnow():
                remaining = user.suspended_until - datetime.utcnow()
                hours = int(remaining.total_seconds() // 3600)
                if hours > 24:
                    time_str = f'{hours // 24} day(s)'
                elif hours > 0:
                    time_str = f'{hours} hour(s)'
                else:
                    time_str = 'less than an hour'
                flash(f'Account suspended for {time_str}. Reason: {user.suspend_reason or "Policy violation"}', 'danger')
                return redirect(url_for('auth.login'))

            # Successful login
            user.last_login_at = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')

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

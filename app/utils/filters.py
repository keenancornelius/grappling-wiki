"""
Jinja2 template filters for GrapplingWiki
"""

import markdown
import bleach
from datetime import datetime, timedelta


# Allowed HTML tags for markdown output
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'table', 'thead', 'tbody',
    'tr', 'th', 'td', 'img', 'hr', 'div', 'span'
]

# Allowed attributes for HTML tags
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'div': ['class'],
    'span': ['class']
}


def markdown_to_html(text):
    """
    Convert markdown text to sanitized HTML using markdown and bleach.

    Args:
        text (str): Markdown formatted text

    Returns:
        str: Sanitized HTML
    """
    if not text:
        return ''

    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=['tables', 'fenced_code', 'codehilite'],
        extension_configs={
            'markdown.extensions.codehilite': {
                'use_pygments': True,
                'css_class': 'highlight'
            }
        }
    )

    # Sanitize HTML
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

    return clean_html


def timeago(dt):
    """
    Convert datetime to human-readable "time ago" format.
    Example: "2 hours ago", "3 days ago", "just now"

    Args:
        dt (datetime): DateTime object

    Returns:
        str: Human-readable time difference
    """
    if not dt:
        return ''

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except (ValueError, TypeError):
            return ''

    now = datetime.utcnow()
    diff = now - dt

    # Calculate time units
    seconds = diff.total_seconds()

    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:  # 7 days
        days = int(seconds // 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif seconds < 2592000:  # 30 days
        weeks = int(seconds // 604800)
        return f'{weeks} week{"s" if weeks > 1 else ""} ago'
    elif seconds < 31536000:  # 365 days
        months = int(seconds // 2592000)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(seconds // 31536000)
        return f'{years} year{"s" if years > 1 else ""} ago'


def word_count(text):
    """
    Count the number of words in text.

    Args:
        text (str): Text to count

    Returns:
        int: Number of words
    """
    if not text:
        return 0

    # Remove markdown symbols and count words
    clean_text = text.strip()
    words = clean_text.split()
    return len(words)


def register_filters(app):
    """
    Register all custom filters with Flask application.

    Args:
        app (Flask): Flask application instance
    """
    app.jinja_env.filters['markdown_to_html'] = markdown_to_html
    app.jinja_env.filters['timeago'] = timeago
    app.jinja_env.filters['word_count'] = word_count

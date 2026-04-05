"""
Wiki helper functions for GrapplingWiki
Includes slug generation, TOC generation, HTML sanitization, and diff computation
"""

import re
import bleach
from html.parser import HTMLParser
from difflib import SequenceMatcher


def generate_slug(title):
    """
    Generate a URL-friendly slug from a title.

    Args:
        title (str): Article title

    Returns:
        str: URL-friendly slug
    """
    if not title:
        return ''

    # Convert to lowercase
    slug = title.lower().strip()

    # Remove non-alphanumeric characters except spaces and hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Remove leading and trailing hyphens
    slug = slug.strip('-')

    return slug


def generate_toc(html_content):
    """
    Extract headings from HTML content and generate table of contents.

    Args:
        html_content (str): HTML content

    Returns:
        dict: TOC structure with headings organized by level
    """
    class HeadingParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.headings = []
            self.heading_id_counter = {}

        def handle_starttag(self, tag, attrs):
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                self.current_tag = tag
                self.current_level = int(tag[1])
                # Look for id attribute
                for attr, value in attrs:
                    if attr == 'id':
                        self.heading_id = value
                        break
                else:
                    # Generate id if not found
                    tag_base = f'heading-{self.current_level}'
                    if tag_base not in self.heading_id_counter:
                        self.heading_id_counter[tag_base] = 0
                    self.heading_id_counter[tag_base] += 1
                    self.heading_id = f'{tag_base}-{self.heading_id_counter[tag_base]}'

        def handle_data(self, data):
            if hasattr(self, 'current_tag'):
                text = data.strip()
                if text:
                    self.headings.append({
                        'level': self.current_level,
                        'text': text,
                        'id': self.heading_id
                    })
                delattr(self, 'current_tag')

    parser = HeadingParser()
    parser.feed(html_content)

    # Build nested structure
    toc = []
    stack = []

    for heading in parser.headings:
        level = heading['level']

        # Adjust stack to current level
        while stack and stack[-1]['level'] >= level:
            stack.pop()

        if not stack:
            # Top level
            heading['children'] = []
            toc.append(heading)
            stack.append(heading)
        else:
            # Child of last item in stack
            heading['children'] = []
            stack[-1]['children'].append(heading)
            stack.append(heading)

    return toc


def sanitize_html(html_content):
    """
    Sanitize HTML content using bleach.
    Removes potentially dangerous tags and attributes.

    Args:
        html_content (str): HTML content to sanitize

    Returns:
        str: Sanitized HTML
    """
    allowed_tags = [
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'table', 'thead', 'tbody',
        'tr', 'th', 'td', 'img', 'hr', 'div', 'span', 'section', 'article', 'figure',
        'figcaption', 'dl', 'dt', 'dd'
    ]

    allowed_attributes = {
        'a': ['href', 'title', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class', 'id'],
        'span': ['class', 'id'],
        'section': ['class', 'id'],
        'article': ['class', 'id'],
        'figure': ['class', 'id']
    }

    clean_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

    return clean_html


def compute_diff(old_text, new_text):
    """
    Compute diff between two texts using SequenceMatcher.
    Returns a list of diff operations.

    Args:
        old_text (str): Original text
        new_text (str): New text

    Returns:
        list: List of diff entries with operation type and content
    """
    if not old_text:
        old_text = ''
    if not new_text:
        new_text = ''

    # Split into lines for better diff display
    old_lines = old_text.split('\n')
    new_lines = new_text.split('\n')

    matcher = SequenceMatcher(None, old_lines, new_lines)
    diff = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Unchanged lines
            for line in old_lines[i1:i2]:
                diff.append({
                    'type': 'context',
                    'content': line
                })
        elif tag == 'delete':
            # Removed lines
            for line in old_lines[i1:i2]:
                diff.append({
                    'type': 'delete',
                    'content': line
                })
        elif tag == 'insert':
            # Added lines
            for line in new_lines[j1:j2]:
                diff.append({
                    'type': 'add',
                    'content': line
                })
        elif tag == 'replace':
            # Replaced lines (show as delete then add)
            for line in old_lines[i1:i2]:
                diff.append({
                    'type': 'delete',
                    'content': line
                })
            for line in new_lines[j1:j2]:
                diff.append({
                    'type': 'add',
                    'content': line
                })

    return diff


def get_excerpt(text, length=200):
    """
    Get an excerpt from text of specified length.

    Args:
        text (str): Full text
        length (int): Maximum length of excerpt

    Returns:
        str: Excerpt with ellipsis if truncated
    """
    if not text:
        return ''

    # Remove markdown and HTML tags
    clean_text = re.sub(r'[#*_`\[\]()]', '', text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)

    if len(clean_text) <= length:
        return clean_text

    # Truncate to length and find last word boundary
    excerpt = clean_text[:length]
    last_space = excerpt.rfind(' ')
    if last_space > 0:
        excerpt = excerpt[:last_space]

    return excerpt.rstrip() + '...'


def format_text(text, format_type='plain'):
    """
    Format text for different contexts.

    Args:
        text (str): Text to format
        format_type (str): Format type - 'plain', 'truncate', 'slug'

    Returns:
        str: Formatted text
    """
    if not text:
        return ''

    if format_type == 'plain':
        # Remove all markdown and HTML
        text = re.sub(r'[#*_`\[\]()]', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    elif format_type == 'truncate':
        return get_excerpt(text)

    elif format_type == 'slug':
        return generate_slug(text)

    return text


def count_words(text):
    """
    Count words in text.

    Args:
        text (str): Text to count

    Returns:
        int: Word count
    """
    if not text:
        return 0

    # Remove markdown and HTML
    clean_text = re.sub(r'[#*_`\[\]()]', '', text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)

    # Split on whitespace and filter empty strings
    words = [w for w in clean_text.split() if w]
    return len(words)


def estimate_read_time(text, words_per_minute=200):
    """
    Estimate reading time in minutes.

    Args:
        text (str): Article text
        words_per_minute (int): Average reading speed

    Returns:
        str: Reading time estimate (e.g., "5 min read")
    """
    word_count = count_words(text)
    minutes = max(1, round(word_count / words_per_minute))

    if minutes == 1:
        return "1 min read"
    else:
        return f"{minutes} min read"

"""
SEO utilities for GrapplingWiki
Handles sitemap generation, meta tags, and structured data (JSON-LD)
"""

import json
from datetime import datetime
from urllib.parse import urljoin


def generate_sitemap_xml(articles, base_url='https://grapplingwiki.com'):
    """
    Generate XML sitemap for search engines.

    Args:
        articles (list): List of article objects with url, updated_at attributes
        base_url (str): Base URL of the website

    Returns:
        str: XML sitemap string
    """
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Add home page
    sitemap_xml += '  <url>\n'
    sitemap_xml += f'    <loc>{base_url}/</loc>\n'
    sitemap_xml += f'    <lastmod>{datetime.utcnow().isoformat()}</lastmod>\n'
    sitemap_xml += '    <changefreq>daily</changefreq>\n'
    sitemap_xml += '    <priority>1.0</priority>\n'
    sitemap_xml += '  </url>\n'

    # Add articles
    if articles:
        for article in articles:
            article_url = urljoin(base_url, article.url if hasattr(article, 'url') else f'/article/{article.slug}')
            last_modified = article.updated_at if hasattr(article, 'updated_at') else datetime.utcnow()

            sitemap_xml += '  <url>\n'
            sitemap_xml += f'    <loc>{article_url}</loc>\n'
            sitemap_xml += f'    <lastmod>{last_modified.isoformat() if hasattr(last_modified, "isoformat") else last_modified}</lastmod>\n'
            sitemap_xml += '    <changefreq>weekly</changefreq>\n'
            sitemap_xml += '    <priority>0.8</priority>\n'
            sitemap_xml += '  </url>\n'

    sitemap_xml += '</urlset>'

    return sitemap_xml


def generate_meta_tags(title, description, url, article=None):
    """
    Generate meta tags dictionary for HTML head.

    Args:
        title (str): Page title
        description (str): Page description
        url (str): Full page URL
        article (object): Optional article object with additional data

    Returns:
        dict: Dictionary of meta tag data
    """
    meta_tags = {
        'title': title,
        'description': description,
        'og_title': title,
        'og_description': description,
        'og_type': 'website',
        'og_url': url,
        'twitter_card': 'summary_large_image',
        'twitter_title': title,
        'twitter_description': description,
        'canonical': url
    }

    if article:
        # Add article-specific meta tags
        if hasattr(article, 'image_url') and article.image_url:
            meta_tags['og_image'] = article.image_url
            meta_tags['twitter_image'] = article.image_url

        if hasattr(article, 'created_at'):
            meta_tags['article_published_time'] = article.created_at.isoformat()

        if hasattr(article, 'updated_at'):
            meta_tags['article_modified_time'] = article.updated_at.isoformat()

        if hasattr(article, 'author') and article.author:
            author_name = article.author.username if hasattr(article.author, 'username') else str(article.author)
            meta_tags['article_author'] = author_name

        if hasattr(article, 'category') and article.category:
            meta_tags['article_section'] = article.category

    return meta_tags


def generate_article_jsonld(article, base_url='https://grapplingwiki.com'):
    """
    Generate JSON-LD structured data for an article.
    Helps search engines understand article content better.

    Args:
        article (object): Article object with various attributes
        base_url (str): Base URL of the website

    Returns:
        str: JSON-LD script content
    """
    article_url = urljoin(base_url, article.url if hasattr(article, 'url') else f'/article/{article.slug}')

    schema = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': article.title if hasattr(article, 'title') else '',
        'description': article.summary if hasattr(article, 'summary') else '',
        'url': article_url,
        'inLanguage': 'en',
        'publisher': {
            '@type': 'Organization',
            'name': 'GrapplingWiki',
            'url': base_url,
            'logo': {
                '@type': 'ImageObject',
                'url': f'{base_url}/static/images/logo.png'
            }
        }
    }

    # Add author if available
    if hasattr(article, 'author') and article.author:
        author_name = article.author.username if hasattr(article.author, 'username') else str(article.author)
        schema['author'] = {
            '@type': 'Person',
            'name': author_name
        }

    # Add article body if available
    if hasattr(article, 'content') and article.content:
        schema['articleBody'] = article.content[:2000]  # First 2000 chars

    # Add date published
    if hasattr(article, 'created_at') and article.created_at:
        schema['datePublished'] = article.created_at.isoformat()

    # Add date modified
    if hasattr(article, 'updated_at') and article.updated_at:
        schema['dateModified'] = article.updated_at.isoformat()

    # Add image if available
    if hasattr(article, 'image_url') and article.image_url:
        schema['image'] = {
            '@type': 'ImageObject',
            'url': article.image_url
        }

    # Wrap in script tag format
    jsonld_script = f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'

    return jsonld_script

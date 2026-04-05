import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'grappling_wiki.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Wiki settings
    WIKI_NAME = 'GrapplingWiki'
    WIKI_TAGLINE = 'The Free Encyclopedia of Jiu-Jitsu & Grappling'
    WIKI_DESCRIPTION = ('GrapplingWiki is a free, community-driven encyclopedia '
                        'covering all aspects of Brazilian Jiu-Jitsu, submission '
                        'grappling, judo, wrestling, and related martial arts.')
    ARTICLES_PER_PAGE = 25
    RECENT_CHANGES_PER_PAGE = 50

    # SEO
    SITE_URL = os.environ.get('SITE_URL') or 'http://localhost:5000'
    ENABLE_SITEMAP = True

    # User settings
    REGISTRATION_ENABLED = True
    MIN_PASSWORD_LENGTH = 8


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

"""
WTForms for GrapplingWiki application
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, SelectField, SelectMultipleField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, ValidationError,
    Length, Optional, URL, Regexp
)


class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField(
        'Username',
        validators=[
            DataRequired('Username is required'),
            Length(min=3, max=80, message='Username must be 3-80 characters')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired('Password is required')]
    )
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    """Form for user registration"""
    username = StringField(
        'Username',
        validators=[
            DataRequired('Username is required'),
            Length(min=3, max=80, message='Username must be 3-80 characters'),
            Regexp(
                '^[a-zA-Z0-9_-]+$',
                message='Username must contain only letters, numbers, underscores, and hyphens'
            )
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired('Email is required'),
            Email('Invalid email address')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired('Password is required'),
            Length(min=8, message='Password must be at least 8 characters')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired('Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        """Check if username is already taken"""
        # This will be implemented in the application
        pass

    def validate_email(self, email):
        """Check if email is already registered"""
        # This will be implemented in the application
        pass


class ArticleForm(FlaskForm):
    """Form for creating/editing articles"""
    title = StringField(
        'Article Title',
        validators=[
            DataRequired('Article title is required'),
            Length(min=5, max=200, message='Title must be 5-200 characters')
        ]
    )
    content = TextAreaField(
        'Content',
        validators=[
            DataRequired('Article content is required'),
            Length(min=20, message='Article must be at least 20 characters')
        ],
        render_kw={'rows': 20, 'placeholder': 'Write your article in Markdown...', 'data-edit-form': True}
    )
    summary = TextAreaField(
        'Summary',
        validators=[
            Optional(),
            Length(max=500, message='Summary must not exceed 500 characters')
        ],
        render_kw={'rows': 3, 'placeholder': 'Brief summary for search results and preview'}
    )
    category = SelectField(
        'Category',
        validators=[DataRequired('Please select a category')],
        choices=[
            ('technique', 'Technique'),
            ('position', 'Position'),
            ('concept', 'Concept'),
            ('person', 'Notable Person'),
            ('competition', 'Competition'),
            ('glossary', 'Glossary'),
            ('style', 'Grappling Style')
        ]
    )
    tags = StringField(
        'Tags',
        validators=[Optional()],
        render_kw={'placeholder': 'Comma-separated tags (e.g., takedown, submission, defense)'}
    )
    is_published = BooleanField('Publish immediately')
    submit = SubmitField('Save Article')


class EditForm(FlaskForm):
    """Form for editing article content"""
    content = TextAreaField(
        'Content',
        validators=[
            DataRequired('Article content is required'),
            Length(min=20, message='Article must be at least 20 characters')
        ],
        render_kw={'rows': 20, 'placeholder': 'Edit your article in Markdown...', 'data-edit-form': True}
    )
    edit_summary = StringField(
        'Edit Summary',
        validators=[
            Optional(),
            Length(max=200, message='Edit summary must not exceed 200 characters')
        ],
        render_kw={'placeholder': 'What did you change? (optional)'}
    )
    submit = SubmitField('Save Changes')


class DiscussionForm(FlaskForm):
    """Form for creating discussion threads"""
    title = StringField(
        'Discussion Title',
        validators=[
            DataRequired('Title is required'),
            Length(min=5, max=200, message='Title must be 5-200 characters')
        ]
    )
    content = TextAreaField(
        'Discussion',
        validators=[
            DataRequired('Please write something'),
            Length(min=10, message='Discussion must be at least 10 characters')
        ],
        render_kw={'rows': 10, 'placeholder': 'Start a discussion...'}
    )
    submit = SubmitField('Create Discussion')


class ReplyForm(FlaskForm):
    """Form for replying to discussions"""
    content = TextAreaField(
        'Reply',
        validators=[
            DataRequired('Please write a reply'),
            Length(min=1, max=5000, message='Reply must be 1-5000 characters')
        ],
        render_kw={'rows': 6, 'placeholder': 'Write your reply...'}
    )
    submit = SubmitField('Post Reply')


class SearchForm(FlaskForm):
    """Form for searching articles"""
    query = StringField(
        'Search',
        validators=[
            DataRequired('Please enter a search term'),
            Length(min=1, max=100, message='Search term must be 1-100 characters')
        ],
        render_kw={'placeholder': 'Search articles...'}
    )
    submit = SubmitField('Search')


class UserProfileForm(FlaskForm):
    """Form for updating user profile"""
    username = StringField(
        'Username',
        validators=[
            DataRequired('Username is required'),
            Length(min=3, max=80, message='Username must be 3-80 characters'),
            Regexp(
                '^[a-zA-Z0-9_-]+$',
                message='Username must contain only letters, numbers, underscores, and hyphens'
            )
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired('Email is required'),
            Email('Invalid email address')
        ]
    )
    bio = TextAreaField(
        'Bio',
        validators=[Optional(), Length(max=500, message='Bio must not exceed 500 characters')],
        render_kw={'rows': 4, 'placeholder': 'Tell us about yourself...'}
    )
    website = StringField(
        'Website',
        validators=[Optional(), URL('Invalid URL')],
        render_kw={'placeholder': 'https://example.com'}
    )
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    """Form for changing password"""
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired('Current password is required')]
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired('New password is required'),
            Length(min=8, message='Password must be at least 8 characters')
        ]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired('Please confirm your new password'),
            EqualTo('new_password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Change Password')


class CommentForm(FlaskForm):
    """Form for adding comments to articles"""
    content = TextAreaField(
        'Comment',
        validators=[
            DataRequired('Please write a comment'),
            Length(min=1, max=2000, message='Comment must be 1-2000 characters')
        ],
        render_kw={'rows': 4, 'placeholder': 'Add a comment...'}
    )
    submit = SubmitField('Post Comment')


class FilterForm(FlaskForm):
    """Form for filtering articles"""
    category = SelectField(
        'Category',
        choices=[('', 'All Categories')] + [
            ('technique', 'Technique'),
            ('position', 'Position'),
            ('concept', 'Concept'),
            ('person', 'Notable Person'),
            ('competition', 'Competition'),
            ('glossary', 'Glossary'),
            ('style', 'Grappling Style')
        ],
        validators=[Optional()]
    )
    sort_by = SelectField(
        'Sort By',
        choices=[
            ('recent', 'Most Recent'),
            ('popular', 'Most Popular'),
            ('title', 'Title A-Z'),
            ('updated', 'Recently Updated')
        ],
        validators=[Optional()]
    )
    submit = SubmitField('Filter')


class AdminForm(FlaskForm):
    """Form for admin operations"""
    action = SelectField(
        'Action',
        choices=[
            ('delete', 'Delete'),
            ('publish', 'Publish'),
            ('unpublish', 'Unpublish'),
            ('feature', 'Feature'),
            ('unfeature', 'Unfeature'),
            ('lock', 'Lock'),
            ('unlock', 'Unlock')
        ],
        validators=[DataRequired('Please select an action')]
    )
    reason = TextAreaField(
        'Reason',
        validators=[Optional(), Length(max=500, message='Reason must not exceed 500 characters')],
        render_kw={'rows': 3, 'placeholder': 'Reason for this action (optional)'}
    )
    submit = SubmitField('Apply Action')

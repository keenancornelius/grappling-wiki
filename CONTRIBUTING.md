# Contributing to GrapplingWiki

Welcome! This guide will get you from zero to making your first contribution, even if you've never used Git before.

## Prerequisites

You need two things installed on your computer:

1. **Git** — the version control tool
2. **Python 3.11+** — the programming language

### Installing Git

**Mac:** Open Terminal and run `git --version`. If it's not installed, macOS will prompt you to install it. Or install via Homebrew: `brew install git`

**Windows:** Download from https://git-scm.com/download/win and run the installer. Use the default settings. This gives you "Git Bash" which works like a terminal.

**Linux:** `sudo apt install git` (Ubuntu/Debian) or `sudo dnf install git` (Fedora)

### First-Time Git Setup

After installing, tell Git who you are (this shows up on your contributions):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Getting the Code

### Step 1: Fork the repository

1. Go to the GitHub repo page
2. Click the **Fork** button (top right)
3. This creates your own copy of the project under your GitHub account

### Step 2: Clone your fork

```bash
# Replace YOUR_USERNAME with your GitHub username
git clone https://github.com/YOUR_USERNAME/grappling-wiki.git
cd grappling-wiki
```

### Step 3: Add the original repo as "upstream"

This lets you pull in changes other people make:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/grappling-wiki.git
```

### Step 4: Set up your development environment

```bash
# Create a virtual environment (keeps dependencies isolated)
python -m venv venv

# Activate it
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run the wiki locally
python run.py
```

Visit http://localhost:5000 — you should see GrapplingWiki running locally!

## Making Changes

### The Branch Workflow

Never work directly on `main`. Always create a branch:

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull upstream main

# Create a new branch for your work
# Name it after the stream and what you're doing:
git checkout -b stream-f/add-takedown-glossary
```

Branch naming convention: `stream-X/short-description`

Examples:
- `stream-b/add-watchlist-model`
- `stream-d/fix-mobile-nav`
- `stream-f/add-submission-glossary`
- `stream-c/edit-conflict-detection`

### Making Commits

As you work, save your progress with commits:

```bash
# See what files you changed
git status

# Add the files you want to commit
git add app/models/article.py
git add app/templates/wiki/view.html
# Or add everything: git add .

# Commit with a descriptive message
git commit -m "[Stream B] Add watchlist model for article change tracking"
```

Commit message format: `[Stream X] Short description of what you did`

### Pushing Your Branch

When you're ready to share your work:

```bash
# Push your branch to YOUR fork on GitHub
git push origin stream-f/add-takedown-glossary
```

### Creating a Pull Request

1. Go to your fork on GitHub
2. You'll see a banner saying "Compare & pull request" — click it
3. Write a description of what you changed and why
4. Click **Create pull request**

Someone will review your changes and either approve them or ask for adjustments. Once approved, your changes get merged into the main project!

## Staying Up to Date

Other people will be making changes too. Keep your local copy current:

```bash
# Switch to main
git checkout main

# Pull the latest changes from the original repo
git pull upstream main

# Push the updates to your fork
git push origin main

# If you're working on a branch, update it too:
git checkout stream-f/my-feature
git rebase main
```

## Project Structure Quick Reference

| What you want to do | Where to look |
|---|---|
| Change how data is stored | `app/models/` |
| Change page behavior/logic | `app/routes/` |
| Change how pages look | `app/templates/` |
| Change styles | `app/static/css/style.css` |
| Change client-side behavior | `app/static/js/wiki.js` |
| Add glossary content | `content/glossary/` |
| Change forms | `app/forms.py` |
| Change SEO features | `app/utils/seo.py` |

## Task Streams

Check `CLAUDE.md` for the full list of task streams (A through G). Each stream has a checklist of work to be done. Pick a stream, claim a task, and create a branch for it.

Quick overview:
- **Stream A** — DevOps, CI/CD, deployment
- **Stream B** — Database models, migrations, seed data
- **Stream C** — Routes, views, business logic
- **Stream D** — Frontend, templates, UX
- **Stream E** — SEO and content discovery
- **Stream F** — Content architecture, glossary writing
- **Stream G** — Community features, moderation

## Common Git Commands Cheat Sheet

```bash
git status              # See what's changed
git add <file>          # Stage a file for commit
git add .               # Stage all changes
git commit -m "msg"     # Commit staged changes
git push origin <branch> # Push branch to your fork
git pull upstream main  # Get latest from main project
git checkout <branch>   # Switch to a branch
git checkout -b <name>  # Create and switch to new branch
git log --oneline -10   # See recent commits
git diff                # See unstaged changes
git stash               # Temporarily save uncommitted changes
git stash pop           # Restore stashed changes
```

## Getting Help

- Check `CLAUDE.md` for project architecture details
- Open a GitHub Issue if you find a bug or have a question
- Tag your issues with the relevant stream label (e.g., `stream-b`, `stream-d`)

## Code Style

- Python: Follow PEP 8. Use `black` for formatting, `flake8` for linting
- Templates: Use Jinja2 escaping. Always include CSRF tokens on forms
- CSS: Mobile-first. Use the existing class naming patterns
- Commits: `[Stream X] Description` format
- Tests: Write tests for new routes and model methods

Thank you for contributing to GrapplingWiki! Every contribution helps build the most comprehensive grappling resource on the internet.

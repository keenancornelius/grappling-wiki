"""
Seed script: create the Miha Perhavec article.
Run from project root: python scripts/seed_miha.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Article, ArticleRevision, Category

ARTICLE = {
    "title": "Miha Perhavec",
    "slug": "miha-perhavec",
    "category": "person",
    "summary": "Slovenian-born grappling polymath, Polaris veteran, best-selling author, and co-founder of Legion American Jiu-Jitsu — one of the most complete grapplers of his generation.",
    "content": """## Overview

Miha Perhavec is a Slovenian judo and jiu-jitsu black belt, professional grappling competitor, published author, and co-founder of Legion American Jiu-Jitsu in San Diego, California. With over two decades of grappling experience spanning judo, MMA, and submission grappling, Perhavec represents a rare breed in the modern era — a competitor whose technical depth is matched only by his ability to articulate it. His book *Modern Submission Grappling: A No-Gi Jiu-Jitsu Manual* and its companion video course have established him as one of the foremost educators in no-gi grappling, and his competition record across multiple formats and continents speaks to a career built on relentless refinement.

Few people in the grappling world have lived as many lives on the mat as Miha Perhavec. Judo black belt at sixteen. Undefeated MMA streak. IBJJF medalist across Europe. Polaris submission machine. Best-selling author. And through all of it, a quiet, methodical approach to the craft that makes him one of the most respected minds in the room at Legion San Diego — or anywhere else he steps on the mat.

## Early Life and Judo Career

Perhavec was born and raised in Kranj, Slovenia, a small city nestled at the foot of the Julian Alps. He began training judo around the age of nine or ten and quickly showed promise in a country with a proud judo tradition. Slovenia has produced five Olympic judo medals since 2004, including two golds, and the young Perhavec trained alongside future Olympic medalists during his formative years.

The Slovenian national judo system is rigorous and technically demanding, and it forged in Perhavec a deep understanding of grips, off-balancing (kuzushi), and throwing mechanics that would later become a defining feature of his grappling style. He earned his first-degree judo black belt at just sixteen years old — an achievement that speaks to both his technical ability and his competitive maturity at a young age.

Despite training at an elite level and having a clear path in competitive judo, Perhavec eventually grew disillusioned with the sport. The constant rule changes that increasingly restricted ground work and leg attacks made judo feel, in his view, like a less complete martial art than it had been. He wanted to grapple without arbitrary limitations on where the fight could go.

## MMA Career

At eighteen, Perhavec walked into a local MMA gym and found the next chapter. His judo base gave him an immediate advantage — the throws translated, the scrambles felt natural, and his ground control was already ahead of most beginners. He compiled an amateur MMA record of 11-1, with eleven first-round finishes, the vast majority by submission. The record tells you everything about how he fought: get the takedown, find the neck or the arm, finish fast.

But MMA was ultimately a stepping stone. The grappling was what pulled him, and the emerging world of professional submission-only competition offered something MMA could not — a pure test of grappling skill without the variables of strikes and rounds.

## The Nomadic Years

Perhavec's jiu-jitsu journey required leaving Slovenia, where the competition scene was small and training partners were limited. What followed was a period of itinerant training that took him across Europe — living and competing out of Warsaw, Poland; Oslo, Norway; and Dublin, Ireland. In each city he sought out the best rooms he could find, absorbed local styles, and sharpened his game against different body types and tactical approaches.

This nomadic period was formative. Competing across the IBJJF European circuit, Perhavec amassed five IBJJF No-Gi European Open medals, including three silvers, and earned Double Gold at multiple IBJJF Open tournaments. He was not just collecting hardware — he was building the kind of broad, adaptable game that only comes from rolling with strangers in unfamiliar gyms in unfamiliar countries.

His travels eventually brought him to Los Angeles for the IBJJF World Championships and to Abu Dhabi for the sport's most prestigious events, competing against the best grapplers on the planet.

## Polaris and Professional Competition

Perhavec made his name on the international stage through Polaris, the UK-based professional submission grappling promotion. His Polaris record is a statement of intent: 3-1 overall, with a perfect 3-0 record in the Polaris Pro middleweight division and a 100% submission rate — every single win coming by leg lock.

In an era when leg locks were transitioning from niche weapons to mainstream necessities, Perhavec was already finishing world-class opponents with them under bright lights and professional rules. His only Polaris loss came against 10th Planet standout Richie "Boogeyman" Martinez, who caught a deep rear naked choke in under a minute at Polaris 10 — the kind of quick exchange that can happen between two aggressive finishers.

Beyond Polaris, Perhavec competed on Who's Number One and other professional grappling cards, consistently testing himself against elite competition.

## Partnership with Keenan Cornelius and Legion AJJ

The defining partnership of Perhavec's career began when he connected with Keenan Cornelius. The two recognized a shared philosophy — technical depth over athleticism, systematic thinking over random drilling, and a belief that grappling instruction could be better than what the industry was offering.

In late 2019, Perhavec relocated to San Diego at Cornelius's invitation. Together, they co-founded Legion American Jiu-Jitsu, building the academy from the ground up into one of the most respected training environments in Southern California. Perhavec's role at Legion extends beyond co-owner — he is a lead instructor whose classes reflect his systematic, detail-oriented approach to the art.

On January 19, 2021, Cornelius awarded Perhavec his jiu-jitsu black belt — the first black belt promotion in Legion AJJ's history. It was a milestone that recognized not just Perhavec's technical skill, but the depth of his competitive resume and his contributions to the team's culture.

## Modern Submission Grappling: The Book

After more than eighteen months of writing and development, Perhavec published *Modern Submission Grappling: A No-Gi Jiu-Jitsu Manual* in August 2024. The book became a best-seller and filled a gap that had existed in grappling literature for years — a comprehensive, systematically organized manual covering the entire no-gi game from a modern competitive perspective.

Where most instructional content in grappling lives in video format and teaches techniques in isolation, Perhavec's book presents grappling as an interconnected system. The writing reflects his background: precise, organized, and structured like someone who has spent years thinking about how to teach complex physical concepts through language.

## The No-Gi Video Manual

Complementing the book, Perhavec produced the *No-Gi Video Manual* — a ten-hour instructional course that walks through the complete no-gi curriculum in nine chapters. The course covers standup and takedowns (drawing heavily on his judo expertise), guard play and guard passing, dominant position control and defense, upper and lower body submissions, and detailed leg lock systems.

The course also includes bonus judo instructional modules, flowcharts for positional decision-making, and a companion discussion community. Additional standalone courses on JiuJitsuX cover specialized topics like the Major Inner Reaper and Major Outer Reaper (Osoto Gari) — judo throws adapted for no-gi grappling.

## Teaching Philosophy

Perhavec's approach to instruction is defined by clarity and structure. His judo training instilled a respect for fundamentals and proper mechanics, while his years of competing across Europe gave him an appreciation for adaptability and problem-solving. He teaches grappling as a system of interconnected positions and decisions rather than a collection of isolated techniques.

At Legion San Diego, his classes are known for their depth — the kind of sessions where a single concept might be explored from multiple angles over an hour, with each variation building on the last. Students describe his teaching as methodical, patient, and unusually good at explaining the *why* behind the *what*.

## Competition Highlights

- Judo black belt (1st degree) — earned at age 16 in Slovenia
- Jiu-jitsu black belt (1st degree) — first black belt promoted by Keenan Cornelius at Legion AJJ (January 2021)
- 5 IBJJF No-Gi European Open medals, including 3 silvers
- Multiple IBJJF Open Double Gold finishes
- Polaris Pro: 3-0 in middleweight division, 100% submission rate (all leg locks)
- Overall Polaris record: 3-1
- Amateur MMA record: 11-1 (11 first-round finishes)
- IBJJF World Championships competitor
- Who's Number One competitor

## Publications and Instructionals

- *Modern Submission Grappling: A No-Gi Jiu-Jitsu Manual* (book, August 2024)
- *No-Gi Video Manual* — 10-hour comprehensive course (jiujitsumanual.com)
- *Major Inner Reaper* — judo throw instructional (JiuJitsuX)
- *Major Outer Reaper (Osoto Gari)* — judo throw instructional (JiuJitsuX)

## Personal

Perhavec currently lives and trains in San Diego, California, where he serves as co-owner and lead instructor at Legion American Jiu-Jitsu alongside Keenan Cornelius. He continues to compete, teach, and develop instructional content.

## See Also

- Keenan Cornelius
- Legion American Jiu-Jitsu
- Leg Locks
- Judo
- Polaris (Competition)
- No-Gi Grappling
"""
}


def seed():
    app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
    with app.app_context():
        # Get admin user (try 'keenan' first, then 'admin', then any user)
        admin = User.query.filter_by(username='keenan').first()
        if not admin:
            admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User.query.filter_by(username='GrapplingWiki').first()
        if not admin:
            admin = User.query.first()
        if not admin:
            print("No user found. Create one first.")
            return

        # Get or create Person category
        cat = Category.query.filter_by(slug=ARTICLE['category']).first()
        if not cat:
            cat = Category(
                name=ARTICLE['category'].title(),
                slug=ARTICLE['category'],
                description='Practitioners, instructors, competitors, and pioneers.'
            )
            db.session.add(cat)
            db.session.flush()

        # Check if article exists
        existing = Article.query.filter_by(slug=ARTICLE['slug']).first()
        if existing:
            print(f"Article '{ARTICLE['title']}' already exists — updating content.")
            existing.content = ARTICLE['content']
            existing.summary = ARTICLE['summary']
            existing.category_id = cat.id

            # Add new revision
            latest = existing.revisions.order_by(ArticleRevision.revision_number.desc()).first()
            rev_num = (latest.revision_number + 1) if latest else 1
            revision = ArticleRevision(
                article_id=existing.id,
                editor_id=admin.id,
                content=ARTICLE['content'],
                edit_summary='Updated article content',
                revision_number=rev_num
            )
            db.session.add(revision)
            db.session.commit()
            print(f"Updated '{ARTICLE['title']}' (revision #{rev_num}).")
            return

        # Create new article
        article = Article(
            title=ARTICLE['title'],
            slug=ARTICLE['slug'],
            content=ARTICLE['content'],
            summary=ARTICLE['summary'],
            author_id=admin.id,
            category_id=cat.id,
            category=cat.slug,
            is_published=True,
        )
        db.session.add(article)
        db.session.flush()

        # Initial revision
        revision = ArticleRevision(
            article_id=article.id,
            editor_id=admin.id,
            content=ARTICLE['content'],
            edit_summary='Initial article creation',
            revision_number=1
        )
        db.session.add(revision)
        db.session.commit()
        print(f"Created '{ARTICLE['title']}' ({ARTICLE['slug']})")


if __name__ == '__main__':
    seed()

"""
Seed script: populate the wiki with foundational grappling articles.
Run from project root: python scripts/seed_articles.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Article, ArticleRevision, Tag

TAGS = [
    ("Technique", "technique", "Submissions, sweeps, passes, escapes, takedowns, and other individual moves."),
    ("Position", "position", "Guards, pins, dominant positions, and transitional states."),
    ("Concept", "concept", "Principles, strategies, theories, and mental models for grappling."),
    ("Person", "person", "Practitioners, instructors, competitors, and pioneers of the grappling arts."),
    ("Competition", "competition", "Tournaments, rulesets, organizations, and competitive events."),
    ("Style", "style", "Martial arts disciplines and grappling systems."),
]

ARTICLES = [
    {
        "title": "Rear Naked Choke",
        "slug": "rear-naked-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "The most dominant submission in grappling — a blood choke applied from the back.",
        "content": """## Overview

The rear naked choke (RNC) is a blood choke applied from behind an opponent, targeting both carotid arteries to restrict blood flow to the brain. It is considered the highest-percentage submission in competitive grappling and mixed martial arts, largely because the attacker applies it from the back — the single most dominant position in the sport.

The technique requires no gi grips and works identically in gi and no-gi competition, making it universally applicable across all grappling disciplines.

## Mechanics

The attacker wraps one arm around the opponent's neck, placing the crook of the elbow directly under the chin. The choking arm grabs the bicep of the free arm, and the free hand is placed behind the opponent's head. By squeezing the arms together and driving the head forward, pressure is applied to both sides of the neck simultaneously.

The choke works by compressing the carotid arteries rather than the trachea, making it a blood choke rather than an air choke. A properly applied RNC can render an opponent unconscious in as little as 3-5 seconds.

## Key Details

The most common error is allowing the opponent to tuck their chin, which forces the forearm across the jaw or trachea rather than the neck. Experienced grapplers address this by first establishing a body triangle or strong seatbelt grip, then working to clear the chin using the blade of the forearm, forehead pressure, or transitioning to a short choke.

## Entries

The RNC is most commonly entered from back control, but can also be applied from:

- Turtle position (as a rolling back take)
- Side control transitions
- Standing back clinch
- Front headlock snap-backs

## Competition Results

The rear naked choke is statistically the most successful submission in UFC history and is among the top finishing techniques at ADCC. Its dominance across rulesets and weight classes makes it one of the first techniques taught to beginners and one of the last techniques masters are still refining.

## Related Techniques

See also: Back Control, Body Triangle, Seatbelt Grip, Short Choke, Mata Leão
"""
    },
    {
        "title": "Closed Guard",
        "slug": "closed-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "The foundational bottom position in Brazilian Jiu-Jitsu, where the guard player locks their legs around the opponent's waist.",
        "content": """## Overview

Closed guard is a ground fighting position where the bottom grappler wraps their legs around the opponent's torso, locking their ankles behind the opponent's back. It is one of the most fundamental positions in Brazilian Jiu-Jitsu and serves as the starting point for an enormous variety of attacks, sweeps, and transitions.

Despite being a bottom position, closed guard is considered offensive — the guard player controls the distance, posture, and pace of the exchange.

## History

Closed guard became central to BJJ's identity through the Gracie family's development of the art. Royce Gracie famously used closed guard to control and submit much larger opponents in the early UFC events, demonstrating that a skilled guard player could neutralize size and strength advantages from their back.

## Attacking from Closed Guard

The closed guard offers a diverse set of submissions and sweeps:

**Submissions:** Armbar, Triangle Choke, Guillotine, Omoplata, Kimura, Cross Collar Choke (gi)

**Sweeps:** Hip Bump Sweep, Scissor Sweep, Flower Sweep, Pendulum Sweep

**Transitions:** Open guard variations, rubber guard, high guard for armbar setups

## Defending in Closed Guard

The top player's primary objectives are to maintain posture, prevent the guard player from breaking their alignment, and work to open the guard (separate the locked ankles). Common guard-opening techniques include standing up in guard, knee-in-the-tailbone pressure, and log-splitter grips.

## Strategic Concepts

The fundamental battle in closed guard is posture versus posture-breaking. When the guard player breaks the top player's posture (pulls them down), attacks become available. When the top player maintains upright posture, they can begin working to pass.

Grip fighting is critical — whoever controls the grips controls the exchange.

## Related

See also: Open Guard, Half Guard, Armbar, Triangle Choke, Hip Bump Sweep
"""
    },
    {
        "title": "Mount",
        "slug": "mount",
        "category": "position",
        "tags": ["Position"],
        "summary": "The most dominant top position in grappling, sitting on top of a supine opponent.",
        "content": """## Overview

Mount (also called full mount) is a dominant ground position where one grappler sits on top of the other's torso, with knees on either side. It is widely considered the single most dominant position in grappling, offering the top player a massive mechanical advantage for strikes and submissions while severely limiting the bottom player's options.

In the positional hierarchy, mount sits just below back control as the most advantageous position. In IBJJF competition, achieving mount awards 4 points.

## Variations

**Low Mount:** The rider sits low on the opponent's hips. Good for maintaining the position and setting up submissions. The bottom player has more space to create frames.

**High Mount:** The rider climbs their knees toward the opponent's armpits. Extremely dominant — limits the bottom player's arm movement and opens direct submission threats. Often the endgame configuration before finishing.

**S-Mount:** One leg is posted up near the head while the other knee remains on the ground. Creates an angle for armbar finishes and is very difficult to escape.

**Technical Mount:** One leg hooks under the opponent while the other posts. A transitional variant often used when the bottom player turns to their side, creating a pathway to the back.

## Attacks

Mount provides access to some of the highest-percentage submissions in grappling: armbar, cross collar choke, Americana, Ezekiel choke, mounted triangle, and arm triangle setups. The constant threat of multiple attacks forces the bottom player into defensive postures that create further openings.

## Escapes

The two fundamental mount escapes are the trap-and-roll (upa) and the elbow-knee escape (shrimping). Both require precise timing and technique, as the mounted player is fighting against gravity, body weight, and often an opponent actively hunting submissions.

## Related

See also: Back Control, Side Control, Armbar, Americana, Ezekiel Choke
"""
    },
    {
        "title": "Armbar",
        "slug": "armbar",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A joint lock that hyperextends the elbow by isolating the arm between the legs and hips.",
        "content": """## Overview

The armbar (juji gatame) is a joint lock submission that hyperextends the opponent's elbow. The attacker isolates one of the opponent's arms, controls it between their legs, and applies upward hip pressure against the elbow joint while pulling the wrist downward. It is one of the most versatile and commonly used submissions across all grappling arts.

The armbar can be applied from nearly every position — mount, guard, side control, back control, and even standing — making it one of the first submissions taught to beginners and one of the most studied techniques at the highest levels.

## Mechanics

The key mechanical principles of the armbar are:

**Arm isolation:** The attacker must control the opponent's arm, typically by hugging it to their chest with the thumb pointing up.

**Hip placement:** The hips must be positioned tight against the opponent's shoulder/upper arm, creating a fulcrum point at the elbow.

**Leg control:** Both legs cross over the opponent's body — one across the face/chest to prevent posturing, one across the torso to anchor the position.

**Breaking mechanics:** The attacker lifts their hips into the elbow while pulling the wrist toward their chest. The combined forces hyperextend the joint.

## Common Setups

**From mount:** The attacker threatens a choke, forcing the opponent to defend with their hands. As a hand extends to push or frame, the attacker isolates the arm, pivots, and swings into the armbar.

**From closed guard:** The attacker controls posture, establishes a high guard, pivots their hips to angle off, clears the head with one leg, and extends the arm.

**From side control:** The attacker steps over the head from side control, often using a kimura grip to isolate the arm before transitioning to the armbar.

## Defense

The primary defenses against the armbar are: stacking (driving forward to compress the attacker), hitchhiker escape (rolling toward the thumb to relieve pressure), and grip fighting (clasping the hands together to prevent arm extension). Each defense has specific counters, creating a deep chain of technique and counter-technique.

## Competition

The armbar is one of the most successful submissions in competitive history across judo, BJJ, and MMA. Roger Gracie, widely considered the greatest BJJ competitor of all time, built his competition career around the armbar from mount.

## Related

See also: Mount, Closed Guard, Kimura, Triangle Choke, Omoplata
"""
    },
    {
        "title": "Guard Passing",
        "slug": "guard-passing",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The art of navigating past an opponent's legs to achieve a dominant position.",
        "content": """## Overview

Guard passing is the discipline of moving past an opponent's legs from a top position to achieve side control, mount, or another dominant position. It is one of the most complex and strategically rich aspects of grappling, requiring a blend of pressure, timing, speed, and technical knowledge.

In competitive BJJ, passing the guard awards 3 points. But beyond the scoreboard, guard passing represents the top player's primary pathway to finishing the fight — most high-percentage submissions require a dominant position that can only be reached by first clearing the legs.

## Passing Philosophies

Guard passing can be broadly categorized into three philosophical approaches:

**Pressure passing** relies on bodyweight, hip pressure, and grinding through the guard. The passer aims to flatten the guard player, eliminate their hip movement, and slowly work past the legs. Techniques include over-under pass, smash pass, and body lock passing. This style favors larger, heavier grapplers but is effective at all levels.

**Speed passing** uses explosive movement and timing to blow past the guard before the guard player can establish grips or frames. Techniques include toreando, leg drag, and X-pass. This style favors athletic grapplers with good reaction time.

**Misdirection passing** combines feints and chain attacks — threatening one pass to set up another. The passer reads the guard player's reactions and exploits the openings created by their defenses. This represents the most advanced and conceptually rich approach.

## Key Principles

Regardless of style, all successful guard passing shares certain principles:

**Control the hips.** If you control where the opponent's hips can move, you control the guard. Pin them to the mat, elevate them, or angle them away.

**Eliminate frames.** The guard player survives by creating structural barriers (frames) with their arms and legs. Stripping or bypassing these frames is essential.

**Maintain pressure.** Giving the guard player space to reguard is the most common passing mistake. Stay heavy, stay tight, stay connected.

**Pass to a position, not through a position.** Know where you want to end up before you start. Passing without a destination leads to scrambles.

## Related

See also: Closed Guard, Half Guard, Side Control, Toreando, Leg Drag
"""
    },
    {
        "title": "Marcelo Garcia",
        "slug": "marcelo-garcia",
        "category": "person",
        "tags": ["Person"],
        "summary": "Five-time ADCC champion and widely regarded as one of the greatest no-gi grapplers in history.",
        "content": """## Overview

Marcelo Garcia is a Brazilian Jiu-Jitsu black belt and competitive grappler widely considered one of the greatest of all time, particularly in no-gi competition. He is a five-time ADCC world champion, four-time IBJJF world champion, and the founder of the Marcelo Garcia Academy in New York City.

What distinguished Garcia from his contemporaries was not just his competitive record but the way he won — with a style defined by creativity, aggression, and a willingness to fight from positions other competitors avoided.

## Competitive Career

Garcia's ADCC record is among the most impressive in the history of the sport. Competing primarily at the 77kg and 88kg weight classes, he defeated opponents far larger than himself through superior technique and relentless offensive pressure.

His signature techniques became the blueprint for modern no-gi grappling: the arm drag to back take, the guillotine choke from every angle, the butterfly guard sweep game, and the north-south choke.

## Style and Innovations

Garcia's game was built around several core principles that influenced an entire generation of grapplers:

**The arm drag.** Garcia elevated the arm drag from a simple wrestling technique to the centerpiece of a complete back-taking system. His seated arm drag became the most imitated technique in competitive no-gi grappling.

**Butterfly guard.** While butterfly guard existed before Garcia, his systematic approach to sweeping and transitioning from the position redefined how the guard was used offensively.

**Guillotine choke.** Garcia's guillotine — particularly his marcelotine variation — became one of the most feared front headlock attacks in the sport.

**X-guard.** Although not the inventor of X-guard, Garcia was instrumental in developing and popularizing the position at the highest levels of competition.

## Legacy

Beyond competition, Garcia's impact includes his academy (which produced multiple world champions), his pioneering approach to online instruction through MGinAction, and his reputation for sportsmanship and openness in sharing technique. He is frequently cited by professional grapplers as the single most influential figure in modern no-gi jiu-jitsu.

## Related

See also: ADCC, Butterfly Guard, X-Guard, Arm Drag, Guillotine
"""
    },
    {
        "title": "ADCC",
        "slug": "adcc",
        "category": "competition",
        "tags": ["Competition"],
        "summary": "The Abu Dhabi Combat Club Submission Wrestling World Championship — grappling's most prestigious no-gi tournament.",
        "content": """## Overview

The Abu Dhabi Combat Club Submission Wrestling World Championship (commonly known as ADCC) is widely regarded as the most prestigious submission grappling tournament in the world. Founded in 1998 by Sheikh Tahnoun bin Zayed Al Nahyan of the United Arab Emirates, ADCC brings together elite grapplers from Brazilian Jiu-Jitsu, wrestling, judo, sambo, and other grappling disciplines to compete under a unified no-gi ruleset.

The tournament is held biennially and features invite-only competitors alongside regional trial winners, creating a field that consistently represents the absolute highest level of submission grappling on earth.

## Ruleset

ADCC's ruleset is designed to encourage submission-seeking and penalize passivity. Key rules include:

**Overtime structure:** Matches begin with a regulation period where points are not scored — only submissions win. If no submission occurs, an overtime period begins where points are awarded. This structure incentivizes attacking in regulation when there is nothing to lose from a scoring perspective.

**Point system:** In overtime, points are awarded for takedowns (2 points), sweeps (2 points), passing guard (3 points), mount (2 points), back mount (3 points), and knee on belly (2 points). Negative points are given for pulling guard.

**No advantages:** Unlike IBJJF, there are no advantage points. This eliminates conservative strategies built around edge cases in scoring.

## Weight Classes

ADCC features weight classes for both men and women, plus an absolute (open weight) division. The absolute division is considered the ultimate test — where a 66kg competitor might face a 99kg opponent, and technique must overcome size.

## History and Significance

ADCC has served as the proving ground for many of the greatest grapplers in history. Multiple-time champions include Marcelo Garcia, Andre Galvao, and Gordon Ryan. The tournament has been the venue for some of the most memorable matches in grappling history and continues to set the standard for competitive excellence in the sport.

## Related

See also: Marcelo Garcia, IBJJF Worlds, Submission Grappling, No-Gi Grappling
"""
    },
    {
        "title": "Brazilian Jiu-Jitsu",
        "slug": "brazilian-jiu-jitsu",
        "category": "style",
        "tags": ["Style"],
        "summary": "A ground-fighting martial art descended from judo, emphasizing positional control and submission techniques.",
        "content": """## Overview

Brazilian Jiu-Jitsu (BJJ) is a martial art and combat sport that focuses on ground fighting, positional control, and submission techniques including joint locks and chokes. Developed in Brazil in the early 20th century by the Gracie family from the Japanese art of Kodokan judo, BJJ has become one of the most widely practiced martial arts in the world and a foundational component of mixed martial arts training.

The central thesis of BJJ is that a smaller, weaker person can successfully defend against a larger, stronger assailant by using leverage, technique, and positional strategy — particularly by taking the fight to the ground where size advantages are reduced.

## History

BJJ traces its origins to Mitsuyo Maeda, a Japanese judoka and prizefighter who emigrated to Brazil in 1914. Maeda taught judo (then often called "jiu-jitsu") to Carlos Gracie, who along with his brothers — most notably Helio Gracie — adapted and refined the techniques with an emphasis on ground fighting and submissions.

Over decades, the Gracie family developed a distinct system that diverged significantly from its judo origins, placing greater emphasis on guard work, positional hierarchy, and the ability to fight effectively from the back. The art was relatively unknown outside Brazil until Royce Gracie's dominant performances in the early Ultimate Fighting Championship events (1993-1994), which demonstrated BJJ's effectiveness against practitioners of other martial arts.

## Technical Framework

BJJ is organized around a positional hierarchy, from most dominant to least dominant: back control, mount, knee on belly, side control, half guard, and various open guard positions. The practitioner's goal is either to advance to a more dominant position (from top) or to sweep and submit (from bottom).

The art encompasses hundreds of techniques across these positions, with new innovations continuing to emerge through competition. Modern BJJ has expanded to include sophisticated leg lock systems, wrestling-integrated approaches, and highly specialized guard positions.

## Competition

BJJ competition occurs in both gi and no-gi formats. The International Brazilian Jiu-Jitsu Federation (IBJJF) governs the largest gi competitions, while ADCC is the premier no-gi event. The belt ranking system (white, blue, purple, brown, black) provides a progression framework unique among grappling arts.

## Related

See also: Judo, ADCC, IBJJF Worlds, Closed Guard, Mount, Helio Gracie
"""
    },
    {
        "title": "Half Guard",
        "slug": "half-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A versatile guard position where the bottom player controls one of the top player's legs between their own.",
        "content": """## Overview

Half guard is a ground position where the bottom grappler has one of the top player's legs trapped between their own legs, while the top player has partially passed the guard. Once considered a transitional or inferior position, half guard has evolved into one of the most strategically rich and actively played guards in modern BJJ.

The position exists on a spectrum — from a nearly-passed defensive posture to an aggressive attacking platform, depending on the bottom player's frames, underhooks, and body angle.

## Variations

**Knee Shield (Z-Guard):** The bottom player places their shin across the top player's torso, creating a frame that manages distance and prevents the passer from flattening them. One of the most common and effective half guard configurations.

**Deep Half Guard:** The bottom player dives underneath the top player, positioning themselves below their center of gravity. Despite appearing disadvantageous, deep half offers powerful sweeps because the bottom player controls the top player's base from directly beneath them.

**Lockdown:** Popularized by Eddie Bravo, the lockdown uses a figure-four leg configuration to trap the top player's leg. Combined with the "whip-up" motion, it creates sweeping opportunities and disrupts the top player's base.

**Half Butterfly:** The bottom player inserts a butterfly hook with their free leg while maintaining the half guard with the other. This hybrid position combines the control of half guard with the sweeping power of butterfly guard.

## Strategic Principles

The essential battle in half guard revolves around the underhook. If the bottom player wins the underhook (arm under the top player's armpit), they can build to their knees, sweep, or take the back. If the top player wins the underhook, they can crossface, flatten the bottom player, and begin passing.

Framing is equally critical. The bottom player must prevent being flattened — once flat on their back with no frames, half guard becomes a passing position rather than a guard.

## Related

See also: Closed Guard, Butterfly Guard, Deep Half Guard, Knee Shield, Underhooks
"""
    },
    {
        "title": "Frames and Framing",
        "slug": "frames-and-framing",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The defensive principle of using skeletal structure rather than muscular strength to create barriers and manage distance.",
        "content": """## Overview

Framing is the fundamental defensive concept in grappling of using the bones and skeletal structure of the body to create barriers against an opponent's pressure, rather than relying on muscular strength. A frame converts an opponent's force into a structural load borne by the skeleton, allowing a smaller grappler to withstand and redirect much larger forces than they could resist with muscle alone.

Understanding framing is essential to every aspect of grappling defense, from surviving under mount to retaining guard to escaping pins.

## Principles

**Bone over muscle.** A frame is strong when the load travels through aligned bones — forearm, upper arm, shoulder — into the ground or the opponent's body. It is weak when it depends on muscle contraction to maintain shape.

**Alignment matters.** A frame is most effective when the force travels along the length of the bone rather than across it. An arm braced with a straight line from hand to shoulder can support enormous weight. The same arm bent at an awkward angle collapses easily.

**Frames create space, not positions.** The purpose of a frame is not to hold a position indefinitely but to create enough space to execute a movement — a shrimp, a reguard, an escape. Frames buy time and distance; movement converts them into positional improvement.

## Common Frames

**Forearm frame across the neck:** Used in side control escapes. The bottom player places their forearm across the top player's throat or jaw, creating distance to hip escape.

**Knee-elbow connection:** Used in guard retention. The bottom player keeps their elbows tight to their knees, preventing the passer from closing the distance needed to complete a pass.

**Stiff arm:** An extended arm against the shoulder or hip. Used to maintain distance in open guard and prevent pressure passers from closing space.

## Framing Mistakes

The most common framing errors are pushing (using muscle instead of structure), framing too far from the body (creating leverage for the opponent), and framing without following up (holding a static frame instead of using it to create movement).

## Related

See also: Guard Retention, Side Control Escapes, Shrimping, Posture, Base
"""
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Create or get admin user
        admin = User.query.filter_by(username='GrapplingWiki').first()
        if not admin:
            admin = User(username='GrapplingWiki', email='admin@grapplingwiki.com')
            admin.set_password('grapplingwiki2026')
            db.session.add(admin)
            db.session.flush()
            print(f"Created admin user: GrapplingWiki")

        # Create tags
        tag_map = {}
        for name, slug, desc in TAGS:
            tag = Tag.query.filter_by(slug=slug).first()
            if not tag:
                tag = Tag(name=name, slug=slug, description=desc)
                db.session.add(tag)
                db.session.flush()
                print(f"Created tag: {name}")
            tag_map[name] = tag

        # Create articles
        created = 0
        for data in ARTICLES:
            existing = Article.query.filter_by(slug=data["slug"]).first()
            if existing:
                print(f"  Skipping (exists): {data['title']}")
                continue

            article = Article(
                title=data["title"],
                slug=data["slug"],
                content=data["content"].strip(),
                summary=data["summary"],
                author_id=admin.id,
                category=data["category"],
                is_published=True,
                view_count=0
            )

            # Add tags
            for tag_name in data.get("tags", []):
                if tag_name in tag_map:
                    article.tags.append(tag_map[tag_name])

            db.session.add(article)
            db.session.flush()

            # Create initial revision
            rev = ArticleRevision(
                article_id=article.id,
                editor_id=admin.id,
                content=data["content"].strip(),
                edit_summary="Initial article",
                revision_number=1
            )
            db.session.add(rev)
            created += 1
            print(f"  Created: {data['title']}")

        db.session.commit()
        print(f"\nDone! Created {created} articles, {len(tag_map)} tags.")
        print(f"Visit http://localhost:5000 to see them.")


if __name__ == '__main__':
    seed()

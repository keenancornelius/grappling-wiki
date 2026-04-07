"""
Comprehensive seed: high-quality grappling articles with full relationship graph.
Creates 64 articles across positions, submissions, sweeps, passes, takedowns, and concepts.
Safe to run repeatedly — skips existing articles by slug.

Run from project root:
    python scripts/seed_comprehensive.py

or with Flask CLI:
    flask seed-comprehensive
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Article, ArticleRevision, Category
from app.models.article import ArticleRelationship


def get_or_create_subcategory(parent_slug, name, slug, description, user_id):
    """Get or create a subcategory under an existing parent category."""
    # Check if subcategory already exists
    cat = Category.query.filter_by(slug=slug).first()
    if cat:
        return cat

    # Find parent
    parent = Category.query.filter_by(slug=parent_slug).first()
    if not parent:
        print(f"  [warn] Parent category '{parent_slug}' not found, skipping subcategory '{name}'")
        return None

    # Create subcategory
    cat = Category(
        name=name,
        slug=slug,
        description=description,
        parent_id=parent.id,
        created_by_id=user_id
    )
    db.session.add(cat)
    db.session.flush()
    print(f"  [created] Subcategory: {name}")
    return cat


def seed_article(title, slug, content, summary, category_slug, author_id):
    """Create an article with initial revision. Returns the Article or None if it already exists."""
    existing = Article.query.filter_by(slug=slug).first()
    if existing:
        return existing

    # Look up category by slug
    cat = Category.query.filter_by(slug=category_slug).first()
    if not cat:
        print(f"  [warn] Category '{category_slug}' not found for article '{title}'")
        return None

    article = Article(
        title=title,
        slug=slug,
        content=content.strip(),
        summary=summary,
        author_id=author_id,
        category_id=cat.id,
        category=category_slug,  # Keep legacy field populated
        is_published=True,
        view_count=0
    )
    db.session.add(article)
    db.session.flush()

    # Create initial revision
    rev = ArticleRevision(
        article_id=article.id,
        editor_id=author_id,
        content=content.strip(),
        edit_summary='Initial article creation',
        revision_number=1
    )
    db.session.add(rev)
    print(f"  [created] {title}")
    return article


def add_relationship(source_slug, target_slug, rel_type, user_id):
    """Add relationship between two articles if both exist and relationship doesn't already exist."""
    src = Article.query.filter_by(slug=source_slug).first()
    tgt = Article.query.filter_by(slug=target_slug).first()

    if not src or not tgt:
        return False

    existing = ArticleRelationship.query.filter_by(
        source_article_id=src.id,
        target_article_id=tgt.id,
        relationship_type=rel_type
    ).first()

    if existing:
        return False

    rel = ArticleRelationship(
        source_article_id=src.id,
        target_article_id=tgt.id,
        relationship_type=rel_type,
        created_by_id=user_id
    )
    db.session.add(rel)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE CONTENT
# ─────────────────────────────────────────────────────────────────────────────

POSITIONS = {
    "mount": {
        "title": "Mount",
        "category_slug": "dominant-position",
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

The trap-and-roll captures the opponent's arm on one side, bridges the hips explosively upward, and rolls the opponent over the captured arm. The elbow-knee escape creates space by framing on the hip and shoulder, shrimping the hips out, and establishing half guard or open guard.

## Strategic Value

Mount is the position where most professional matches are finished. The threat of submissions is so omnipresent that maintaining mount often means victory is inevitable — the opponent must escape or face submission, and the pressure of avoiding multiple threats often leads to mistakes.

"""
    },

    "side-control": {
        "title": "Side Control",
        "category_slug": "dominant-position",
        "summary": "A dominant pin position where the top player controls the opponent laterally, chest-to-chest.",
        "content": """## Overview

Side control (also called side mount or kesa gatame in judo terminology) is a dominant top position where the top player lies perpendicular across the opponent's torso, controlling their arm and shoulder while pinning them to the mat. Despite being less dominant than mount or back control, side control is one of the most common and strategically important positions in grappling.

The positional transition from guard passing almost always leads to side control as an intermediate step. In IBJJF, achieving side control awards 3 points.

## Key Mechanics

The top player's weight is distributed across the opponent's chest and shoulder, with the hips tight to prevent the bottom player from creating space. The control arm (closest to the opponent's head) wraps around or controls the neck/shoulder, while the bottom arm often grips the far hip or belt to pin the opponent down.

A crucial principle is keeping the head on the same side as the control arm — if the head is on the opposite side, the opponent can more easily escape via underhook or shrimp.

## Variations

**Kesa Gatame:** A judo-style grip where the top player's control arm wraps the opponent's neck tightly. Extremely tight but leaves some submission openings for the bottom player.

**Underhook Side Control:** The top player secures an underhook beneath the opponent's armpit, a very powerful control that often leads to back takes or mounting.

**Overhook Side Control:** The control arm overhooks the opponent's arm and shoulder, similar to a top-half guard position. Good for maintaining pressure.

**Reverse Side Control:** The top player lies on their back, perpendicular to the opponent, controlling their arm and legs. A less stable but sometimes useful variant for transitions.

## Attacks

From side control, the top player can attack with kimura, americana, arm triangle, darce choke (with front headlock positioning), north-south choke, and multiple knee on belly transitions. Submissions are less immediate than from mount, but the strategic control often sets up better positioning.

## Transitions

Side control is the hub of the top position. From here, the top player can advance to mount, knee on belly, north-south position, or back control. Side control also serves as the landing spot for many guard pass variations.

## Escapes

The bottom player's fundamental side control escape is the underhook escape (creating an underhook and using it to build to their knees or escape to top) or the elbow-escape (framing on the knee and hip, shrimping, and working to turtle position or half guard).

## Strategic Role

Side control is the crossroads of positional dominance. It's not the final destination but the launching pad for more devastating positions. Many modern high-level matches feature extensive side control exchanges where both players vie for better positioning rather than immediate submissions.

"""
    },

    "back-control": {
        "title": "Back Control",
        "category_slug": "dominant-position",
        "summary": "Rear dominant position with legs wrapped around the opponent's torso and chest-to-back control.",
        "content": """## Overview

Back control (often called back mount or rear control) is arguably the most dominant position in grappling, with one player behind an opponent, typically with both legs wrapped around their torso (the body triangle) and control of their arms. The back player has superior position, limited opponent options, and direct access to the rear naked choke.

In IBJJF competition, achieving back control with hooks awards 4 points, and back control with the body triangle is considered even more dominant.

## Why Back Control Dominates

The back player is invisible to the opponent — the opponent cannot see hands, arms, or body position, making it nearly impossible to defend against attacks. Combined with body weight control and the rear naked choke threat, back control has the highest submission finish rate of any position in competitive grappling.

## Variations

**Back Mount with Hooks:** The attacking player's feet hook both legs on the inside, with the heels pulled up toward the opponent's groin or thighs. Most common configuration.

**Body Triangle:** The attacking player's legs wrap around the opponent's torso with ankles crossed, forming a locked triangle. Extremely tight and minimizes the opponent's ability to create space.

**Back Mount with Seatbelt Grip:** The attacking player has one arm wrapped around the opponent's torso (seatbelt grip) while the other hand controls the far arm or neck. Good control but slightly less offensive than double-under positioning.

**Turtle Position Transition:** When an opponent turtles (gets on hands and knees), back control can transition to this defensive shell position.

## Attacks

The rear naked choke is the primary back control submission — it is the highest-percentage submission in the sport and most finishes come from back control. Other submissions available include the body triangle submission, arm triangle from the back, and the jaw crank/neck crank.

## Escapes

Escaping back control is extremely difficult. The primary escapes are: bridging hard to roll the back player, rolling to create space and turn to face the opponent, moving the back player's hips away from center, and going inverted (turtle position) to transition out. None are high-percentage against an opponent who fully understands back control.

## Hooks and Base

Maintaining back control requires excellent hook placement — the attacking player must keep feet tight and prevent the opponent from rotating. Losing the hooks often means losing the position entirely. The attacking player must also maintain body connection (chest to back) to prevent the opponent from turning.

## Strategic Dominance

In high-level competition, achieving back control is often the match-ender. Statistics show that rear naked choke submissions from back control account for a huge percentage of all competition finishes. Many matches are decided not by who gets back control first, but by who maintains it longest.

"""
    },

    "closed-guard": {
        "title": "Closed Guard",
        "category_slug": "guard",
        "summary": "The foundational bottom position where the guard player locks their legs around the opponent's torso.",
        "content": """## Overview

Closed guard is a ground fighting position where the bottom grappler wraps their legs around the opponent's torso, locking their ankles behind the opponent's back. It is one of the most fundamental positions in Brazilian Jiu-Jitsu and serves as the starting point for an enormous variety of attacks, sweeps, and transitions.

Despite being a bottom position, closed guard is considered offensive — the guard player controls the distance, posture, and pace of the exchange. In IBJJF competition, pulling closed guard scores nothing, but the position is the foundation of guard strategy.

## History

Closed guard became central to BJJ's identity through the Gracie family's development of the art. Royce Gracie famously used closed guard to control and submit much larger opponents in the early UFC events, demonstrating that a skilled guard player could neutralize size and strength advantages from their back.

## The Posture Battle

The fundamental dynamic in closed guard is the battle over posture. When the guard player breaks the top player's posture (pulls them down), attacks become available — submissions, sweeps, and control. When the top player maintains upright posture, they can begin working to pass guard.

This dynamic drives the entire closed guard exchange: the bottom player seeks to collapse posture, the top player resists and tries to open the guard or improve position.

## Attacking from Closed Guard

The closed guard offers a diverse set of submissions and sweeps:

**Submissions:** Armbar, triangle choke, guillotine, omoplata, kimura, cross collar choke (gi)

**Sweeps:** Hip bump sweep, scissor sweep, flower sweep, pendulum sweep

**Transitions:** Open guard variations, rubber guard, high guard for armbar setups

## Guard Opening Mechanics

The top player's primary objectives are to maintain posture, prevent the guard player from breaking their alignment, and work to open the guard (separate the locked ankles). Common guard-opening techniques include standing up in guard, knee-in-the-tailbone pressure, and log-splitter grips.

## Defending in Closed Guard

The guard player must prevent being flattened — a flattened guard player has lost much of their offensive capability. Framing with the arms against the opponent's hips and shoulders is critical to maintain space and create movement opportunities.

## Grip Fighting

Grip fighting is critical in closed guard — whoever controls the grips controls the exchange. If the guard player secures good collar and sleeve grips, they can break posture easily. If the top player controls the guard player's hands, they can maintain posture and begin passing.

## Strategic Concepts

The fundamental battle in closed guard is posture versus posture-breaking. This creates a rich technical exchange where both players have multiple viable paths to victory.

"""
    },

    "half-guard": {
        "title": "Half Guard",
        "category_slug": "guard",
        "summary": "A versatile guard position where the bottom player traps one of the top player's legs between their own.",
        "content": """## Overview

Half guard is a ground position where the bottom grappler has one of the top player's legs trapped between their own legs, while the top player has partially passed the guard. Once considered a transitional or inferior position, half guard has evolved into one of the most strategically rich and actively played guards in modern BJJ.

The position exists on a spectrum — from a nearly-passed defensive posture to an aggressive attacking platform, depending on the bottom player's frames, underhooks, and body angle.

## Why Half Guard Evolved

Early BJJ often discouraged half guard as a "weak" position. But over the last two decades, practitioners like John Kavanagh, Eddie Bravo, and others demonstrated that half guard could be a powerful attacking position when the underhook and sweep mechanics were properly understood.

## Variations

**Knee Shield (Z-Guard):** The bottom player places their shin across the top player's torso, creating a frame that manages distance and prevents the passer from flattening them. One of the most common and effective half guard configurations. The knee shield creates immediate sweeping opportunities.

**Deep Half Guard:** The bottom player dives underneath the top player, positioning themselves below their center of gravity. Despite appearing disadvantageous, deep half offers powerful sweeps because the bottom player controls the top player's base from directly beneath them.

**Lockdown:** Popularized by Eddie Bravo, the lockdown uses a figure-four leg configuration to trap the top player's leg. Combined with the "whip-up" motion, it creates sweeping opportunities and disrupts the top player's base.

**Half Butterfly:** The bottom player inserts a butterfly hook with their free leg while maintaining the half guard with the other. This hybrid position combines the control of half guard with the sweeping power of butterfly guard.

**Deep Half with Underhook:** Also called "scuttle guard," the bottom player achieves deep half while establishing an underhook, a very powerful combination for sweeping.

## The Underhook Principle

The essential battle in half guard revolves around the underhook. If the bottom player wins the underhook (arm under the top player's armpit), they can build to their knees, sweep, or take the back. If the top player wins the underhook, they can crossface, flatten the bottom player, and begin passing more effectively.

## Framing

Framing is equally critical. The bottom player must prevent being flattened — once flat on their back with no frames, half guard becomes a passing position rather than a guard. The knee shield frame is the primary defensive tool.

## Attacking from Half Guard

From half guard, the bottom player can:

- **Sweep** (via knee shield, deep half, or whip mechanics)
- **Escape** to the knees or open guard
- **Attack submissions** (heel hook from half, ankle lock from deep half)
- **Take the back** (via underhook and turn)

## Transitions

Half guard is often a transitional position. From bottom, it can transition to closed guard (if the free leg wraps), open guard, or back control (via underhook). From top, the goal is typically to establish a stronger pass or transition to side control or mount.

## Strategic Role

In modern competition, half guard is a critical intermediate position. Many matches feature extended half guard exchanges where the bottom player works to sweep while the top player works to pass or improve position.

"""
    },

    "butterfly-guard": {
        "title": "Butterfly Guard",
        "category_slug": "guard",
        "summary": "A sitting open guard position where the bottom player uses butterfly hooks to elevate and sweep the opponent.",
        "content": """## Overview

Butterfly guard is a sitting open guard position where the bottom grappler sits upright with their feet hooked on the inside of the opponent's thighs (butterfly hooks), creating immediate sweeping and transitional opportunities. The position is considered highly offensive and is fundamental in modern no-gi grappling.

Unlike closed guard, butterfly guard requires less leg strength to maintain and offers more mobility. It is a primary entry point to arm drags, back takes, and multiple sweep attacks.

## Key Mechanics

The bottom player sits with feet planted on the ground, knees bent, and both feet hooked on the inside of the top player's thighs. This hook position is the defining feature — the feet are in the crease between the thigh and hip, allowing the bottom player to elevate the top player's knees by driving their own knees upward.

Good hand positioning (on the opponent's shoulders, chest, or around the neck) determines what attacks become available.

## The Butterfly Hook Elevator

The primary attack from butterfly guard is the butterfly hook sweep, where the bottom player drives both knees upward while pulling the opponent, causing them to flip forward. This sweep works against almost any top player position and is high-percentage at all levels.

## Variations

**Aggressive Butterfly Guard:** The bottom player uses collar ties, underhooks, or shoulder control to chain into multiple attacks. Often used as an entry point to arm drag back takes.

**Feet on Hips Butterfly:** The bottom player's hooks are on the opponent's hips rather than the thighs, used primarily as a transitional position or for distance management.

**Butterfly with Deep Underhook:** The bottom player combines the butterfly hooks with a deep underhook, creating a very powerful offensive position.

## From Butterfly to Back

Many modern grapplers, particularly Marcelo Garcia, use butterfly guard primarily as an entry to arm drags and back takes. The position's mobility and control make it ideal for transitioning to the highest-percentage submission (rear naked choke from back control).

## Submissions from Butterfly

While not as submission-heavy as closed guard, butterfly guard allows triangle choke setups, guillotine chokes (by transitioning to closed guard or front headlock positioning), and collar choke variations in gi.

## Common Attacks

1. **Butterfly Hook Sweep:** The primary attack
2. **Arm Drag:** Grab one arm and pull across the body to rotate and take the back
3. **Overhook Back Take:** Secure an overhook and transition to back control
4. **Collar Tie Takedown:** Pull the head and drive forward to take down a standing opponent
5. **Transition to Closed Guard:** Rock back onto your shoulders and pull the opponent into closed guard for different attacks

## Open Guard Fundamentals

Butterfly guard teaches critical open guard principles: footwork, hip mobility, quick transitions, and arm drag mechanics. Practitioners strong in butterfly guard typically develop excellent overall open guard games.

"""
    },

    "de-la-riva-guard": {
        "title": "De La Riva Guard",
        "category_slug": "guard",
        "summary": "An open guard position using a hook on the opponent's far knee and distance management with the hands.",
        "content": """## Overview

De La Riva (DLR) guard is an open guard position where the bottom grappler hooks the opponent's far knee with their own leg while using hand grips on the opposite side to control distance and angle. Named after the legendary team DLR, this position became fundamental to modern open guard strategy and is characterized by its emphasis on distance, angle, and leverage over body contact.

## Key Mechanics

The bottom player uses one leg to hook the opponent's far knee from the outside, while placing the other foot on the opponent's hip or underbelly for distance. The arms control grips on the opponent's pants or jacket (in gi) or body for leverage. The result is a position where the bottom player controls the engagement from a distance, able to quickly transition into sweeps or escape.

## Hook Position

The crucial hook is placed on the outside of the opponent's far knee. This hook allows the bottom player to:

- Control the opponent's leg and base
- Create angles for sweeping
- Manage distance to prevent passing
- Transition to other positions like berimbolo or x-guard

## Variations

**Standup DLR:** The bottom player keeps their non-hooking leg extended for distance while standing to their feet, creating immediate back-take opportunities.

**Leg Drag DLR:** The bottom player transitions to a leg drag position for sweeping.

**High Hook DLR:** The bottom player hooks higher up on the leg for more control, typically used against taller opponents.

**Reverse DLR:** The bottom player reverses the hook to the other side, often used as a transitional position.

## Distance Management

DLR is fundamentally about maintaining the right distance — far enough to be safe from submissions but close enough to attack. The hand grips and foot on the hip are the distance controllers. Poor distance control results in getting passed; too much distance and attacks aren't available.

## Sweeping from DLR

The primary DLR sweeps involve:

- **Tripod Sweep:** The bottom player uses the DLR hook, far leg, and hands to create a tripod and sweep the opponent's far leg
- **Berimbolo:** A complex inversion and back take using the DLR hook as the pivot
- **Sit-up Sweep:** The bottom player sits up into the DLR hook to elevate and sweep the opponent

## Transitions

DLR transitions to many positions: x-guard, spider guard, leg drag, berimbolo, and back to standing. Good DLR players constantly flow between these positions, making them unpredictable.

## Modern Evolution

The position has evolved dramatically. Early DLR focused on sweeping and positional advantage, while modern DLR players like Gustavo Batista and João Gabriel Rocha have incorporated leg lock attacks, particularly heel hooks and back takes, making it a complete attacking system.

"""
    },

    "spider-guard": {
        "title": "Spider Guard",
        "category_slug": "guard",
        "summary": "A gi-based open guard using grips on the opponent's sleeves to control posture and create sweeping angles.",
        "content": """## Overview

Spider guard is an open guard position specific to gi (jacket) grappling where the bottom player grips both of the opponent's sleeves, typically near the cuff or sleeve opening, and places their feet on the opponent's biceps. This configuration allows remarkable control over the opponent's posture and arm positioning, making it difficult to pass and creating multiple sweeping opportunities.

The position is characteristic of high-level gi competition, particularly among guard-focused competitors, and is essential knowledge for any serious gi grappler.

## Key Mechanics

The bottom player:

1. Grips both sleeves (typically lasso-style or near the cuff)
2. Places both feet on the opponent's biceps
3. Lies on their back or at an angle, creating distance

This configuration traps the opponent's arms and controls their posture. The opponent cannot easily lower their hands or collapse forward without the bottom player having immediate sweeping opportunities.

## Sleeve Control Principle

Spider guard is built on the principle of controlling the opponent's sleeves. By controlling the sleeves, the bottom player controls the opponent's arm positioning, which limits their options significantly. A passer who cannot lower their hands and cannot posture down is severely limited.

## Variations

**Two-on-One Spider:** Both sleeves are controlled, the most common form.

**Lasso Spider:** One leg wraps around the arm while controlling the sleeve grip.

**Sit-up Spider:** The bottom player sits up into spider guard for more aggressive sweeping.

**Spider with Collar Grip:** Often combined with sleeve control for even more positional control.

**Spider Guard Entry from Closed Guard:** A common transition where the guard player breaks posture and places feet on biceps while maintaining sleeve grips.

## Sweeping from Spider Guard

The primary sweeps from spider guard involve:

- **Basic Spider Sweep:** Use foot placement on the biceps and sleeve control to elevate the opponent's arms, creating a rotating sweep
- **Armdrag from Spider:** Convert the sleeve grip into an arm drag and take the back
- **Scissors Sweep Variation:** Combine spider guard setup with scissor mechanics

## Defensive Challenges

Spider guard is effective precisely because it's difficult to pass. A skilled spider guard player can create sweeps or submissions faster than a passer can establish dominant positioning. However, spider guard requires grip strength and can be tiring for the guard player.

## Transitions

From spider guard, the bottom player can:

- Sweep to top position
- Transition to lasso guard or De La Riva
- Take the back (via armdrag)
- Transition to collar chokes

## Gi-Only Position

Spider guard is almost entirely a gi position — without sleeves to control, the effectiveness diminishes dramatically. This is one of the major differences between gi and no-gi grappling.

"""
    },

    "x-guard": {
        "title": "X-Guard",
        "category_slug": "guard",
        "summary": "An underneath sweep guard using an inside thigh hook and foot placement to control the opponent's base.",
        "content": """## Overview

X-guard is an underneath open guard position where the bottom grappler hooks the opponent's inner thigh with their own leg while placing the other foot on the opponent's hip, creating a two-point control system (forming an "X" shape visually). The position is characterized by its power in unbalancing and sweeping and has become a cornerstone of modern open guard.

Unlike many guard positions that emphasize distance, X-guard is about getting underneath the opponent and disrupting their base from below.

## Key Mechanics

The bottom player places one leg with a hook on the inside of the opponent's thigh, while the other leg's foot sits on the opponent's hip or belly for control and angle creation. The hands typically control the opponent's arms or body for additional stability.

The critical concept is that the bottom player is underneath the opponent's center of gravity, making it very difficult for the opponent to maintain their position. Any forward movement by the opponent can be converted into a sweep.

## The Underneath Position Principle

X-guard works because the bottom player is below the opponent's center of gravity. Gravity naturally favors sweeping from below, and the opponent's own weight becomes a liability. This principle makes X-guard high-percentage even against larger opponents.

## Variations

**X-Guard with Overhook:** The bottom player secures an overhook on the opponent's arm while maintaining the hook and foot control, creating a very dominant position.

**X-Guard to Leg Drag:** A transitional position where the bottom player converts to a leg drag position.

**Standing X-Guard:** The bottom player partially stands into the X-guard for more aggressive attacks.

**X-Guard Sit-up:** The bottom player sits up more to create better angles for sweeping and back takes.

## Sweeping from X-Guard

The primary X-guard sweep uses the hook and foot placement to elevate the opponent, typically resulting in side control or mount position. The key is timing — the sweep works when the opponent attempts to pass or create distance.

## Back Take from X-Guard

Many modern X-guard players use the position as an entry to back takes. By converting the hook control and underbody position into back control, players can chain directly to the rear naked choke.

## Footwork and Agility

X-guard players develop excellent footwork and hip mobility. The constant shifting of hooks, foot placement, and angles requires dynamic movement and timing.

## Common Transitions

From X-guard, the bottom player can:

- Sweep to top position
- Take the back
- Transition to single-leg X (a leg lock position)
- Escape to open guard
- Come to the knees

## Integration with Other Guards

X-guard works synergistically with other open guards. Good open guard players often flow between X-guard, De La Riva, spider guard, and other positions, making them unpredictable and difficult to pass.

"""
    },

    "knee-on-belly": {
        "title": "Knee on Belly",
        "category_slug": "dominant-position",
        "summary": "A transitional dominant position with one knee on the opponent's abdomen, creating discomfort and submission threats.",
        "content": """## Overview

Knee on belly (KOB), also called knee in the belly or knee on chest, is a transitional dominant position where the top player places one knee on the opponent's abdomen or chest while using their other leg for base, creating both discomfort and multiple submission and positional threats. While less dominant than mount or back control, knee on belly is a powerful intermediate position that keeps the opponent in constant defensive pressure.

In IBJJF competition, achieving knee on belly awards 2 points.

## Strategic Purpose

Knee on belly serves multiple purposes:

1. **Disruption:** The knee creates constant physical discomfort and unease, forcing the opponent into reactive defense
2. **Angle Creation:** The position creates angles for submissions and transitions that aren't available from other positions
3. **Threat Diversification:** From KOB, the top player can transition to multiple positions quickly
4. **Fatigue:** The discomfort and constant threat cause fatigue and decision-making errors

## Position Details

The controlling player's knee sits tightly against the opponent's side, typically at the floating rib or abdominal area. The base leg (usually the back leg) is extended for stability. Hands typically control the head/neck area or wrap around for security.

## Key Submissions from KOB

- **Arm Triangle Choke:** The rear arm transitions to an arm triangle position
- **Kimura Grip:** Control the opponent's far arm for a shoulder lock
- **Americana:** Control the far arm in a different angle
- **Keylock/Armlock:** Control the near shoulder and arm
- **Neck Cranks:** Various neck cranks and chokes

## Transitions

Knee on belly is fundamentally a transitional position. From here, the top player can move to:

- **Mount Position:** Push the knee off and transition to mount
- **Side Control:** Move the knee and establish side control
- **Back Control:** Rotate to take the back
- **North-South Position:** Move to a head-to-toe control

## Defensive Reactions

The opponent in knee on belly typically tries to:

- **Escape the pressure:** Creating frames and shrimping to escape
- **Create an underhook:** To disrupt the top player's control
- **Roll away:** Using momentum to dislodge the knee

The top player must anticipate these reactions and use them as entries to submissions or better positions.

## Balance and Agility

Maintaining knee on belly requires good balance and weight distribution. A skilled KOB player maintains constant pressure and mobility, ready to transition or apply submissions.

## Frustration Tool

At higher levels, knee on belly is also a psychological tool. The constant discomfort and threat of transitions to worse positions often causes decision-making errors and defensive panic.

"""
    },

    "north-south": {
        "title": "North-South Position",
        "category_slug": "dominant-position",
        "summary": "A head-to-toe pin position where the top player controls the opponent perpendicular from above their head.",
        "content": """## Overview

The north-south position (also called north-south pressure or north-south control) is a dominant pin where the top player lies perpendicular to the opponent with their head near the opponent's head and their body extending down toward their opponent's feet. This position creates unique submission opportunities and is particularly effective in no-gi grappling.

Unlike side control, north-south approaches the opponent from directly above the head, creating different structural pressures and submission angles.

## Key Mechanics

The top player's weight is distributed across the opponent's face, neck, and upper chest area. Hands typically control the opponent's near arm or chest. The pressure is very direct and uncomfortable for the opponent.

## Submissions from North-South

**North-South Choke:** The most common submission, applied by sliding the forearm across the opponent's neck from above. The position naturally facilitates this choke.

**Arm Triangle:** Transition with arm control for an arm triangle choke.

**Leg Lock Setup:** The position can transition to leg lock attacks on the opponent's near leg.

**Neck Crank:** Various pressing neck techniques.

## Transitions

From north-south, the top player can:

- Transition to side control
- Move to mount
- Move to the legs for leg lock attempts
- Return to a more traditional side control position

## Escape Routes

The opponent in north-south typically escapes via:

- **Framing:** Creating frames against the hips or shoulders
- **Shrimping:** Creating space and reversing position
- **Under-hook:** Securing an underhook to disrupt control
- **Inverting:** Going inverted to turtle

## Pressure Dynamics

North-south is effective because the pressure is directly downward and the opponent has limited options. The head-to-toe alignment makes it difficult to create frames or leverage.

## No-Gi Preference

While north-south works in both gi and no-gi, it is particularly effective in no-gi where the choke mechanics work more smoothly without the friction of the jacket.

"""
    },

    "turtle-position": {
        "title": "Turtle Position",
        "category_slug": "transitional",
        "summary": "A defensive shell position on hands and knees, used for escaping pressure or transitioning to standing.",
        "content": """## Overview

Turtle position (also called turtle guard or defensive shell) is a position where a grappler is on their hands and knees with their head tucked and back rounded, creating a defensive shell against top pressure. While typically seen as a transitional or defensive position, skilled practitioners use turtle to escape dominant positions, transition to standing, or even attack from underneath.

The position gets its name from the resemblance to a turtle withdrawing into its shell — everything is contracted and protected.

## Uses

**Escape from Pressure:** When under extreme pressure in side control or mount, turtling up allows the bottom player to reduce submission vulnerability and buy time to escape.

**Transition to Standing:** From turtle, the bottom player can work toward getting to their feet or transitioning to a more advantageous position.

**Defensive Holding:** Against a passer, turtling can slow their progress and create opportunities for counterattack.

## Dangers

Turtle position has significant risks. The back is exposed, making it vulnerable to:

- **Back Control:** The opponent can easily slide around and achieve back control with hooks
- **Rear Naked Choke:** A high-percentage finish from the exposed back
- **Back Exposure:** Multiple submissions targeting the exposed back

## Turning and Reversing

Rather than staying static in turtle, the defensive player should actively work to turn and face the opponent. This transition from turtle to reversal or to standing is the goal, not staying in the shell position.

## Turtle from Front Headlock

When caught in a front headlock or snap-down position, going to turtle can be an intentional defense to escape the submission threat while staying low.

## Escaping to the Knees

From turtle, the bottom player can:

- **Extend to standing:** Using hand placement and hip movement to get to their feet
- **Rotate and escape:** Turn to face the opponent and create distance
- **Explode to standing:** Explosive movement from turtle to a standing position

## Top Player Strategy

The opponent controlling a turtled player should immediately work to establish back control before the turtle player can transition or escape. The opening is fleeting.

## Not an Offensive Position

Turtle is almost never an offensive position. The priority is always to transition out while minimizing damage and submission risk.

"""
    },

    "50-50-guard": {
        "title": "50/50 Guard",
        "category_slug": "leg-entanglement",
        "summary": "A symmetrical leg entanglement position where both players have equal control and leg lock opportunities.",
        "content": """## Overview

The 50/50 guard is a leg entanglement position where both grapplers have one leg hooked around the other's corresponding leg, creating a symmetrical position where both players have equal leg lock opportunities and control. The name reflects the equal nature of the position — neither player has a clear advantage, hence "50/50."

This position has become increasingly important in modern grappling, particularly in no-gi and leg lock-heavy competition.

## Mechanics

Both players sit at angles with one leg of each player entangled with the other's leg. The entanglement creates a situation where:

- Both players can attack the entangled leg with leg locks
- Neither player can easily escape without risk
- Position changes require precise timing and technique

## Entry Points

The 50/50 typically develops from:

- **Open guard:** A transition while working open guard
- **Guard pass defense:** A defensive counter to certain passing attempts
- **Direct engagement:** One player intentionally establishing the 50/50
- **Leg lock exchanges:** Natural outcome of leg lock battles

## Leg Lock Threats

From 50/50, both players have immediate access to:

- **Heel Hook:** The primary submission threat
- **Straight Ankle Lock:** Secondary submission option
- **Knee Reap:** Transitional control technique
- **Calf Slicer:** Less common but viable

## Breaking the Symmetry

The key to advantage from 50/50 is breaking the symmetry. This can be done through:

- **Heel Hook Entry:** Establishing a heel hook faster than the opponent
- **Leg Control:** Gaining better control over the entangled leg through pressure or angle
- **Transition Out:** Moving to a dominant position where you control the opponent's leg
- **Leg Lock Defense:** Preventing the opponent's attacks while setting up your own

## Disengagement

Players often use 50/50 as a transition. By quickly disengaging from the entanglement, a player can move to open guard, standing, or other positions.

## Modern Evolution

Originally considered a stalling position, modern understanding of 50/50 recognizes it as an exciting position with high-percentage leg lock attacks. Top competitors now pursue 50/50 deliberately.

## Risk Assessment

The 50/50 is inherently risky for both players. Entering 50/50 without a clear path to advantage can result in trading dangerous leg lock attempts. Skilled 50/50 players understand how to break symmetry quickly.

"""
    },

    "ashi-garami": {
        "title": "Ashi Garami",
        "category_slug": "leg-entanglement",
        "summary": "The standard leg entanglement position controlling one of the opponent's legs with both of your legs.",
        "content": """## Overview

Ashi garami is a leg entanglement position where one grappler controls the opponent's leg (usually between the knees and hip) using both of their own legs, creating a powerful position for foot and ankle lock attacks. Often called "inside leg lock position" or "foot lock position," ashi garami is the foundational position for much of modern leg lock grappling.

The term comes from Japanese judo terminology where "ashi" means leg and "garami" means entanglement.

## Mechanics

One player's leg is trapped between both legs of the controlling player. The controlling player's legs wrap the trapped leg, typically with:

- One leg behind the trapped leg's knee
- The other leg across the hip area or knee
- Both legs working together to control the position

## Primary Submissions

From ashi garami, the primary submissions are:

**Heel Hook:** The most dangerous and highest-percentage submission, applying rotational force to the knee and ankle by controlling the heel.

**Straight Ankle Lock:** Hyperextension of the ankle by isolating the foot.

**Knee Reap:** Control technique that sets up heel hooks from different angles.

**Toe Hold:** Rotational force applied to the forefoot and ankle.

## Defending the Trapped Leg

The opponent with a trapped leg must:

- **Escape the position:** Use hip movement and leg strength to dislodge the attacker
- **Defend the submission:** Point toes, turn hips, or invert to avoid the worst angles
- **Counterattack:** Use their free leg or arms to attack while defending the trapped leg
- **Invert:** Going inverted is often the best escape option

## Positional Variations

**Inside Control:** Maximum control over the trapped leg with tight wrapping.

**Sidecar Position:** A variation where the controlling player's hips are perpendicular to the trapped leg.

**80/20 Position:** A specific angle variation used for particular heel hook entries.

**Saddle Position:** A more advanced variation with even better control.

## Transitioning In and Out

Ashi garami is often a transitional position. Grapplers enter ashi garami from:

- Guard positions (closed guard, half guard)
- Passing attempts
- Open guard transitions
- Leg lock chains

From ashi garami, players can transition to:

- Heel hook finishes
- Ankle lock finishes
- Saddle position
- Other leg lock positions
- Back to open guard

## Guard vs. Submission

The distinction between "ashi garami" as a guard position (bottom player's defensive counter to a passer) and "ashi garami" as a leg lock position (attacking position) is important. Context determines the application.

## Modern Importance

Modern leg lock systems, particularly those pioneered by John Danaher, have elevated ashi garami from a niche position to a core part of high-level grappling. Understanding ashi garami is now considered essential.

"""
    },

    "saddle-position": {
        "title": "Saddle Position (Inside Sankaku)",
        "category_slug": "leg-entanglement",
        "summary": "An advanced leg entanglement with dominant control over the opponent's leg, primarily for heel hook attacks.",
        "content": """## Overview

The saddle position (also called inside sankaku, which translates to "inside triangle" in Japanese judo terminology) is an advanced leg entanglement position where the controlling player has exceptional positional dominance over the opponent's trapped leg. Unlike standard ashi garami, the saddle position offers even more control and is often considered the apex of leg lock dominance.

The name "saddle" comes from the visual appearance — the controlling player is positioned much like sitting in a saddle, straddling the opponent's leg.

## Positioning

In the saddle position, the controlling player:

- Positions their hips underneath the opponent's leg (essentially going under the leg)
- Keeps the opponent's foot and ankle between their legs
- Often has their back to the opponent's body
- Controls the foot/ankle for immediate submission threats

This positioning provides superior control compared to standard ashi garami because the controlling player is directly underneath the trapped leg.

## Primary Advantage

The major advantage of the saddle is that the trapped player has extremely limited escape options. Being underneath their leg, the controlling player can apply submissions with greater power and the trapped player's natural movements are less effective.

## Heel Hook from Saddle

The heel hook from saddle position is considered one of the most dangerous submissions in grappling. The angle and control mean that even small movements can result in dangerous pressure on the ankle and knee.

## Entries to Saddle

The saddle position is typically reached from:

- **Ashi garami:** Transitioning by going underneath the trapped leg
- **X-guard:** Inverting and converting to saddle
- **Guard position:** Some guards can transition directly to saddle
- **Leg lock chains:** Natural progression from other leg lock positions

## Dangers

For the attacking player, achieving saddle position brings submission threats but also risk. The inverted or underneath positioning can make the attacking player vulnerable to arm submissions or guard reversals if not careful.

For the defending player, the danger is acute — the limited options and dominant control mean that submission risk is very high.

## Escaping Saddle

Escaping from saddle is difficult but possible:

- **Explosive extension:** Straightening the trapped leg powerfully to dislodge the attacker
- **Inversion:** Going completely inverted to change the mechanics
- **Countersub:** Attacking the attacking player's arm or neck while defending
- **Hip pressure:** Creating pressure with the hips to disrupt control

## Advanced Technique

The saddle position is considered advanced grappling. Beginners should prioritize fundamental leg lock positions before focusing on saddle mechanics. The position requires excellent body awareness and understanding of leg lock principles.

## Modern Development

Modern leg lock systems have refined saddle position mechanics significantly. Techniques once considered dangerous or impractical are now understood as high-percentage attacks with proper knowledge.

"""
    },

    "deep-half-guard": {
        "title": "Deep Half Guard",
        "category_slug": "guard",
        "summary": "An aggressive underneath half guard position where the bottom player drives underneath the opponent's base.",
        "content": """## Overview

Deep half guard is a guard position where the bottom grappler drives underneath the opponent, positioning themselves below and to the side of the top player's center of gravity. While it appears defensive or desperate at first glance, deep half guard is actually an aggressive attacking position with powerful sweeping mechanics.

The position is called "deep" because the bottom player is deeply underneath the opponent rather than engaging at the typical half guard distance.

## Key Mechanics

The bottom player:

- Drives the head and upper body underneath the opponent's body
- Maintains trap on one of the opponent's legs (half guard)
- Often secures a rear-facing underhook
- Uses shoulder and head placement to control positioning

This underneath position gives the bottom player significant sweeping power because they're directly below the opponent's center of gravity.

## Why Deep Half Works

Gravity favors sweeping from below. When the bottom player is underneath the opponent and can maintain control, they have tremendous sweeping power. The opponent's own weight becomes a liability in deep half.

## Sweeping from Deep Half

The primary deep half sweeps involve:

- **Hip bump/whip:** Explosive upward movement to flip the opponent
- **Back take:** Using underhook control to transition to back control
- **Turn to standing:** Pivot to get both players upright
- **Knee-up sweep:** Create space and reset positioning

## Underhook Importance

The underhook is critical in deep half. An underhook gives the bottom player tremendous control and enables most sweeps. Without the underhook, deep half becomes more defensive.

## Positional Variations

**Deep Half with Underhook:** The core aggressive version with maximum sweep potential.

**Head-and-Arm Pressure:** More defensive version where the bottom player focuses on preventing passing rather than immediate sweeping.

**Back-Facing Deep Half:** The bottom player faces away from the opponent, using different mechanics.

## Defense by Top Player

The top player defending against deep half should:

- Flatten the bottom player
- Eliminate the underhook
- Control the trapped leg tightly
- Use hand pressure to prevent the hip bump

## Transitioning Out

If the sweep doesn't work, the bottom player should transition to the next attack or move to a different guard position. Staying static in failed deep half is dangerous.

## Physical Demands

Deep half guard requires good hip flexibility, shoulder mobility, and explosive power. It's more physically demanding than some other guard positions but offers high-percentage sweeping rewards.

## Modern Application

Deep half has moved from a niche or desperation technique to a legitimate attacking system. Top competitors use deep half intentionally as part of their guard game.

"""
    },

    "rubber-guard": {
        "title": "Rubber Guard",
        "category_slug": "guard",
        "summary": "A high closed guard with an overhook controlling the opponent's head and arm, used for transitions and submissions.",
        "content": """## Overview

Rubber guard is a specialized closed guard variation where the bottom grappler has their legs locked around the opponent's torso and one arm (usually the arm-side arm) is wraped over the opponent's shoulder as an overhook. The combination of the closed guard lock and the overhook creates a very tight, controlling position.

The position is named for its appearance — it looks like the bottom player has wrapped around the opponent like a piece of rubber.

## Key Mechanics

The bottom player:

- Maintains closed guard leg lock
- Secures an overhook with one arm on the opponent's shoulder/arm
- Often has a grip with the other arm on the back or neck area
- Pulls the opponent down and in, breaking their posture completely

This creates one of the most inescapable guard positions from the bottom player's perspective.

## Submissions from Rubber Guard

**Armbar:** The overhook arm can transition to an armbar setup.

**Triangle Choke:** Transition to a tight triangle by moving one leg to the shoulder.

**Omoplata:** The overhook position naturally transitions to omoplata.

**Choke Variations:** Various chokes using the close control.

## Positional Control

One of rubber guard's primary benefits is positional control rather than immediate submissions. The opponent is completely controlled, unable to posture up or escape easily, and must make a defensive decision.

## Getting into Rubber Guard

Rubber guard typically develops from:

- Closed guard with collar tie control
- Breaking posture then establishing the overhook
- Direct entry by pulling and wrapping the arm
- Transitioning from other high-guard variations

## Dangers

The overhook creates submission threats for the top player as well. If the bottom player is careless with their arms, the opponent can attack for an armbar or other submission.

## Counters

The opponent can counter rubber guard by:

- **Breaking the leg lock:** Opening the guard to escape the position
- **Posture development:** Finding ways to straighten up despite the overhook
- **Hip escape:** Creating space to transition to another position
- **Arm submission:** Attacking the overhook arm for an armbar or other submission

## Transitions and Flow

Rubber guard is excellent for chaining into multiple attacks. The control allows the bottom player to:

- Transition to triangle
- Transition to omoplata
- Attack with the guard's submissions
- Move to a higher or more favorable guard position

## Modern Application

Rubber guard has gained popularity through high-level competitors and instructors who have refined the techniques and transitions. It's particularly useful against opponents who try to maintain posture and prevent the bottom player from working.

"""
    },

    "z-guard": {
        "title": "Z-Guard (Knee Shield)",
        "category_slug": "guard",
        "summary": "A half guard variation with the shin across the opponent's torso, creating distance and framing for sweeps.",
        "content": """## Overview

Z-guard, also called knee shield or knee shield guard, is a half-guard variation where the bottom grappler places their shin across the opponent's torso (perpendicular to the body) while maintaining a trapped leg between their own legs (the half-guard configuration). The shin creates a frame that manages distance and prevents the top player from flattening or passing.

The position is named "Z" because the bottom player's legs form a Z-shape when viewed from above.

## Key Mechanics

The bottom player:

- Maintains the half guard trap on one of the opponent's legs
- Places the other leg's shin across the opponent's torso as a shield
- Keeps hands ready for additional framing or attacking
- Uses the shin frame to prevent the top player from collapsing into them

This configuration combines the control of half guard with the distance management of the knee shield.

## The Shield Principle

The knee shield serves primarily as a barrier. It prevents the top player from achieving the flattened, heavy pressure position needed to pass the guard. As long as the knee shield frame remains intact, the bottom player maintains defensive integrity.

## Sweeping from Z-Guard

The knee shield creates natural sweeping opportunities:

- **Z-Guard Sweep:** Using the trapped leg and knee shield together to flip the opponent
- **Underhook Sweep:** If the bottom player establishes an underhook beneath the shield, powerful sweeps become available
- **Knee Strike Transition:** In no-gi, the bottom player can use the knee for striking (in certain rule sets)

## Maintaining the Frame

The key to successful Z-guard is maintaining the shin frame. If the top player flattens or removes the frame, the bottom player loses much of the position's benefit. The bottom player must actively protect and maintain the frame.

## Underhook Battle

Like standard half guard, Z-guard revolves around the underhook battle. If the bottom player secures an underhook, attacks become available. If the top player wins the underhook, passing improves significantly.

## Variations

**High Knee Shield:** The shin is placed higher up on the opponent's torso.

**Low Knee Shield:** The shin is placed lower, closer to the hip.

**Knee Shield with Collar Tie:** Adds collar control for additional attack options.

**Knee Shield with Under Pass Defense:** More defensive variation focused on preventing the pass.

## Transitions

From Z-guard, the bottom player can:

- Sweep to top position
- Transition to closed guard by bringing the free leg across
- Move to deep half guard variations
- Transition to open guard
- Attack with leg locks (in no-gi/leg lock-friendly rulesets)

## Role in Guard Progression

Z-guard is often taught as an intermediate guard position, bridging the gap between half guard and more complex open guards. Its relative simplicity and effectiveness make it valuable at all levels.

## Modern Emphasis

Z-guard has become increasingly popular in competition. Many modern grapplers use Z-guard as a primary guard variation, particularly in gi competition.

"""
    },

    "single-leg-x": {
        "title": "Single-Leg X",
        "category_slug": "leg-entanglement",
        "summary": "A leg entanglement position combining elements of X-guard with leg lock threats from underneath.",
        "content": """## Overview

Single-leg X (SLX) is a leg entanglement position that combines elements of X-guard (underneath control with inside thigh hook) with leg lock positioning. The bottom grappler controls one of the opponent's legs using an inside leg hook while positioning themselves underneath, creating both sweeping opportunities and foot lock threats.

The position is relatively new in the evolution of grappling, becoming prominent through the popularization of leg lock systems in modern competition.

## Key Mechanics

The bottom player:

- Uses an inside leg hook on the opponent's thigh (similar to X-guard)
- Positions themselves underneath the opponent's base
- Often uses foot placement on the opponent's hip for additional control
- Creates angles for heel hooks and other leg lock attacks

## Relation to X-Guard

Single-leg X is essentially a leg lock version of X-guard. While standard X-guard focuses on sweeping and positional advantage, single-leg X emphasizes leg lock attacks as the primary threat.

## Primary Attacks

From single-leg X, the main attacks are:

**Heel Hook:** The primary submission, applied by controlling the heel and rotating the trapped leg.

**Straight Ankle Lock:** A secondary option for foot lock.

**Back Take:** Can transition to back control using the leg control.

**Sweep:** Though less emphasized than leg locks, sweeping is possible from SLX.

## Entry Points

Single-leg X typically develops from:

- X-guard transitions where the focus shifts to leg locks
- Open guard leg lock entries
- Direct engagement pursuing leg lock opportunities
- Guard pass counters using leg lock principles

## Positional Advantages

The underneath positioning in single-leg X provides:

- Multiple angles for heel hook entry
- Lower risk position compared to some leg lock positions
- Transitional flexibility to other positions
- Good escape options if the submission isn't available

## Defense

The opponent with a trapped leg in single-leg X must:

- **Escape the position:** Use hip mobility and leg strength to dislodge the attacker
- **Defend submissions:** Understand leg lock defense principles
- **Counterattack:** Use arms or free leg to attack while defending
- **Invert:** Going inverted is often the primary defense

## Modern Leg Lock Systems

Single-leg X has become a fundamental position in modern leg lock systems, particularly those emphasizing heel hook attacks. Understanding SLX is now considered essential for leg lock competency.

## Transitioning

From single-leg X, grapplers can transition to:

- Heel hook finish
- Saddle position for increased control
- Standard ashi garami
- Back to guard positions
- Standing position

## Risk and Reward

Single-leg X offers high-percentage leg lock attacks but also carries risk. The leg lock-focused position means both players may be attacking legs, so timing and understanding of leg lock defense are critical.

"""
    },

    "50-50-guard": {
        "title": "50/50 Guard",
        "category_slug": "leg-entanglement",
        "summary": "A symmetrical leg entanglement position where both players have equal attacks and defenses, primarily leg locks.",
        "content": """## Overview

The 50/50 guard is a leg entanglement position where both grapplers have one leg trapped and equal access to leg lock submissions. Unlike other positions where one player has a clear advantage, the 50/50 is by design symmetrical — both the bottom and top player can attack heel hooks, footlocks, and sweeps simultaneously.

The position is relatively modern in grappling's evolution, gaining prominence through the systematization of leg lock attacks in the 21st century. In the 50/50, the bottom player has trapped one of the top player's legs while their own opposite leg is also trapped.

## Key Mechanics

In a true 50/50 position:

- Both players have one leg ensnared
- Both have access to footlock attacks
- Both can defend leg lock submissions simultaneously
- The position is the ultimate symmetrical contest of leg lock knowledge
- Whoever has superior leg lock offense and defense controls the exchange

## Positional Setup

The 50/50 typically develops from:

- Open guard leg lock transitions
- Failed leg lock entries that result in mutual entanglement
- Deliberate entry from far guard positions
- Scrambles where both players establish leg control

## Attacks from 50/50

Both players can simultaneously attack:

**Heel Hooks:** The primary submission from 50/50, available to both grapplers.

**Straight Ankle Locks:** A secondary option when heel hooks aren't available.

**Sweeps:** Despite the leg entanglement, sweeping options exist if one player executes faster.

## Modern Leg Lock Rules

The 50/50 guard became significantly more important after IBJJF and other rulesets began allowing heel hooks at higher belt levels. In rulesets that restrict heel hooks, 50/50 becomes less threatening. In open heel hook rulesets, 50/50 is a critical battleground.

## The Symmetry Problem

The fundamental challenge of 50/50 is its symmetry. Neither player has a clear technical advantage, so the exchange becomes a pure contest of:

- Leg lock knowledge and execution speed
- Heel hook defense understanding
- Hip mobility and flexibility
- Mental composure in a high-stakes position

## Escaping 50/50

To escape 50/50 without being submitted, a grappler must:

- Defend against simultaneous leg lock attacks
- Create space to dislodge one leg
- Invert or reposition to a more favorable entanglement
- Transition to a position where they have an advantage

## Competition Context

In rulesets where heel hooks are unrestricted, 50/50 becomes a common battle point in matches. Competitors develop deep systems for both attacking and defending from the position.

## Role in Leg Lock Systems

Modern leg lock systems treat 50/50 as a waypoint in a larger system. Rather than stalling in 50/50, practitioners learn to attack, defend, and transition to positions of advantage (like saddle position or single-leg X).
"""
    },

    "headquarters": {
        "title": "Headquarters",
        "category_slug": "transitional",
        "summary": "A standing or kneeling passing position with combat base, used as the launching pad for guard pass finishes.",
        "content": """## Overview

Headquarters (also called combat base or the passing position) is a standing or kneeling configuration where the passer establishes a strong, balanced base while beginning guard pass execution. It is not a dominant position in itself but rather a transitional posture from which passes are completed.

The term describes the strong, athletic stance grapplers use when actively working through guard — feet apart, knees slightly bent, weight distributed for power and mobility. Headquarters is fundamental to all guard passing concepts.

## Key Mechanics

A proper headquarters position features:

**Wide Base:** Feet spread approximately shoulder-width apart for stability.

**Bent Knees:** Slight knee flex provides explosive power and reduces vulnerability to sweeps.

**Upright Posture:** The passer maintains an upright torso to prevent guard player arm attacks and maintain leverage.

**Forward Pressure:** The passer's hips maintain contact or near-contact with the guard player.

**Combat Ready:** The passer is prepared to react to guard attacks, sweeps, or submissions while advancing the pass.

## Relationship to Guard Defense

Headquarters is the top player's counter to guard security. A guard player who is flattened or heavily pressured may be unable to launch sweeps or submissions from guard. The passer uses headquarters to:

- Maintain safety from footlocks and leg attacks
- Develop passing pressure
- Transition between passing angles
- Establish a foundation for guard pass completions

## Variations

**Standing Headquarters:** Completely on the feet, used against open guard and far guard positions.

**Kneeling Headquarters:** One or both knees down, used in pass transitions or when closing distance to the guard player.

**Combat Base with Hand Contact:** Hands frame on the guard player's body for additional control and reference.

## Transitioning Through Headquarters

Effective guard passing often involves moving through headquarters multiple times:

1. Establish headquarters distance
2. Attack passing angle
3. Guard player escapes or improves position
4. Reset to headquarters
5. Attack a different passing lane

## Relationship to Guard Passing Systems

Headquarters is the foundational posture for all guard passing. Whether attacking with knee slice, leg drag, toreando, or pressure passing, the passer must establish headquarters control first.

## Balance and Weight Distribution

Superior headquarters positioning often determines passing success more than any specific technique. A passer with:

- Better balance
- More stable weight distribution
- Quicker lateral movement through headquarters
- Better pressure maintenance

will pass guard more consistently than a passer with technically flashy but poorly-grounded passes.

## Teaching Progression

Headquarters is typically taught early in passing curricula because:

- It provides the fundamental stance for all passes
- It offers immediate feedback (balance, pressure)
- It teaches the importance of base before technique
- It develops the kinesthetic understanding needed for advanced passing
"""
    },
}

SUBMISSIONS = {
    "armbar": {
        "title": "Armbar",
        "category_slug": "submission",
        "summary": "A joint lock that hyperextends the elbow by isolating the arm between the legs and hips.",
        "content": """## Overview

The armbar (also called arm lock or juji gatame in Japanese) is a joint lock submission that hyperextends the opponent's elbow. The attacker isolates one of the opponent's arms, controls it between their legs, and applies upward hip pressure against the elbow joint while pulling the wrist downward. It is one of the most versatile and commonly used submissions across all grappling arts.

The armbar can be applied from nearly every position — mount, guard, side control, back control, and even standing — making it one of the first submissions taught to beginners and one of the most studied techniques at the highest levels.

## Mechanics

The key mechanical principles of the armbar are:

**Arm Isolation:** The attacker must control the opponent's arm, typically by hugging it to their chest with the thumb pointing up.

**Hip Placement:** The hips must be positioned tight against the opponent's shoulder/upper arm, creating a fulcrum point at the elbow.

**Leg Control:** Both legs cross over the opponent's body — one across the face/chest to prevent posturing, one across the torso to anchor the position.

**Breaking Mechanics:** The attacker lifts their hips into the elbow while pulling the wrist toward their chest. The combined forces hyperextend the joint.

## Variations

**From Mount:** The attacker controls posture and arm position, pivots the hips, and executes the armbar from the dominant position.

**From Closed Guard:** One of the most accessible entries — the attacker controls the collar, pivots, clears the head with one leg, and extends.

**From Side Control:** Using kimura grip transition to isolate the arm before armbar.

**Straight Armbar:** Both legs are extended straight, commonly seen in wrestling and no-gi.

**Figure-Four Armbar:** The legs create a figure-four grip for additional security.

**Extended Armbar:** The attacker is fully extended, applying maximum pressure.

## Defense

The primary defenses against the armbar are:

**Stacking:** Driving forward to compress the attacker and relieve elbow pressure.

**Hitchhiker Escape:** Rolling toward the thumb to reduce armbar pressure and potentially escape.

**Grip Fighting:** Clasping the hands to prevent arm extension.

**Arm Position:** Bending the elbow before the armbar is fully locked to prevent hyperextension.

## Competition Statistics

The armbar is one of the most successful submissions in competitive history across judo, BJJ, and MMA. Roger Gracie, widely considered the greatest BJJ competitor of all time, built his competition career around the armbar from mount.

## Teaching Progression

Most schools teach armbar as a foundational technique because:

- Multiple entries from common positions
- Clear mechanical principles
- Defense strategies are learnable
- Variations adapt to different body types and strengths

"""
    },

    "triangle-choke": {
        "title": "Triangle Choke",
        "category_slug": "submission",
        "summary": "A blood choke applied using the legs as a triangle to compress the neck and carotid arteries.",
        "content": """## Overview

The triangle choke (also called triangle or sankaku jime in Japanese) is a blood choke submission applied using the legs to create a triangular frame around the opponent's neck and arm. One leg passes around the neck while the other leg creates the base of the triangle, and the legs are locked together to apply choking pressure.

The triangle choke is characterized by its high-percentage success rate, particularly from closed guard, and its reliance on leg strength rather than arm strength.

## Basic Mechanics

**Leg Positioning:** One leg wraps around the opponent's neck and shoulder, while the other leg creates the base of the triangle by passing over the opponent's arm on the opposite side.

**Lock Completion:** The legs are locked by crossing the ankle over the shin, creating a locked triangle around the opponent's neck and arm.

**Compression:** Pressure is applied by tightening the triangle and pulling the opponent's body forward to increase neck compression.

**Target:** The choke compresses both carotid arteries, restricting blood flow to the brain.

## Entries

**From Closed Guard:** The most common and reliable entry. The guard player creates a high guard, pivots the hips, and locks the triangle.

**From Open Guard:** Using leg placement and hand control to set up the triangle position.

**From Mount:** Transitioning from threatened armbar or other mount attacks.

**From Side Control:** Less common but possible with good positioning.

**Standing Triangle:** Jumping to the opponent's back and locking a triangle choke.

## Tightening and Finishing

A triangle isn't finished simply by locking the legs. To finish the choke:

- **Pull the opponent down:** Use the hands to pull the opponent's head and body forward
- **Rotate the hips:** Adjust hip angle to increase pressure
- **Tighten the triangle:** Squeeze the legs together to reduce space
- **Maintain connection:** Keep the opponent pulled in rather than pushing away

## Defense

Triangle defenses include:

**Stacking:** Driving forward to compress the triangle and reduce effectiveness.

**Posture:** Maintaining an upright posture to prevent the choke mechanics from working.

**Escape:** Creating space by turning into the attacking player and shrimping out.

**Arm Position:** Removing the trapped arm from the triangle before it's locked.

**Prevention:** Preventing the triangle setup before it's fully formed.

## Variations

**Triangle from Guard:** The fundamental form

**Inverted Triangle:** The attacker is inverted or upside-down

**Standing Triangle:** Applied while standing or using leverage from standing

**Mounted Triangle:** Applied from mount position

## Known for:

The triangle choke is known for its democratic nature — small grapplers can finish large opponents using the triangle because it relies on leg strength and positioning rather than size. Conversely, strong leg defense and explosive counters are very effective against the triangle.

"""
    },

    "guillotine-choke": {
        "title": "Guillotine Choke",
        "category_slug": "submission",
        "summary": "A front headlock choke applied with one arm wrapped around the opponent's neck from the front.",
        "content": """## Overview

The guillotine choke (also called front choke or mata leão in Portuguese, meaning "lion killer") is a blood choke applied by wrapping one arm around the opponent's neck from the front while using body pressure and often the guard to compress the carotid arteries.

The guillotine is one of the highest-percentage submissions in grappling, available from numerous positions (guard, front headlock, standing clinch), and is effective in both gi and no-gi competition.

## Basic Mechanics

**Arm Position:** One arm wraps around the opponent's neck, with the crook of the elbow under the chin or aligned with the carotid arteries.

**Second Arm Control:** The other hand typically grabs the bicep of the choking arm, clasps behind the head, or pulls the opponent into the choke.

**Choke Application:** Pressure is applied by squeezing the arms together, pulling the opponent's head into the choke, and using bodyweight to compress the neck.

**Target:** Blood flow restriction via carotid compression rather than airway restriction.

## Entries

**From Closed Guard:** Guard player pulls the head down for a guillotine entry with arm wrapping from below.

**From Front Headlock:** Direct application after establishing a front headlock position.

**From Standing:** Snap down into a front headlock and guillotine in one motion.

**From Turtle Position:** Wrap from the back as the opponent turtles.

**From Arm Drag:** Transition during arm drag to back-take positions.

## Variations

**Standard Guillotine:** The fundamental wrapped position.

**High Elbow Guillotine:** The elbow placement is higher, compressing different neck anatomy.

**Low Elbow Guillotine:** The elbow is lower, creating a different pressure angle.

**Marcelotine:** Marcelo Garcia's famous guillotine variation with exceptional finishing rate.

**Bravo Guillotine:** Eddie Bravo's system emphasizing no-gi guillotine details.

**Reverse Guillotine:** Applied from behind rather than from the front.

## Tightening Mechanics

Proper guillotine finishing requires:

- **Correct arm position:** The crook of the elbow must be tight against the neck
- **Body pressure:** Using the body and legs to add pressure
- **Head pulling:** Pulling the opponent's head into the choke continuously
- **Timing:** Recognizing when pressure is sufficient to take the submission

## Defense

Guillotine defenses include:

**Chin Tuck:** Tucking the chin to prevent the arm from sinking properly.

**Hip Escape:** Creating space and disengaging from the choke.

**Shoulder Pressure:** Pressing the opponent's shoulder to relieve pressure.

**Rolling:** Rolling out of the choke to escape.

**Prevention:** Not allowing the arm to wrap in the first place.

## Competition Dominance

The guillotine's prevalence in competition is remarkable — it appears from so many positions and is so high-percentage that beginners and advanced grapplers both rely on it heavily.

"""
    },

    "kimura": {
        "title": "Kimura",
        "category_slug": "submission",
        "summary": "A shoulder lock applying inward rotational pressure to the shoulder joint, trapping both arms.",
        "content": """## Overview

The kimura (also called figure-four armlock or ude garami in Japanese judo) is a shoulder lock submission that applies inward rotational force to the shoulder joint. The attacker traps the opponent's arm and uses their own arm and leg to create a lever that internally rotates the shoulder, potentially causing a rotator cuff injury or dislocation.

The kimura is available from many positions and is highly effective because it attacks the shoulder — a joint with limited range of motion in the rotational direction being attacked.

## Basic Mechanics

**Arm Trapping:** The attacker controls the opponent's arm, typically by pinning it across their own body.

**Grip Formation:** The attacker creates a figure-four grip: their hand grabs their own wrist, with the opponent's arm trapped between the attacker's arms.

**Lever Creation:** Using body positioning and hip movement, the attacker creates a lever that applies inward rotational force.

**Breaking Mechanics:** Pressing forward with the hips or pulling upward on the trapped arm applies pressure to the shoulder joint.

## Entries

**From Closed Guard:** One of the primary entries — the guard player controls the arm and establishes the figure-four grip.

**From Mount:** The mounted player controls the far arm and sets up a kimura.

**From Side Control:** The side control player secures the kimura from the top position.

**From Half Guard:** Possible with the right arm positioning and underhook.

**From Standing:** Can be applied from standing clinch positions.

## Variations

**Standard Kimura:** The basic figure-four lock.

**High Elbow Kimura:** The grip is positioned higher on the arm.

**Arm Triangle Kimura:** Combines kimura control with arm triangle threat.

**Kimura Grip from Bottom:** Securing the grip while on the bottom in various positions.

**Reverse Kimura (Americana):** Similar position but with outward rotation instead.

## Gripping Details

The grip itself is crucial to kimura finishing:

- **Hand Position:** One hand must firmly grasp the opposite wrist
- **Arm Position:** The opponent's arm must be positioned correctly relative to the attacker's body
- **Wrist Alignment:** The opponent's wrist angle affects pressure application

## Defense

Kimura defenses include:

**Grip Fighting:** Preventing the grip from being established in the first place.

**Arm Escape:** Removing the trapped arm from the lock before pressure increases.

**Angle Adjustment:** Changing body position to relieve pressure.

**Rotate Into:** Rotating the shoulder in the direction of pressure to escape.

**Flexibility:** Superior shoulder flexibility makes kimura significantly less effective.

## Submission vs. Control

The kimura grip itself is often used as control rather than an immediate submission. Many grapplers use the kimura grip to control an opponent's arm while advancing position or setting up other attacks.

"""
    },

    "americana": {
        "title": "Americana",
        "category_slug": "submission",
        "summary": "A shoulder lock applying outward rotational pressure, the reverse-rotation counterpart to the kimura.",
        "content": """## Overview

The americana (also called far-side keylock or ude garami reverse) is a shoulder lock submission that applies outward rotational force to the shoulder joint. It is mechanically the opposite rotation of the kimura — while the kimura rotates the shoulder internally, the americana rotates it externally, attacking the rotator cuff from a different angle.

The americana is particularly effective from dominant positions like mount and side control, where the attacker has superior positioning.

## Basic Mechanics

**Arm Trapping:** The attacker controls the opponent's arm, typically from a top position.

**Grip Formation:** The attacker creates a figure-four grip with the opponent's arm, but with the lever arm positioned to apply outward rotation.

**Lever Creation:** Using the attacker's arms and body position, outward rotational force is applied to the shoulder.

**Breaking Mechanics:** Pressing downward or pulling outward applies pressure to the shoulder joint in the opposite direction from a kimura.

**Target:** The rotator cuff and shoulder joint in external rotation.

## Entries

**From Mount:** The most common entry — the mounted player controls the far arm.

**From Side Control:** Another dominant entry from side control positioning.

**From North-South Position:** Possible when the attacker is perpendicular to the opponent.

**From Back Control:** Can transition to americana from back position with arm control.

**From Arm Drag:** Possible as a transition when arm control is established.

## Variations

**Standard Americana:** The basic figure-four lock with outward rotation.

**High Americana:** The grip is positioned higher on the arm.

**Low Americana:** The grip is positioned lower toward the wrist.

**Reverse Grip Americana:** Different hand positioning creating a variation of the lock.

## Differences from Kimura

Though mechanically similar in structure, americana and kimura differ significantly:

- **Direction:** Americana rotates externally, kimura rotates internally
- **Positions:** Americana is more effective from top positions, kimura from guard
- **Pressure Feel:** The pressure sensation is distinctly different
- **Defenses:** Different defensive mechanics work better for each

## Tap Rate

The americana is known for a high tap rate, particularly from mounted positions where the attacker has significant weight and positional advantage. Opponents often tap relatively quickly rather than risking shoulder damage.

## Defense

Americana defenses include:

**Grip Fighting:** Preventing or breaking the figure-four grip.

**Shoulder Flexibility:** Allowing external rotation without damage.

**Position Escape:** Escaping the dominant position before the americana is locked.

**Turning Into:** Rotating toward the attacker to relieve pressure.

**Bridge and Escape:** Creating space and transitioning out.

## Comparison to Kimura

The americana and kimura are often taught together because they use the same grip structure but apply opposite rotational forces. Understanding both gives a grappler excellent shoulder lock options from multiple positions.

"""
    },

    "omoplata": {
        "title": "Omoplata",
        "category_slug": "submission",
        "summary": "A shoulder lock using the legs to control the opponent's arm and apply external rotation to the shoulder.",
        "content": """## Overview

The omoplata (also called the shoulder wheel or omo plata in Brazilian Portuguese) is a shoulder lock where the attacking player uses their legs to trap and control the opponent's arm, applying outward rotational pressure to the shoulder joint. Unlike arm-based shoulder locks like the kimura or americana, the omoplata uses leg control, making it unique in shoulder lock mechanics.

The omoplata is particularly effective from guard positions where leg control is strongest and has seen increased application in modern competition.

## Basic Mechanics

**Arm Control:** The attacker traps the opponent's arm using their legs, typically by placing one leg across the opponent's arm and upper back.

**Position Setup:** The attacking player positions their hips perpendicular to the opponent, with the trapped arm under control.

**Rotation Application:** Using hip pressure and leg control, outward rotation is applied to the shoulder.

**Finishing:** The attacker either applies enough pressure directly or uses hand control to intensify the submission.

## Entries

**From Closed Guard:** A primary entry where the guard player controls the arm with the legs.

**From Rubber Guard:** The overhook position naturally transitions to omoplata.

**From High Guard:** The elevated leg position enables omoplata setups.

**From Mount:** Possible with good arm positioning.

**From Side Control:** Can transition to omoplata with proper positioning.

## Finishing Methods

The omoplata can be finished in multiple ways:

**Leg Pressure:** Pure leg pressure on the trapped arm and shoulder.

**Hand Finish:** Grabbing the opponent's wrist and pulling to intensify rotation.

**Hip Pressure:** Driving the hips to apply additional force.

**Transition to Armbar:** Sometimes the omoplata transitions to an armbar finish instead of straight shoulder lock completion.

## Variations

**High Omoplata:** The legs control the arm higher up.

**Low Omoplata:** The legs control the arm lower, near the wrist.

**Inverted Omoplata:** The attacker inverts to apply different pressure angles.

**Omoplata Armbar:** Transitioning from omoplata to armbar mechanics.

## Defense

Omoplata defenses include:

**Rolling Over:** The top player can attempt to roll over the omoplata to relieve pressure.

**Arm Escape:** Removing the arm from leg control before the lock is complete.

**Leg Removal:** Physically removing the attacker's leg control.

**Shoulder Flexibility:** Allowing external rotation without injury.

**Prevention:** Not allowing the position to develop in the first place.

## Unique Aspects

The omoplata is distinctive because:

- It's one of the few submissions emphasizing leg control over arm control
- It requires body flexibility and hip mobility from the attacker
- It transitions naturally from guard positions
- It has high failure-to-armbar-transition rate, making it unpredictable

"""
    },

    "darce-choke": {
        "title": "D'Arce Choke",
        "category_slug": "submission",
        "summary": "An arm-in head and arm choke applied with control of the neck and one arm wrapped around it.",
        "content": """## Overview

The d'arce choke (also called the brabo choke or arm-in choke) is a blood choke applied from positions with head and arm control, where one of the opponent's arms is wrapped inside the attacker's choking arm. Named after John d'Arce, who popularized it in competition, the d'arce is increasingly common in modern grappling.

The position is distinct from the guillotine because one of the opponent's arms is trapped inside the attacker's choking arm, changing the mechanics and escape options.

## Basic Mechanics

**Arm-In Positioning:** The opponent's arm extends forward into the attacker's choking arm (the arm is "in" the choke).

**Neck Control:** The attacker wraps the choking arm around the opponent's neck.

**Secondary Control:** The other arm typically controls the opponent's near arm or clasps with the first arm to complete the lock.

**Choke Application:** Pressure is applied by squeezing the arms together and pulling the opponent's head into the choke.

## Entries

**From Front Headlock:** Using the arm-in position that naturally occurs in front headlock to set up the d'arce.

**From Turtle Position:** Wrapping from behind when the opponent turtles.

**From Half Guard:** Transitioning when the opponent's arm is positioned correctly.

**From Side Control:** Possible with the right arm positioning.

**From Guard:** Pulling the head down with an arm-in configuration.

## Variations

**High D'Arce:** The choking arm is positioned higher on the neck.

**Low D'Arce:** The choking arm is positioned lower.

**Side D'Arce:** Applied from a perpendicular angle.

**D'Arce to Anaconda Transition:** Transitioning between arm-in choke variations.

## Differences from Guillotine

The d'arce differs from the guillotine in critical ways:

- **Arm Position:** The opponent's arm is inside the choke vs. outside
- **Setup Positions:** Different positions favor each choke
- **Defenses:** The trapped arm changes available defenses
- **Mechanics:** The mechanics and pressure angles differ significantly

## Defense

D'Arce defenses include:

**Arm Extraction:** Removing the trapped arm from the choke.

**Turning Into:** Rotating into the attacker to relieve pressure.

**Hip Escape:** Creating space and changing position.

**Grip Breaking:** Breaking the attacker's grip before pressure increases.

**Prevention:** Preventing the arm-in position in the first place.

## Technical Details

Successfully finishing the d'arce requires understanding:

- Proper arm-in positioning
- When to apply pressure vs. when to adjust positioning
- How to tighten the choke progressively
- The balance between arm control and neck pressure

## Modern Popularity

The d'arce has seen increased use in modern competition, particularly among grapplers who understand the mechanics deeply and can chain it with other attacks.

"""
    },

    "heel-hook": {
        "title": "Heel Hook",
        "category_slug": "submission",
        "summary": "A dangerous leg lock applying rotational pressure to the knee by controlling the heel.",
        "content": """## Overview

The heel hook is a leg lock submission where the attacker controls the opponent's heel while using their body and legs to apply rotational force to the knee joint. The heel hook is considered one of the most dangerous submissions in grappling because the knee has limited tolerance for rotational stress and heel hook injuries can be severe.

The heel hook is restricted or banned in many competition rulesets for beginners and lower-level competitors due to injury risk, but is allowed in advanced no-gi competition, ADCC, and other submission-heavy formats.

## Basic Mechanics

**Heel Control:** The attacker controls the opponent's heel, typically by placing it in the crook of their elbow or controlling it with their hands.

**Body Position:** The attacker uses their body positioning to create rotational leverage on the knee.

**Rotational Force:** By rotating the attacker's hips or moving the opponent's foot in a specific direction, rotational stress is applied to the knee joint.

**Submission:** The opponent taps when the rotational pressure becomes unbearable or risks ligament damage.

## Positions for Heel Hooks

**Ashi Garami:** The primary leg lock position for heel hooks, where both attacker's legs control one opponent leg.

**Saddle Position:** An advanced position providing maximum control and danger.

**Single-Leg X:** An underneath position offering heel hook opportunities.

**Half Guard:** With proper positioning, heel hooks can be applied from half guard.

**Open Guard:** Advanced practitioners can heel hook from open guard positions.

## Variations

**Straight Heel Hook:** Direct rotational pressure with minimal complexity.

**Hook and Reap:** Establishing the heel hook with knee reap positioning.

**Inside Heel Hook:** The attacker's leg position is on the inside of the opponent's leg.

**Outside Heel Hook:** Different leg positioning creating an outside heel hook angle.

**Elevated Heel Hook:** The attacker's hip position is higher than the opponent's leg.

## Danger and Injury Risk

Heel hooks are considered dangerous because:

- The knee's rotational tolerance is limited
- Injuries can occur suddenly without much warning
- Ligament damage (ACL, MCL, PCL) can be severe
- Cartilage damage can have long-term consequences

## Defenses

Heel hook defenses include:

**Inversion:** Going completely inverted to change the mechanics.

**Leg Extraction:** Removing the trapped leg from the attacker's control.

**Pressure Adjustment:** Moving to reduce rotational stress.

**Position Escape:** Disengaging from the heel hook position entirely.

**Prevention:** Avoiding entering heel hook positions with experienced heel hook practitioners.

## Rule Variations

Different competition formats have different heel hook rules:

- **IBJJF:** Banned for white, blue, and purple belts; restricted for brown and black belts
- **ADCC:** Allowed at all levels
- **No-Gi:** Generally allowed in higher-level competition
- **Submission-First:** Often emphasized given the submission-heavy rule set

## Tap vs. Injury

Heel hook training requires understanding:

- Clear communication about intensity levels
- Tap rate understanding — tapping before significant danger
- Partner's comfort level with leg lock intensity
- The difference between pressure and damage

## Modern Evolution

Modern leg lock systems have refined heel hook entries and mechanics significantly, making the technique higher-percentage when applied correctly while also emphasizing safety and controlled tapping.

"""
    },

    "triangle-from-bottom": {
        "title": "Mounted Triangle (Triangle from Mount)",
        "category_slug": "submission",
        "summary": "A triangle choke applied while mounted on the opponent, combining mount's dominance with triangle mechanics.",
        "content": """## Overview

The mounted triangle (also called triangle from mount) is a triangle choke applied while the attacker maintains a mounted position on the opponent. The position combines the dominance of mount with the leg-based choking mechanics of the triangle, creating a high-percentage submission that appears from a position of control.

The mounted triangle is often overlooked in favor of the armbar from mount, but offers distinct advantages and represents an important variation in mount attacks.

## Basic Mechanics

**Mount Position Maintenance:** The attacker starts with full mount and maintains it while setting up the triangle.

**Triangle Setup:** Using the mount position as a platform, the attacker creates a triangle around the opponent's neck and arm.

**Positioning:** Unlike guard triangle, the mounted triangle uses the mounted player's momentum and positioning.

**Completion:** Applying pressure by pulling the opponent's body forward or adjusting hip positioning.

## Entry from Mount

The typical mounted triangle entry involves:

1. Positioning for an armbar or other mount submission
2. Sensing the opponent's defensive response
3. Transitioning the legs to triangle position
4. Using the mount leverage to tighten the triangle

## Advantages

**Dominance:** The attacker maintains mount dominance while attacking.

**Difficulty Escaping:** The opponent is in a dominated position with limited escape options.

**Pressure Application:** Mount allows for explosive pressure increases.

**Transition Safety:** If the triangle isn't ideal, the attacker can transition to other mount attacks.

## Variations

**High Mount Triangle:** Executed from high mount position.

**Low Mount Triangle:** Applied from lower mount with different mechanics.

**Mounted Triangle with Hip Control:** Using hip positioning to maximize pressure.

## Challenges

**Setup Time:** Creating the triangle from mount requires setup that gives the opponent defensive opportunities.

**Positioning Difficulty:** The geometric positioning required is more complex than some mount attacks.

**Mount Loss Risk:** During transition, the attacker might lose dominant mount position.

## Defense

Mounted triangle defenses include:

**Stack:** Compressing the triangle by stacking forward.

**Arm Removal:** Removing the trapped arm before the choke completes.

**Hip Escape:** Creating space to escape mount and the triangle.

**Posture:** Maintaining posture to prevent choke compression.

## Position Development

Unlike the armbar from mount, which is often taught early, the mounted triangle is sometimes not emphasized in basic curricula. Developing the position requires understanding both mount control and triangle mechanics.

## Submission Rate

In competition, the mounted triangle has a respectable but lower finish rate than the armbar from mount, making it more of a supplementary attack in mount rather than the primary submission threat.

"""
    },

    "rear-naked-choke": {
        "title": "Rear Naked Choke",
        "category_slug": "submission",
        "summary": "A blood choke applied from behind, compressing both carotid arteries using the forearm and arm.",
        "content": """## Overview

The rear naked choke (RNC), also called the mata leão in Portuguese, is a blood choke applied from behind an opponent where the attacker wraps one arm around the opponent's neck while using the other arm to reinforce the hold. It is considered the highest-percentage submission in competitive grappling and mixed martial arts, largely because the attacker applies it from the back — the single most dominant position in the sport.

The technique requires no gi grips and works identically in gi and no-gi competition, making it universally applicable across all grappling disciplines.

## Mechanics

The attacker wraps one arm around the opponent's neck, placing the crook of the elbow directly under the chin. The choking arm grabs the bicep of the free arm, and the free hand is placed behind the opponent's head or clasps the opposite bicep. By squeezing the arms together and driving the head forward, pressure is applied to both sides of the neck simultaneously.

The choke works by compressing the carotid arteries rather than the trachea, making it a blood choke rather than an air choke. A properly applied RNC can render an opponent unconscious in as little as 3-5 seconds.

## Proper Arm Positioning

The most critical element is arm positioning. The crook of the elbow must be directly under the chin. If the forearm rides up onto the jaw or trachea, the choke becomes significantly less effective and uncomfortable rather than dangerous.

## Chin Tuck Defense

A common error is allowing the opponent to tuck their chin, which forces the forearm across the jaw or trachea rather than the neck. Experienced grapplers address this by first establishing a body triangle or strong seatbelt grip, then working to clear the chin using the blade of the forearm, forehead pressure, or transitioning to a short choke.

## Entries

The RNC is most commonly entered from back control, but can also be applied from:

- Turtle position (as a rolling back take)
- Side control transitions
- Standing back clinch
- Front headlock snap-backs
- Arm drag transitions

## Short Choke Variation

The short choke (also called the anaconda variation) modifies the basic RNC mechanics when the opponent is defending the chin. Different hand positioning and pressure angles are used to attack the neck despite chin defense.

## Competition Results

The rear naked choke is statistically the most successful submission in UFC history and is among the top finishing techniques at ADCC. Its dominance across rulesets and weight classes makes it one of the first submissions taught to beginners and one of the last techniques masters are still refining.

## Defense

RNC defenses are limited but include:

**Chin Defense:** Tucking the chin to prevent clean carotid compression.

**Escape Timing:** Moving out of back control before the choke is locked.

**Arm Positioning:** Positioning the arms to prevent the lock.

**Rolling:** Explosive rolling to dislodge the attacker.

"""
    },

    "toe-hold": {
        "title": "Toe Hold",
        "category_slug": "submission",
        "summary": "An ankle/foot rotation lock that compresses and rotates the foot using the toes and foot mechanics.",
        "content": """## Overview

The toe hold (also called a toe lock or torsion ankle lock) is a leg lock submission that attacks the ankle and foot through rotational mechanics. The attacker controls the opponent's foot and applies rotational pressure, compressing the ankle joint and potentially causing torsional damage to ligaments and joints.

The toe hold is primarily available from leg entanglement positions like ashi garami, 50/50 guard, and saddle position. It is considered one of the fundamental leg lock attacks in modern grappling systems.

## Mechanics

The toe hold works by:

**Foot Control:** The attacker secures the opponent's foot, typically by clasping the toes or forefoot with both hands or one hand and a leg.

**Rotational Pressure:** The attacker rotates the foot and ankle through mechanical advantage, applying torsional stress to the ankle joint.

**Compression:** Simultaneously, the attacker may compress the foot against their own body, creating joint compression.

**Target:** The ankle joint itself is the primary target, with potential damage to ligaments and connective tissue.

## Entries

The toe hold is most commonly entered from:

- Ashi garami position
- 50/50 guard
- Saddle position
- Outside ashi garami
- Various leg lock scrambles

## Variations

**Standard Toe Hold:** Both hands control the foot for maximum rotational power.

**Heel Hook to Toe Hold Transition:** Converting from a heel hook position to a toe hold if the heel hook isn't working.

**Foot Lock Transition:** Often paired with straight ankle lock attempts.

## Defense

Defending against a toe hold requires:

- **Foot Positioning:** Keeping the foot positioned to prevent rotational pressure
- **Ankle Mobility:** Being flexible enough to accommodate the rotation without injury
- **Countertattack:** Using arm control to attack the opponent's leg or position
- **Escape:** Dislodging the leg by creating space and movement

## Submission Mechanics

A properly applied toe hold can force submission through:

- Ankle joint pain
- Ligament stress and potential damage
- Foot cramping
- General joint discomfort leading to tapping

## Modern Leg Lock Systems

The toe hold is a standard part of modern leg lock curricula. Grapplers learning leg locks typically learn toe holds alongside heel hooks and straight ankle locks as part of the fundamental submissions available from leg entanglements.

## Rulesets and Legality

In most rulesets that permit leg locks, toe holds are legal at all belt levels. Some rulesets have historically restricted them, but modern standards generally allow unrestricted leg lock submissions at higher belt levels.
"""
    },

    "kneebar": {
        "title": "Kneebar",
        "category_slug": "submission",
        "summary": "A joint lock that hyperextends the knee using leverage and leg positioning.",
        "content": """## Overview

The kneebar (also called knee lock or ひざ絞め in Japanese) is a leg lock submission that applies hyperextension pressure to the knee joint. The attacker controls the opponent's leg and applies direct pressure to hyperextend the knee, typically using their own legs or torso as a fulcrum.

The kneebar has gained significant prominence in modern leg lock systems and is considered one of the primary submissions from various leg entanglement positions.

## Mechanics

The kneebar operates by:

**Leg Isolation:** The attacker controls and isolates one of the opponent's legs.

**Fulcrum Placement:** The attacker's body (typically hips, torso, or legs) creates a fulcrum point against the opponent's knee.

**Hyperextension:** The attacker uses leverage to hyperextend the knee joint, applying stretching pressure.

**Submission Force:** The hyperextension stress forces submission or risks ligament damage.

## Common Positions for Kneebars

Kneebars are available from:

- Saddle position (the most dominant for kneebar setup)
- Ashi garami variations
- Leg entanglement positions
- Top leg lock positions
- Some open guard transitions

## Variations

**Saddle Kneebar:** Applied from saddle position with the attacker's legs wrapped around the opponent's leg.

**Inside Kneebar:** Using an inside leg position for control.

**Belly-Down Kneebar:** Controlling the leg while lying on the opponent for additional pressure.

## Defense

Defending against a kneebar requires:

- **Escape Timing:** Moving out of position before the lock is fully secured
- **Leg Strength:** Using quad strength to resist hyperextension
- **Positional Awareness:** Understanding kneebar-favorable positions and avoiding them
- **Counterattack:** Using arm control to attack the top player while defending

## Comparison to Heel Hook

The kneebar and heel hook are both leg lock submissions, but they:

- Attack different joints (knee vs. ankle)
- Apply different force vectors (hyperextension vs. rotation)
- Are available from slightly different positions
- Have different defense strategies

## Modern Leg Lock Ranking

In modern grappling, kneebars rank alongside heel hooks and straight ankle locks as fundamental leg lock submissions. All three are essential skills in leg lock-heavy rulesets.

## Teaching Progression

Kneebars are typically taught after the heel hook in leg lock curricula, as they require similar positional understanding but apply different mechanical principles.
"""
    },

    "straight-ankle-lock": {
        "title": "Straight Ankle Lock",
        "category_slug": "submission",
        "summary": "The foundational ankle lock that hyperextends the foot and ankle joint.",
        "content": """## Overview

The straight ankle lock (also called straight foot lock, ankle lock, or ashigatame) is the most basic and fundamental leg lock submission in grappling. The attacker controls the opponent's ankle and applies direct hyperextension pressure, compressing and stretching the ankle joint until the opponent submits or risks foot and ankle injury.

The straight ankle lock is the first leg lock taught to most grapplers and remains one of the highest-percentage submissions across all rulesets and skill levels.

## Mechanics

The straight ankle lock works by:

**Ankle Control:** The attacker controls the opponent's foot, typically by wrapping both hands around the ankle or foot.

**Fulcrum Positioning:** The attacker may use their own body or legs as a fulcrum to amplify pressure.

**Hyperextension:** The attacker applies direct upward or backward pressure on the foot, hyperextending the ankle joint.

**Pressure Application:** The force is applied to the ankle joint itself, causing joint stress.

## Basic Entry

The straight ankle lock can be entered from:

- Guard position (wrapping the foot)
- Leg entanglement positions
- Transitional positions during scrambles
- Almost any position where foot control is established

## Variations

**Foot Lock from Guard:** Wrapping the opponent's ankle while in open guard, then extending the leg.

**Straight Ankle Lock from Top:** Controlling the opponent's foot from a top position like side control.

**Heel-to-Throat Position:** Controlling the foot against the throat for additional pressure.

**Compression Angle Lock:** Adding compression to the ankle joint for increased pressure.

## Defense

Defending against a straight ankle lock involves:

- **Footwork:** Positioning the foot to distribute pressure across the entire joint
- **Flexibility:** Being mobile enough to prevent hyperextension
- **Timing:** Escaping before full lock is achieved
- **Positioning:** Avoiding foot lock positions entirely

## Submission Speed

The straight ankle lock is known for:

- Quick submission times when properly applied
- Clear feedback to the defending grappler
- Minimal ambiguity about submission completion
- Immediate and obvious joint stress

## Historical Significance

The straight ankle lock is one of the oldest leg lock submissions and appears in traditional judo and wrestling. Modern BJJ leg lock systems build upon the straight ankle lock foundation, but it remains the most universal and fundamental foot lock.

## Teaching Progression

Straight ankle locks are typically taught early in leg lock curricula because:

- Simple mechanics and clear application
- Multiple entry points from common positions
- Good learning tool for understanding leg lock pressure
- High percentage at all skill levels
"""
    },

    "ezekiel-choke": {
        "title": "Ezekiel Choke",
        "category_slug": "submission",
        "summary": "A gi choke applied using the sleeve as a lapel, compressing the neck from inside the guard or mount.",
        "content": """## Overview

The ezekiel choke (also called sleeve choke or inside sleeve choke) is a gi-specific blood choke that uses the opponent's own sleeve as a choking element. One hand controls the opponent's sleeve near the wrist while the other hand applies pressure against the neck, using the sleeve fabric to compress the carotid arteries.

The ezekiel is known for being available from positions where other chokes might be unavailable, particularly from inside closed guard where lapel grips might not be accessible.

## Mechanics

The ezekiel choke operates by:

**Sleeve Control:** The attacker controls the opponent's sleeve, typically near the wrist or forearm.

**Pressure Application:** The attacker uses the controlled sleeve as a choking element, pressing it against the opponent's neck.

**Hand Positioning:** Usually one hand controls the sleeve while the other applies direct pressure, or both hands work in coordination.

**Carotid Compression:** The sleeve compresses against the carotid arteries, restricting blood flow to the brain.

## Entries

The ezekiel choke can be entered from:

- Closed guard (from inside the guard, using mount position)
- Mount position (very dominant position for the choke)
- Side control (in certain configurations)
- Various gi-specific positions

## Mount Position Application

From mount, the ezekiel is particularly powerful:

- The top player has gravity and weight advantage
- The mounted player's arms are restricted
- The sleeves are within easy reach
- The choke is difficult to defend once established

## Gi Dependence

The ezekiel choke requires a gi to apply effectively. The sleeve fabric is essential to creating the choking pressure. In no-gi grappling, the technique is not available.

## Defense

Defending against the ezekiel requires:

- **Hand Position:** Preventing the attacker from controlling the sleeve
- **Head Positioning:** Rotating the head to prevent clean carotid compression
- **Escape:** Moving out of mount or guard before the choke is fully locked
- **Grip Breaking:** Breaking the attacker's grip on the sleeve

## Comparison to Other Gi Chokes

The ezekiel differs from other gi chokes:

- Uses the sleeve rather than lapels
- Often available when lapel chokes are not
- Technically simpler than complex collar chokes
- Works well from inside guard positions

## Teaching Progression

The ezekiel is typically taught as an alternative gi choke alongside the cross collar choke. It's valued for its:

- Simplicity
- Multiple entry points
- Effectiveness from guard (where many chokes are difficult)
- Quick application potential

## Gi Rules and Legality

The ezekiel is legal at all belt levels in IBJJF and most other rulesets. It is considered a fundamental gi submission.
"""
    },

    "bow-and-arrow-choke": {
        "title": "Bow and Arrow Choke",
        "category_slug": "submission",
        "summary": "A gi choke applied from back control using the collar and belt grips in a bow-and-arrow configuration.",
        "content": """## Overview

The bow and arrow choke is a gi-specific blood choke applied from back control. The attacker uses the opponent's own lapel/collar as the primary choking element (the bow) and the opponent's belt or pant leg (the arrow) for additional leverage. The configuration resembles the mechanics of drawing a bow and arrow.

The bow and arrow is known for being a devastating finishing technique from back control when the standard rear naked choke is being defended.

## Mechanics

The bow and arrow works by:

**Collar Control:** The attacker grips the opponent's collar with one hand, pulling it across the neck.

**Belt/Lapel Grip:** The attacker's other hand grips the opponent's belt or pants, creating a leverage point.

**Arching Pressure:** The attacker arches their back, pulling the collar tight while pushing with the belt grip.

**Choke Application:** This combination compresses both carotid arteries, creating blood flow restriction.

## Setup from Back Control

The bow and arrow is typically set up when:

- The opponent defends the chin against the rear naked choke
- The attacker already has back control with hooks
- The gi provides collar grips for the choke
- The opponent is attempting to defend conventional back control submissions

## Gi Requirement

Like all collar chokes, the bow and arrow requires a gi to execute. The lapel/collar must be substantial enough to grip and control.

## Variations

**High Bow and Arrow:** Using high collar grips for different pressure angles.

**Low Bow and Arrow:** Using lower collar grips, closer to the chest.

**Double Sleeve Grip:** Some variations use sleeve grips instead of collar.

## Defense

Defending against the bow and arrow includes:

- **Collar Defense:** Keeping the collar tight against the neck to prevent pulling
- **Hip Movement:** Rotating the hips to reduce choke pressure
- **Hand Control:** Using hands to prevent the belt grip
- **Escape:** Moving out of back control position

## Comparison to Rear Naked Choke

While both are back control submissions:

- The bow and arrow uses the gi, the RNC does not
- The bow and arrow attacks from a different angle
- The bow and arrow is often available when RNC defense is strong
- Both are finishing submissions from the same position

## Strategic Value

The bow and arrow serves as an excellent finishing option when:

- The opponent is defending the chin well
- The collar grip is strong
- The gi allows for sleeve/collar control
- Direct RNC attempts are being countered

## Teaching Progression

The bow and arrow is typically taught as an advanced back control submission, usually after the rear naked choke is well-established.
"""
    },

    "cross-collar-choke": {
        "title": "Cross Collar Choke",
        "category_slug": "submission",
        "summary": "A fundamental gi choke using both collar lapels from guard, mount, or top positions.",
        "content": """## Overview

The cross collar choke (also called the cross choke, x-choke, or collar choke) is one of the most fundamental gi-specific blood chokes in Brazilian Jiu-Jitsu. The attacker uses both of the opponent's collar lapels to compress the neck and carotid arteries, with one hand controlling each lapel in a crossed pattern.

The cross collar choke is accessible from numerous positions and is one of the first submissions taught to beginners in gi training.

## Mechanics

The cross collar choke operates by:

**Grip Setup:** The attacker gets grips on both sides of the opponent's collar.

**Crossed Configuration:** One hand's lapel control crosses over the other for optimal pressure.

**Neck Compression:** Both hands pull the lapels tight against the neck, compressing both carotid arteries.

**Pressure Application:** Squeezing the hands together increases pressure, forcing submission.

## Entry Positions

The cross collar choke can be entered from:

- Closed guard (very common entry)
- Mount position
- Open guard variations
- Side control (in certain configurations)
- Some standing positions

## Guard Entry

From closed guard, the cross collar is particularly effective:

- The guard player breaks the opponent's posture
- Collar grips are easily established
- The mount position often follows the posture break
- Multiple entry angles are available

## Mount Variation

From mount, the cross collar is devastating:

- Weight distribution favors the top player
- The mounted player cannot easily defend grips
- Multiple submission combinations flow from mount
- The choke often ends the match when achieved cleanly

## Defense

Defending against the cross collar requires:

- **Grip Defense:** Preventing the attacker from establishing strong collar grips
- **Neck Position:** Keeping the chin tight and head positioned to minimize choke pressure
- **Posture:** Maintaining upright posture in guard to prevent the choke from being locked
- **Escape:** Moving to different positions or breaking the attacker's guard

## Gi Dependence

The cross collar choke requires a gi to execute effectively. The collar lapels must be substantial and grippable. In no-gi competition, this submission is not available.

## Teaching Progression

The cross collar choke is typically taught very early in gi training because:

- Simple mechanics
- Multiple accessible entries
- High percentage at all skill levels
- Foundation for understanding collar chokes

## Competition Statistics

The cross collar choke remains one of the most successful gi submissions at all belt levels and competition organizations.
"""
    },

    "loop-choke": {
        "title": "Loop Choke",
        "category_slug": "submission",
        "summary": "A gi choke using a loop or collar grip from top positions, often set up with snap-down techniques.",
        "content": """## Overview

The loop choke is a gi-specific blood choke that uses a collar grip (typically from the opponent's own lapel wrapped in a loop configuration) to compress the neck. The attacker controls the collar in a particular way that creates a choking loop around the opponent's neck.

The loop choke is valued for appearing from snap-down setups and front headlock positions, making it a common finishing submission in standing and ground transitions.

## Mechanics

The loop choke works by:

**Collar Control:** The attacker establishes a grip on the opponent's collar, typically the same-side collar.

**Loop Configuration:** The attacker manipulates the lapel to create a loop or tight band around the neck.

**Compression:** The attacker pulls and compresses the collar against the neck, restricting carotid flow.

**Hand Positioning:** Both hands work in coordination to maintain and tighten the loop.

## Setup from Snap Down

The loop choke commonly flows from:

- Snap-down techniques that establish front headlock
- Collar grip acquisition from the standing position
- Transitions into the loop choke finish
- Often paired with guillotine choke defenses

## Front Headlock Entry

When the opponent defends a guillotine choke:

- The attacker switches to loop choke positioning
- The collar grip is already established
- The position transitions smoothly
- The loop choke becomes the follow-up submission

## Variations

**Same-Side Loop Choke:** Using the same-side collar (right collar from right side).

**Cross Loop Choke:** Using the opposite-side collar for a different pressure angle.

**Double Sleeve Loop:** Some variations use sleeve grips instead of collar.

## Defense

Defending against the loop choke includes:

- **Head Positioning:** Keeping the chin tight and neck protected
- **Collar Control:** Preventing tight collar grips from being established
- **Escape:** Moving out of front headlock or snap-down positions
- **Grip Breaking:** Breaking the attacker's collar grip

## Relationship to Other Front Headlock Submissions

The loop choke is part of the front headlock submission family:

- Similar to guillotine but different mechanics
- Often transitions from guillotine defense
- Uses collar rather than arm elements
- Available from comparable positions

## Teaching Progression

The loop choke is typically taught as an intermediate gi submission, often alongside guillotine choke and its variations.

## Gi Requirement

Like other collar chokes, the loop choke requires a gi with collar grips to execute.
"""
    },

    "arm-triangle": {
        "title": "Arm Triangle",
        "category_slug": "submission",
        "summary": "A choke combining the opponent's arm with the attacker's chest, compressing the neck without using arms.",
        "content": """## Overview

The arm triangle (also called the head and arm choke or Asphyxiating Choke) is a blood choke that uses the opponent's own arm as one side of a triangle around their neck, combined with the attacker's chest and arm for compression. Unlike a traditional triangle choke, which uses the legs, the arm triangle uses upper body positioning.

The arm triangle is particularly valuable from top positions like side control and mount, where the attacker has weight and gravity advantage.

## Mechanics

The arm triangle operates by:

**Arm Positioning:** One of the opponent's arms is pulled across their own neck (the arm trapped becomes part of the choking mechanism).

**Chest Pressure:** The attacker's chest and torso create pressure against the opponent's neck.

**Squeeze:** The attacker squeezes their own arms together, adding compression to the choke.

**Carotid Compression:** The combination compresses the carotid arteries, restricting blood flow.

## Setup from Side Control

From side control, the arm triangle is set up by:

- Controlling the opponent's far arm
- Creating an underhook position
- Positioning the trapped arm across the opponent's neck
- Tightening the chest pressure
- Applying additional hand pressure for finish

## Mount Application

From mount, the arm triangle is devastating:

- The mounted player is trapped beneath the mounted player
- The arm is easily controlled and pulled across
- Weight distribution applies constant pressure
- The choke finishes quickly when properly locked

## Back Control Variation

The arm triangle can also be applied from back control when:

- The opponent moves to escape back control
- One arm can be isolated and controlled
- The attacker can apply chest pressure
- The transition often surprises the defending grappler

## Defense

Defending against the arm triangle requires:

- **Arm Positioning:** Preventing the arm from being pulled across the neck
- **Space Creation:** Creating distance to reduce chest pressure
- **Escape:** Rolling or moving to prevent the lock
- **Grip Breaking:** Breaking the attacker's hand control

## Comparison to Traditional Triangle Choke

Both are high-percentage submissions, but:

- Arm triangle uses the arm, not the legs
- Available from different positions (top vs. guard)
- Arm triangle benefits from top pressure
- Triangle choke requires leg positioning

## Strategic Value

The arm triangle is valuable because:

- It surprises opponents expecting submissions from arms
- It flows naturally from side control and mount
- It uses the opponent's own arm against them
- It's difficult to defend once fully locked

## Teaching Progression

The arm triangle is typically taught as an intermediate submission, after basic chokes are learned.
"""
    },

    "north-south-choke": {
        "title": "North-South Choke",
        "category_slug": "submission",
        "summary": "A choke applied from north-south position using collar control and body pressure.",
        "content": """## Overview

The north-south choke is a gi-specific blood choke applied from the north-south position. The attacker is positioned perpendicular to the opponent's body (facing one direction while the opponent faces the opposite direction), and uses collar grips to compress the neck.

The north-south position itself is already dominant, and when the attacker secures a collar grip, submission becomes a logical conclusion.

## Mechanics

The north-south choke operates by:

**Position Establishment:** The attacker achieves north-south position (perpendicular body alignment).

**Collar Control:** Both collar lapels are gripped with one or both hands.

**Pressure Application:** The attacker uses body weight and hand pressure to compress the collar against the neck.

**Choke Finish:** Continued pressure forces submission or unconsciousness.

## North-South Position

The north-south position itself provides:

- Strong positional control
- Multiple submission options (chokes, armbars)
- Difficulty for the bottom player to escape
- Good transition point to other dominant positions

## Grip Variations

**Double Collar Grip:** Both hands grip the collar for maximum pressure.

**Collar and Sleeve:** One hand grips collar, one controls sleeve for additional control.

**Loop Configuration:** The lapel is controlled in a loop for different pressure angles.

## Defense

Defending against the north-south choke includes:

- **Escape from Position:** Moving out of north-south entirely
- **Collar Defense:** Preventing clear collar grips
- **Head Position:** Keeping the neck protected and chin tight
- **Hip Escape:** Creating space and movement to reduce pressure

## Relationship to Other Positional Chokes

The north-south choke is one of several position-specific submissions:

- Similar strategic value to side control submissions
- Part of the pressing/dominant position submission family
- Often chains into other submissions
- Particularly effective when opponent is flattened

## Teaching Progression

The north-south choke is typically taught as an intermediate gi submission, alongside other positional chokes like side control submissions.

## Gi Requirement

The north-south choke requires a gi for collar grips.
"""
    },

    "anaconda-choke": {
        "title": "Anaconda Choke",
        "category_slug": "submission",
        "summary": "An arm-in head and arm choke applied from front headlock positions, part of the guillotine family.",
        "content": """## Overview

The anaconda choke is an arm-in head and arm choke applied from front headlock or snap-down positions. The attacker wraps one arm around the opponent's neck with their arm trapped inside (similar to a guillotine but with the arm wrapped around rather than across).

The anaconda is known for being a powerful follow-up or alternative to the guillotine choke when the opponent defends the standard guillotine grip.

## Mechanics

The anaconda choke operates by:

**Arm Wrapping:** One of the attacker's arms wraps around the opponent's neck.

**Arm Positioning:** The attacker's own arm is positioned inside the wrap (unlike guillotine where the forearm crosses).

**Lock Completion:** The free hand clasps or controls the wrapping arm to complete the choke.

**Pressure Application:** The attacker applies pressure by tightening the arm wrap and applying body weight.

**Carotid Compression:** The arm compresses both carotid arteries, restricting blood flow.

## Setup from Front Headlock

The anaconda is commonly set up when:

- The opponent defends a guillotine choke attempt
- The attacker transitions from guillotine grip
- A snap-down has been established
- The opponent attempts to escape the front headlock

## Arm Position Distinction

Unlike the guillotine:

- The arm wraps around the neck rather than crossing
- The arm is inside the choke rather than outside
- The mechanics create different pressure angles
- The anaconda is often available when guillotine is not

## Grip Variations

**High Grip:** Gripping higher on the arm for increased control.

**Low Grip:** Gripping lower for different pressure angles.

**Leg Assistance:** Sometimes the attacker uses leg positioning to enhance the choke.

## Defense

Defending against the anaconda includes:

- **Arm Control:** Preventing the arm from wrapping fully
- **Escape:** Moving out of front headlock before the choke locks
- **Head Position:** Protecting the neck and creating space
- **Grip Breaking:** Breaking the attacker's grip

## Teaching Progression

The anaconda is typically taught as an intermediate to advanced submission, usually after guillotine is well-established.

## Success in Competition

The anaconda is highly effective in:

- No-gi competition (where it's identical to gi versions)
- Transitional exchanges from guillotine defense
- Scramble situations
- Standing-to-ground transitions
"""
    },

    "calf-slicer": {
        "title": "Calf Slicer",
        "category_slug": "submission",
        "summary": "A compression lock that crushes the calf muscle against the shin bone, causing severe pain.",
        "content": """## Overview

The calf slicer is a compression lock submission that targets the calf muscle. The attacker positions their shin or forearm against the opponent's calf muscle and applies compression, effectively crushing the muscle against the bone. The resulting pain and tissue damage force submission.

The calf slicer is known for being a brutal but less common submission that flows from leg entanglement positions.

## Mechanics

The calf slicer operates by:

**Calf Positioning:** The attacker positions their shin or forearm against the opponent's calf muscle.

**Bone Bracing:** The opponent's shin or bone forms the bracing point against which the calf is compressed.

**Compression Force:** The attacker applies direct compression perpendicular to the muscle fibers.

**Pain Response:** The tissue damage and muscle crushing force submission.

**Target:** The calf muscle (gastrocnemius and soleus muscles) is the primary target.

## Positions for Calf Slicers

Calf slicers are typically applied from:

- Leg entanglement positions
- Bottom leg lock positions
- Scrambles with leg control
- Specific leg lock systems where footlocks aren't available

## Setup Mechanics

A calf slicer is typically set up by:

- Establishing leg control and entanglement
- Positioning the shin or forearm against the calf
- Creating the compression angle
- Applying steadily increasing pressure

## Defense

Defending against the calf slicer includes:

- **Leg Positioning:** Preventing the shin from being placed against the calf
- **Mobility:** Rotating or repositioning the leg to relieve pressure
- **Escape:** Moving out of leg lock position
- **Counterattack:** Using arm control to attack while defending

## Calf Slicer vs. Other Leg Locks

Unlike footlock submissions:

- Attacks muscle tissue rather than joints
- Relies on compression rather than joint mechanics
- Causes different type of pain response
- Available from different positional setups

## Rulesets and Legality

In most rulesets permitting leg locks, calf slicers are legal. However:

- Some organizations specifically restrict compression locks on the calf
- Legality varies by belt level and organization
- Modern rulesets increasingly permit all leg lock submissions

## Teaching Progression

Calf slicers are typically taught as advanced leg lock submissions, after fundamental joint locks are mastered.

## Submission Characteristics

The calf slicer is known for:

- Quick submission times when properly applied
- Clear pain feedback to the defending grappler
- Less common than heel hooks or ankle locks
- Brutal effectiveness when used
"""
    },

    "wrist-lock": {
        "title": "Wrist Lock",
        "category_slug": "submission",
        "summary": "A joint lock submission that hyperextends or rotates the wrist joint, causing pain and potential injury.",
        "content": """## Overview

The wrist lock is a joint lock submission that applies hyperextension or rotational pressure to the wrist joint. The attacker isolates the opponent's wrist and applies controlled force to the wrist joint itself, causing pain and forcing submission to avoid injury.

Wrist locks are particularly common in smaller-weight competitors and gi competition, where they provide high-percentage submissions from various positions.

## Mechanics

The wrist lock operates by:

**Wrist Isolation:** The attacker controls and isolates one wrist.

**Grip Control:** Both of the attacker's hands (or sometimes involving legs) control the wrist.

**Hyperextension:** The attacker applies backward bending force on the wrist, hyperextending the joint.

**Rotational Force:** Sometimes combined with rotational pressure for enhanced effect.

**Joint Stress:** The pressure causes pain and risks ligament damage.

## Entry Positions

Wrist locks can be entered from:

- Mount position
- Guard position (particularly with one-handed grip situations)
- Side control
- Various transitional positions
- Gi-specific grip situations

## Grip Fighting Context

Wrist locks are particularly valuable in:

- Collar and sleeve grip fighting
- Guard retention situations
- Pin defense scenarios
- Preventing specific attacking grips

## Variations

**Simple Hyperextension Wrist Lock:** Direct backward bending.

**Rotational Wrist Lock:** Combining hyperextension with rotation.

**Two-on-One Wrist Lock:** Both hands control the opponent's single wrist.

**Leg-Assisted Wrist Lock:** Using the legs to enhance pressure or control.

## Defense

Defending against a wrist lock requires:

- **Hand Position:** Preventing full wrist isolation
- **Flexibility:** Having mobile wrists to accommodate pressure
- **Escape:** Moving out of position before the lock is fully applied
- **Counterattack:** Using free limbs to attack while defending

## Gi vs. No-Gi Differences

In the gi, wrist locks are:

- More accessible due to grip-fighting opportunities
- More common as submissions
- Often part of gi-specific curricula

In no-gi, wrist locks are:

- Less common due to different grip dynamics
- Still available from certain positions
- Often considered less reliable

## Teaching Progression

Wrist locks are typically taught as intermediate submissions, particularly in gi training programs.

## Safety Considerations

Wrist locks require:

- Careful application to avoid injuries in training
- Clear communication between training partners
- Proper tap recognition and respect for submissions
- Conservative pressure application
"""
    },
}

SWEEPS_AND_PASSES = {
    "scissor-sweep": {
        "title": "Scissor Sweep",
        "category_slug": "sweep",
        "summary": "A fundamental closed guard sweep using a scissor motion with the legs to flip the opponent.",
        "content": """## Overview

The scissor sweep is one of the most fundamental and high-percentage sweeps in Brazilian Jiu-Jitsu, available from closed guard. The guard player uses a scissor motion with their legs to flip the opponent over, typically landing in mount or side control position.

The scissor sweep is often the first sweep taught to beginners because of its mechanical simplicity, high success rate, and immediate effectiveness.

## Mechanics

**Setup:** The guard player breaks the opponent's posture and controls grips (typically collar and sleeve or underbody control).

**Leg Position:** One leg places the heel on the opponent's hip while the other places the sole of the foot on the opponent's hip or thigh on the same side.

**Scissor Motion:** The legs execute a scissors motion — the bottom leg pulls toward the body while the top leg extends, creating rotational force.

**Hand Contribution:** The hands pull the opponent to amplify the sweeping force.

**Direction:** The opponent typically lands in side control or mount.

## Entry Requirements

For an effective scissor sweep:

1. Guard player must control the opponent's posture (they must be broken down)
2. Grip control is necessary to prevent the opponent from posting
3. Proper leg positioning on one side of the opponent's body
4. Hip timing to maximize sweeping power

## Variations

**Standard Scissor Sweep:** The fundamental form with heel and foot placement.

**High Scissor:** The heel is placed higher on the opponent's torso.

**Low Scissor:** The heel is placed lower on the hip or thigh.

**Double Control Scissor:** Using additional hand control for more power.

## Defense

Scissor sweep defenses include:

**Posture Maintenance:** Remaining upright to prevent the sweep.

**Hand Post:** Posting a hand outside the scissor to prevent rotation.

**Leg Escape:** Removing the legs from the scissor motion.

**Weight Shift:** Moving weight away from the sweep direction.

## Counters

An opponent defending the scissor sweep can sometimes:

- Reverse into the guard player
- Counter with an armbar
- Establish a better guard-passing position
- Create space to escape

## Teaching Progression

Scissor sweep is typically taught in the fundamental BJJ curriculum because:

- Simple mechanical structure
- High-percentage success
- Teaches sweeping principles
- Sets foundation for other sweeps

## Sweep Timing

The scissor sweep is heavily timing-dependent. The ideal moment is when the opponent is committing their weight forward or attempting to pass. Timing the sweep with the opponent's movement greatly increases success rate.

"""
    },

    "toreando-pass": {
        "title": "Toreando Pass (Bullfighter Pass)",
        "category_slug": "pass",
        "summary": "A speed-based guard pass using lateral movement and grip control to bypass the legs.",
        "content": """## Overview

The toreando pass (also called the bullfighter pass) is a guard-passing technique where the top player uses quick lateral movement and hand control to bypass the opponent's guard legs without heavy pressure. The pass is named for the footwork similarity to a bullfighter evading a charging bull.

The toreando is one of the highest-percentage guard passes in no-gi grappling and is increasingly used in gi competition due to its effectiveness and speed.

## Basic Mechanics

**Starting Position:** The top player stands or is in a tall posture with the guard player's legs in view.

**Hand Control:** Grab or control both of the guard player's legs/knees from the outside.

**Lateral Step:** Step quickly to the side (usually the direction of the pass).

**Guard Bypass:** As the top player moves laterally, the guard player's legs move with the hands but cannot prevent the top player from advancing.

**Position Achievement:** The top player establishes side control or mount on the opposite side.

## Variations

**High Toreando:** The hands control the knees/thighs higher up.

**Low Toreando:** The hands control the legs lower, closer to the feet.

**Toreando with Underhook:** Adding an underhook during or after the pass.

**Double-Collar Toreando:** Using collar grips as the hand control.

**Pendulum Toreando:** Using a rocking motion instead of pure lateral movement.

## Speed vs. Pressure

The toreando emphasizes speed over pressure. The goal is to move laterally faster than the guard player can adjust, not to flatten them and pressure-pass them. This difference makes the toreando effective against open guard positions.

## Against Open Guard

The toreando is particularly effective against:

- De La Riva Guard
- Spider Guard
- Butterfly Guard
- Other open guards without closed leg lock

## Against Closed Guard

Against closed guard, the toreando works by:

1. Widening stance to create distance
2. Breaking posture and passing with speed
3. Using hand control to manage the legs
4. Sometimes the guard opens as the top player passes

## Defense

Toreando defenses include:

**Leg Control:** Maintaining grip control or reconnecting legs.

**Turning:** Turning to follow the pass direction.

**Underhook:** Creating an underhook to slow the pass.

**Grip Fighting:** Controlling the passer's grips.

**Footlock:** Attacking the passer's leg during the pass.

## Timing and Pressure

The toreando works when:

- The guard player is distracted or setting up their own attacks
- The top player has superior footwork
- The guard player doesn't have effective leg lock threats
- The position allows for explosive movement

## Lead-Pass Timing

The toreando is particularly effective as a lead pass where the top player acts before the guard player fully establishes their position.

## Modern Application

In contemporary jiu-jitsu, particularly at higher levels, the toreando has become a primary passing option due to its consistency and the ability to avoid dangerous leg lock positions.

"""
    },

    "double-leg-takedown": {
        "title": "Double Leg Takedown",
        "category_slug": "takedown",
        "summary": "A fundamental wrestling takedown attacking both legs simultaneously to take the opponent to the ground.",
        "content": """## Overview

The double leg takedown is one of the most fundamental and effective takedowns across wrestling, judo, and grappling. The attacker shoots forward, grabs both of the opponent's legs, and drives forward and downward to take them to the ground.

The double leg is characterized by its high success rate, explosive nature, and application across all skill levels from beginners to elite athletes.

## Basic Mechanics

**Setup:** The attacker measures distance and creates an opportunity to shoot.

**Shooting:** The attacker explosively shoots forward with bent legs, moving the head forward and to the side.

**Leg Grab:** Both legs are grabbed simultaneously — typically around the knees or thighs depending on distance and positioning.

**Drive:** The attacker drives forward and down, using their legs to generate power, driving the opponent backward and to the ground.

**Finishing:** Once the opponent is down, the attacker establishes a dominant position (typically side control or mount).

## Distance Management

The double leg is most effective at intermediate distance — far enough to shoot without the opponent seeing it coming, but close enough to execute the takedown. Footwork and positioning create these opportunities.

## Head Position

Head position is critical for successful double leg execution:

- **Head on the side:** Protecting the head by placing it to the side rather than center of the chest
- **Head past the body:** Following through past the opponent's body to maintain forward momentum

## Variations

**High Double Leg:** The grab is on the thighs, more suitable for shooting from distance.

**Low Double Leg:** The grab is below the knees, better when closer to the opponent.

**Ankle Pick Double:** Similar mechanics but grabbing the ankles rather than higher up.

**Arm Drag to Double:** Setting up the double leg with an arm drag to trap an arm.

## Defense

Double leg defenses include:

**Sprawl:** Pushing the hips back and extending the legs to prevent the takedown.

**Over-Underhook:** Creating arm control to prevent leg access.

**Snap Down:** Controlling the head to prevent the shoot.

**Lateral Movement:** Moving to the side to avoid the direct shooting line.

## Counters

An opponent defending the double leg can:

- Take a dominant position (back control) if the attacker isn't careful
- Knee the sprawled attacker (depending on rules)
- Transition to a countertake

## When to Shoot

Double legs are most effective when:

- The opponent is distracted or setting up their own attack
- The distance is optimal
- The attacker has setup movements creating the opportunity
- The opponent's weight is forward

## Wrestling vs. Jiu-Jitsu Context

In wrestling, the double leg ends with a pin. In BJJ and submission grappling, the double leg transitions to positional dominance that allows for submissions.

## Teaching and Development

The double leg is typically taught early in wrestling curricula due to its fundamental importance and transferability to other takedowns and techniques.

"""
    },

    "hip-bump-sweep": {
        "title": "Hip Bump Sweep",
        "category_slug": "sweep",
        "summary": "A fundamental closed guard sweep using hip bump momentum to flip the opponent.",
        "content": """## Overview

The hip bump sweep (also called the bump sweep) is a closed guard sweep that uses a sudden hip thrust forward combined with grip control to flip the opponent over the guard player's body. It is one of the most accessible and fundamental sweeps taught in BJJ, requiring good timing and hip mobility rather than pure strength.

The hip bump is often taught alongside the scissor sweep as the foundational closed guard sweep for beginners.

## Mechanics

The hip bump sweep operates by:

**Setup:** The guard player breaks the opponent's posture and establishes good grips (typically collar and sleeve).

**Hip Bridge:** The guard player drives their hips forward explosively, creating momentum.

**Combined Pull:** The hands pull the opponent forward while the hips thrust up, creating rotational force.

**Timing:** The sweep's success depends entirely on timing — the hip drive and hand pull must occur simultaneously.

**Finish:** The opponent rotates over the guard player, landing in the sweep direction.

## Key Differences from Scissor Sweep

While both are closed guard sweeps:

- Hip bump uses hip momentum rather than leg scissors
- Hip bump works better when the opponent is heavy
- Scissor sweep creates more mechanical leverage
- Hip bump requires better timing and coordination

## Timing Fundamentals

The hip bump is largely a timing game:

- Must catch the opponent when they're committed
- Works best when the opponent is trying to posture
- Works best when the opponent leans forward
- Poor timing results in failed sweeps

## Variations

**Standard Hip Bump:** Straight forward momentum.

**Hip Bump with Overhook:** Using overhook control for different angles.

**Hip Bump to Side:** Angling the sweep to a specific side for better position.

## Defense

Defending against the hip bump includes:

- **Weight Distribution:** Keeping weight centered and mobile
- **Grip Control:** Preventing strong collar and sleeve grips
- **Timing:** Not falling for timing attempts
- **Hip Escape:** Creating space to escape the sweep

## Teaching Progression

The hip bump is typically taught very early in BJJ curricula because:

- Simple mechanics (just hip thrust)
- Teaches fundamental timing concepts
- Accessible from closed guard
- Builds foundation for more complex sweeps

## Common Mistakes

New students often:

- Use only arms instead of using the hips
- Attempt the sweep from bad positions
- Lack timing and patience
- Try to muscle through instead of using timing
"""
    },

    "butterfly-sweep": {
        "title": "Butterfly Sweep",
        "category_slug": "sweep",
        "summary": "A butterfly guard sweep using the butterfly hooks and upper body control.",
        "content": """## Overview

The butterfly sweep is a fundamental open guard sweep where the guard player uses butterfly hooks (hooks on the inside of the opponent's thighs with the feet) combined with hand control to sweep the opponent. It is one of the highest-percentage sweeps available from butterfly guard.

The butterfly sweep is a staple in most BJJ curricula and is available to even small practitioners against much larger opponents.

## Mechanics

The butterfly sweep operates by:

**Setup:** The guard player establishes butterfly guard with both feet hooked inside the opponent's thighs.

**Hand Control:** The guard player gets collar and sleeve grips or underbody control.

**Elevation:** The feet actively lift the opponent's hips upward using the butterfly hooks.

**Hand Contribution:** The hands pull and contribute to the rotational force.

**Sweep Execution:** The combination of foot elevation and hand pull rotates the opponent over.

## Butterfly Guard Positioning

Butterfly guard itself provides:

- Good hip control
- Natural sweeping opportunities
- Transitional flexibility
- Multiple attacking angles

## Variations

**High Butterfly:** The hooks are placed higher on the thighs.

**Low Butterfly:** The hooks are placed lower, closer to the knees.

**Underhook Butterfly:** Using underhook control instead of collar and sleeve.

**Butterfly to Back Take:** Transitioning to back control instead of landing in mount or side control.

## Defense

Defending against the butterfly sweep requires:

- **Hook Removal:** Escaping or dislodging the butterfly hooks
- **Weight Management:** Keeping weight distributed and mobile
- **Grip Control:** Preventing tight hand grips
- **Posture:** Maintaining upright posture to prevent the sweep

## Teaching Progression

The butterfly sweep is typically taught as an intermediate sweep, after scissor and hip bump sweeps are established.

## Combination Value

The butterfly sweep chains well with:

- Butterfly guard passes
- Back take attempts
- Other open guard sweeps
- Guard transitions

## Effectiveness Factors

Butterfly sweeps are most effective when:

- The opponent is in butterfly guard range
- The guard player has good hip mobility
- Timing is sharp
- Hand grips are strong
"""
    },

    "pendulum-sweep": {
        "title": "Pendulum Sweep",
        "category_slug": "sweep",
        "summary": "A closed guard sweep using a leg pendulum motion to create rotational momentum.",
        "content": """## Overview

The pendulum sweep is a closed guard sweep that uses a pendulum-like leg motion to create rotational force and flip the opponent. One leg swings outward like a pendulum while the other remains anchored, creating a powerful sweeping motion that catches the opponent's weight at the right moment.

The pendulum sweep is known for being particularly effective when the opponent is heavy or trying to maintain base.

## Mechanics

The pendulum sweep operates by:

**Setup:** The guard player establishes closed guard with good posture breaks.

**Pendulum Motion:** One leg swings outward in a pendulum arc while the other provides stability.

**Timing:** The guard player catches the opponent's weight at the apex of the swing.

**Hand Control:** The hands contribute to the sweep, pulling the opponent in the desired direction.

**Rotation:** The combined forces rotate the opponent over the guard player.

## Leg Selection

The pendulum motion typically involves:

- One leg creating the main sweeping force (the pendulum)
- One leg providing base and stability
- Alternating which leg is the active pendulum

## Timing Mechanics

The pendulum sweep requires precise timing:

- Must catch the opponent committed
- Works best when opponent leans
- Depends on rhythm and cadence
- Rhythm creates predictability for better timing

## Variations

**Single Leg Pendulum:** Emphasizing one leg's pendulum motion.

**Double Leg Pendulum:** Both legs contribute to the pendulum motion.

**Pendulum to Different Position:** Directing the sweep to specific locations (side control vs. mount).

## Defense

Defending against the pendulum sweep includes:

- **Weight Management:** Maintaining a wide base
- **Grip Control:** Preventing collar and sleeve control
- **Leg Awareness:** Not allowing the pendulum motion to build
- **Hip Escape:** Creating space and movement

## Teaching Progression

The pendulum sweep is typically taught as an intermediate sweep, often alongside hip bump and scissor sweeps.

## Historical Context

The pendulum sweep is a classic BJJ technique that remains highly effective at all levels.
"""
    },

    "berimbolo": {
        "title": "Berimbolo",
        "category_slug": "sweep",
        "summary": "An inverted back take from De La Riva guard, passing over the shoulder while taking the back.",
        "content": """## Overview

The berimbolo is a dynamic De La Riva guard technique where the guard player inverts (goes upside down) and uses momentum to pass over the opponent's shoulder while simultaneously taking the back. The result is back control from a guard position, making it both a sweep and a positional transition.

The berimbolo is a relatively modern technique that requires significant hip flexibility and comfort with inversion. It became popular through the Mendes brothers' dominance in modern BJJ competition.

## Mechanics

The berimbolo operates by:

**Setup:** The guard player is in De La Riva guard (DLR) with a lasso hook and inside foot control.

**Inversion:** The guard player inverts (tips upside down) while maintaining the DLR control.

**Momentum:** Using the inversion's momentum and hip mobility, the guard player passes over the opponent's shoulder.

**Back Take:** As the guard player passes over, they simultaneously take the opponent's back.

**Finish:** The guard player ends up on top of the opponent's back, establishing hooks or control.

## De La Riva Requirements

The berimbolo requires:

- Established De La Riva guard position
- Good lasso hook control
- Inside leg hook
- Hip mobility and flexibility

## Inversion Mechanics

The inversion is the key element:

- Requires significant hip flexibility
- Creates momentum for the pass
- Allows the transition to back control
- Relies on body awareness and comfort with upside-down positions

## Variations

**Standard Berimbolo:** Basic inversion and back take.

**Berimbolo to Mount:** Adjusting the finish to land in mount instead of back control.

**Berimbolo Leg Lock:** Sometimes transitioning to leg lock attacks if back control isn't available.

## Defense

Defending against a berimbolo includes:

- **Base Maintenance:** Keeping weight distributed
- **Hook Escape:** Preventing the lasso and DLR hooks from being established
- **Movement:** Creating space and movement to prevent the inversion
- **Back Control Defense:** Defending once the back is taken

## Modern Acceptance

The berimbolo transitioned from a rarely-seen technique to a common staple of modern open guard systems, particularly at the professional level.

## Teaching Progression

The berimbolo is typically taught as an advanced open guard technique due to its complexity and flexibility requirements.

## Physical Requirements

The berimbolo requires:

- Hip flexibility
- Body awareness
- Comfort with inversion
- Strength and coordination
"""
    },

    "flower-sweep": {
        "title": "Flower Sweep",
        "category_slug": "sweep",
        "summary": "A closed guard sweep using an overhook and hip motion to flip the opponent.",
        "content": """## Overview

The flower sweep (also called the overhook sweep) is a closed guard sweep that uses an overhook on the opponent's arm combined with hip motion to flip the opponent over. The guard player secures an underhook or overhook position and uses this arm control combined with hip bridging to execute the sweep.

The flower sweep is a classical BJJ technique that is particularly effective when the opponent is controlling posture in a specific way.

## Mechanics

The flower sweep operates by:

**Setup:** The guard player establishes closed guard and breaks posture.

**Overhook Control:** The guard player gets an overhook on the opponent's arm.

**Hip Bridge:** Using the overhook, the guard player bridges explosively.

**Rotational Force:** The combination of overhook control and hip bridge creates the sweeping force.

**Finish:** The opponent rotates over the guard player's body.

## Arm Control Importance

The overhook is critical because:

- It traps the opponent's arm across their own body
- It prevents the opponent from posting to defend
- It creates rotational leverage
- It makes the sweep difficult to defend against

## Variations

**High Overhook:** Overhooking higher on the arm.

**Low Overhook:** Overhooking lower, closer to the wrist.

**Flower Sweep with Two Arms:** Using both arms to enhance control.

## Defense

Defending against the flower sweep includes:

- **Grip Fighting:** Preventing the overhook from being established
- **Posture:** Maintaining upright posture
- **Arm Positioning:** Keeping the arm in a position that prevents the sweep
- **Weight Distribution:** Maintaining a wide base

## Teaching Progression

The flower sweep is typically taught as an intermediate to advanced closed guard sweep.

## Combination Value

The flower sweep chains well with:

- Triangle choke setups
- Armbar transitions
- Other guard sweeps
- Transitions to more advanced positions

## Classical Technique

The flower sweep is considered a classical BJJ technique that has remained effective across decades of evolution.
"""
    },

    "tripod-sweep": {
        "title": "Tripod Sweep",
        "category_slug": "sweep",
        "summary": "An open guard foot sweep using three points of contact to flip the opponent.",
        "content": """## Overview

The tripod sweep is an open guard sweep that uses three points of contact (two hands and typically one foot) to control the opponent and execute a foot sweep. The guard player uses the tripod position to create base and leverage for the sweep.

The tripod sweep is a fundamental open guard technique that teaches good footwork and balance mechanics applicable to many other techniques.

## Mechanics

The tripod sweep operates by:

**Setup:** The guard player establishes open guard with good hand and foot positioning.

**Three Points:** Two hands on the opponent's body/limbs and typically one foot creating the sweeping point.

**Balance:** The three-point contact creates a stable base for the guard player.

**Foot Sweep:** The free foot hooks or sweeps the opponent's leg.

**Rotation:** The combination creates the sweeping force.

## Hand and Foot Positioning

The three points of contact are typically:

- Both hands controlling the opponent
- One foot positioned for the actual sweep
- Balance distributed across all three points

## Variations

**Tripod with Collar and Sleeve:** Using standard collar and sleeve control.

**Tripod with Underhook:** Using underhook control for different angles.

**Tripod to Different Positions:** Sweeping to specific positions based on angle.

## Defense

Defending against the tripod sweep includes:

- **Base Maintenance:** Keeping balance and preventing foot sweeps
- **Hand Control:** Breaking hand grips that create leverage
- **Footwork:** Maintaining foot positioning and awareness
- **Movement:** Creating space and movement to prevent the sweep

## Teaching Progression

The tripod sweep is typically taught as an intermediate open guard technique.

## Mechanical Principles

The tripod sweep teaches:

- Balance and weight distribution
- Multiple points of contact for control
- Footwork mechanics
- Sweep timing and execution
"""
    },

    "sickle-sweep": {
        "title": "Sickle Sweep",
        "category_slug": "sweep",
        "summary": "An open guard foot sweep using a sickle motion of the foot to hook the opponent's leg.",
        "content": """## Overview

The sickle sweep is an open guard sweep where the guard player uses a sickle-like motion with the foot to hook and sweep the opponent's leg. The guard player uses hand control and footwork to execute a sweeping motion that removes the opponent's base.

The sickle sweep is often paired with the tripod sweep as part of footwork-based open guard techniques.

## Mechanics

The sickle sweep operates by:

**Setup:** The guard player establishes open guard position.

**Hand Control:** Hands control the opponent for leverage and direction.

**Sickle Motion:** The guard player's foot makes a sickle-like sweeping motion.

**Hook:** The foot hooks or contacts the opponent's leg.

**Sweep Completion:** The foot motion combined with hand control flips the opponent.

## Foot Motion

The sickle sweep's distinctive feature is the foot motion:

- A curved, sickle-like path
- Creates sweeping force
- Hooks the opponent's leg or ankle
- Generates rotational momentum

## Variations

**Sickle to Inside:** Hooking on the inside of the leg.

**Sickle to Outside:** Hooking on the outside of the leg.

**Sickle with Different Hand Control:** Varying the hand grips.

## Defense

Defending against the sickle sweep includes:

- **Footwork:** Preventing the sickle hook from connecting
- **Base:** Maintaining a stable base and balance
- **Weight:** Managing weight to stay secure
- **Movement:** Creating space and movement

## Teaching Progression

The sickle sweep is typically taught alongside other footwork-based sweeps.

## Mechanical Learning

The sickle sweep teaches:

- Detailed footwork mechanics
- Curved motion and control
- Timing and rhythm
- Integration with hand control
"""
    },

    "knee-slice": {
        "title": "Knee Slice Pass",
        "category_slug": "pass",
        "summary": "A guard pass that slices through the guard with the knee and advances to side control.",
        "content": """## Overview

The knee slice pass (also called the knee cut pass) is a fundamental guard passing technique where the passer drives the knee through the guard player's legs and advances to side control or mount. It is one of the most common and highest-percentage guard passes used at all levels of competition.

The knee slice is particularly effective against open guard and butterfly guard positions.

## Mechanics

The knee slice pass operates by:

**Setup:** The passer establishes headquarters distance and proper base.

**Knee Drive:** The passer drives one knee through the guard player's legs.

**Hip Placement:** As the knee advances, the passer's hips come tight against the guard player.

**Guard Clearing:** The knee clears one leg out of the way while the passer's body pressure prevents re-engagement.

**Position Advance:** The passer finishes in side control or mount position.

## Variations

**Toreando Transition:** Converting a knee slice attempt into a toreando pass.

**Knee Slice to Mount:** Finishing in mount instead of side control.

**Knee Slice with Underhook:** Using underhook control for additional security.

## Timing

The knee slice pass requires:

- Good timing and coordination
- Proper distance management
- Solid base throughout
- Hip mobility and athletic ability

## Defense

Defending against the knee slice includes:

- **Hook Placement:** Using hooks or leg positioning to prevent the knee slice
- **Frame Escape:** Framing and creating space
- **Hip Escape:** Moving the hips away from the passer
- **Reversal:** Using momentum against the passer

## Teaching Progression

The knee slice is typically taught early in passing curricula due to its effectiveness and applicability.

## Why Knee Slice is Universal

The knee slice works well because:

- It attacks multiple guard positions
- It applies immediate pressure
- It's difficult for the guard to defend everything
- It leads naturally to submissions
"""
    },

    "leg-drag": {
        "title": "Leg Drag",
        "category_slug": "pass",
        "summary": "A guard pass that drags the opponent's leg to the side while advancing to dominant position.",
        "content": """## Overview

The leg drag (also called the leg drag pass) is a guard passing technique where the passer controls one of the guard player's legs, drags it to the side, and advances to side control or north-south position. It is a modern guard passing technique that is particularly effective against far guard positions like De La Riva and spider guard.

The leg drag has become increasingly popular at the highest levels of competition in recent years.

## Mechanics

The leg drag pass operates by:

**Leg Control:** The passer controls one of the guard player's legs (typically the one closest to their hip).

**Dragging Motion:** The passer drags the controlled leg toward their hip, removing it from defensive positioning.

**Hip Entry:** As the leg is dragged, the passer's hips advance into the space created.

**Pressure:** The passer applies body weight and pressure to advance to side control.

**Finish:** The passer achieves side control or north-south position.

## Guard Position Targets

The leg drag is particularly effective against:

- De La Riva guard
- Spider guard
- Open guard variations
- Far distance guards

## Hand Control

The passer typically:

- Controls the guard player's pants or belt on one leg
- Maintains grip throughout the pass
- Uses the other hand for body control or pressure
- Prevents the leg from coming back into defensive position

## Variations

**Leg Drag to Side Control:** Finishing in side control.

**Leg Drag to North-South:** Finishing in north-south position.

**Leg Drag with Underhook:** Using underhook control for additional security.

## Defense

Defending against the leg drag includes:

- **Grip Fighting:** Preventing the leg from being controlled
- **Hip Escape:** Moving away from the drag motion
- **Leg Repositioning:** Bringing the leg back into defensive position
- **Reversal:** Using momentum to reverse the pass

## Modern Adoption

The leg drag has become increasingly prominent in modern competition due to its effectiveness and the evolution of guard player defenses.

## Teaching Progression

The leg drag is typically taught as an intermediate to advanced guard pass.

## Effectiveness Factors

Leg drag passes are most effective when:

- The guard player is in far distance guard
- The passer has good hip positioning
- The control grip is secure
- Timing is sharp
"""
    },

    "over-under-pass": {
        "title": "Over-Under Pass",
        "category_slug": "pass",
        "summary": "A pressure passing technique using overhook and underhook control to advance.",
        "content": """## Overview

The over-under pass is a pressure-based guard passing technique where the passer uses overhook and underhook arm control to seal the guard player's hips and advance to dominant position. The passer's body weight applied through the arm connections creates tight, effective control.

The over-under pass is known for its simplicity and high-percentage nature, working particularly well at higher belt levels where grip fighting is emphasized.

## Mechanics

The over-under pass operates by:

**Arm Positioning:** The passer gets an overhook on one arm and an underhook on the opposite side.

**Hip Seal:** The passer seals their hips tight against the guard player's hips.

**Body Pressure:** The passer applies significant body weight through the arm connections.

**Advancement:** Using the tight control, the passer advances to side control.

**Pressure Dominance:** The passer maintains constant pressure throughout the pass.

## Arm Control Details

The overhook and underhook create:

- Lateral control preventing the guard player from rotating
- Strong connection between passer and guard player
- Difficulty for the guard player to establish grips
- Natural progression to side control

## Variations

**Over-Under to Mount:** Advancing to mount instead of side control.

**Over-Under with Leg Control:** Adding leg control for more security.

**Over-Under from Various Distances:** Adjusting for different guard positions.

## Defense

Defending against the over-under pass includes:

- **Arm Control:** Preventing the arm connections from being established
- **Hip Escape:** Creating space despite the tight control
- **Reversal:** Using the pressure against the passer
- **Grip Fighting:** Using grips to prevent the pass

## Teaching Progression

The over-under pass is typically taught as an intermediate passing technique, often alongside other pressure passing methods.

## Pressure Passing Principles

The over-under teaches:

- Importance of body weight distribution
- Arm control and positioning
- Pressure maintenance
- Positional advancement
"""
    },

    "stack-pass": {
        "title": "Stack Pass",
        "category_slug": "pass",
        "summary": "A guard pass that compresses the guard player's hips through stacking pressure.",
        "content": """## Overview

The stack pass is a guard passing technique where the passer uses compression and weight distribution to stack the guard player's hips and advance to dominant position. The passer uses body weight more than technique, applying heavy pressure to flatten and compress the guard player.

The stack pass is particularly effective against closed guard and deep guard positions where the guard player is trying to maintain posture.

## Mechanics

The stack pass operates by:

**Setup:** The passer establishes headquarters and grip control.

**Compression:** The passer drives their body forward, compressing the guard player's hips and torso.

**Stacking:** The guard player's hips are stacked toward their head, reducing their offensive capability.

**Hip Advancement:** As the guard player is compressed, the passer's hips advance.

**Finish:** The passer achieves side control or another dominant position.

## Weight Distribution

The stack pass relies heavily on:

- Body weight distribution
- Forward pressure
- Hip positioning
- Constant compression

## Variations

**Stack to Side Control:** Finishing in side control.

**Stack to Mount:** Finishing in mount position.

**Double Arm Stack:** Using both arms for additional compression.

## Defense

Defending against the stack pass includes:

- **Space Creation:** Creating any space to prevent stacking
- **Shrimping:** Moving the hips to escape the stack
- **Guard Retention:** Maintaining guard positioning despite pressure
- **Reversal:** Creating momentum to reverse the passer

## Teaching Progression

The stack pass is typically taught as a fundamental pressure passing technique.

## Weight vs. Technique

The stack pass emphasizes:

- Body weight usage
- Pressure application
- Positioning over technical complexity
- Fundamental principles
"""
    },

    "long-step-pass": {
        "title": "Long Step Pass",
        "category_slug": "pass",
        "summary": "A guard pass that uses a long stepping motion to bypass the guard and advance to side control.",
        "content": """## Overview

The long step pass is a guard passing technique where the passer takes a long step to the side and behind the guard player's legs, bypassing the guard and advancing to side control. It is a modern passing technique that works well against butterfly guard and open guard variations.

The long step pass is known for being athletic and effective when executed with proper timing and distance management.

## Mechanics

The long step pass operates by:

**Setup:** The passer establishes proper distance and hand control.

**Long Step:** The passer steps far to the side and backward, bypassing the guard.

**Hip Advancement:** The passer's hips advance into the space created by the step.

**Guard Clearing:** The guard player's legs are cleared out of the way.

**Position Advance:** The passer finishes in side control.

## Footwork

The long step pass relies on:

- Athletic stepping and movement
- Good distance management
- Proper weight distribution during the step
- Balance maintenance throughout

## Variations

**Long Step to Different Sides:** Passing to the left or right based on setup.

**Long Step with Underhook:** Using underhook control for additional security.

**Long Step to Mount:** Finishing in mount instead of side control.

## Defense

Defending against the long step pass includes:

- **Leg Hook:** Using hooks to prevent the step
- **Weight:** Maintaining weight distribution to stay grounded
- **Grip Control:** Controlling the passer's posture
- **Reversal:** Using the passer's momentum against them

## Teaching Progression

The long step pass is typically taught as an intermediate to advanced passing technique.

## Athletic Requirements

The long step pass requires:

- Good footwork and coordination
- Athletic ability and mobility
- Timing and distance awareness
- Balance and control
"""
    },

    "body-lock-pass": {
        "title": "Body Lock Pass",
        "category_slug": "pass",
        "summary": "A pressure passing technique using chest-to-chest contact and body lock control.",
        "content": """## Overview

The body lock pass is a pressure-based guard passing technique where the passer achieves chest-to-chest contact with the guard player and uses a body lock grip for control. The passer applies constant pressure and weight distribution to advance to side control or dominant position.

The body lock pass is known for being simple and effective, relying on pressure and positioning rather than complex footwork.

## Mechanics

The body lock pass operates by:

**Setup:** The passer achieves headquarters distance and broken posture.

**Body Lock:** The passer wraps both arms around the guard player's torso, creating a body lock.

**Chest Contact:** The passer maintains chest-to-chest contact throughout the pass.

**Weight Application:** The passer applies significant body weight through the lock.

**Hip Advancement:** The passer's hips advance to side control position.

**Pressure Dominance:** The passer maintains constant pressure.

## Body Lock Grip

The body lock provides:

- Total control of the opponent's torso
- Prevents arm attacks and submissions
- Creates lateral stability
- Allows for pressure application

## Variations

**High Body Lock:** Wrapping higher on the torso.

**Low Body Lock:** Wrapping lower on the hips.

**Body Lock to Mount:** Finishing in mount position.

## Defense

Defending against the body lock pass includes:

- **Arm Positioning:** Preventing the body lock from being established
- **Hip Escape:** Creating space despite the lock
- **Reversal:** Using the passer's pressure against them
- **Leg Control:** Using legs to prevent passage

## Teaching Progression

The body lock pass is typically taught as a fundamental pressure passing technique.

## Pressure Passing Foundation

The body lock pass teaches:

- Importance of chest-to-chest contact
- Body lock mechanics
- Weight distribution
- Constant pressure application
"""
    },

    "x-pass": {
        "title": "X-Pass",
        "category_slug": "pass",
        "summary": "A quick lateral guard pass using crossed leg positioning and hip movement.",
        "content": """## Overview

The x-pass (also called the X-guard pass) is a quick guard passing technique where the passer uses a specific leg crossing pattern and hip movement to rapidly advance to the side and pass the guard. It is known for being quick and effective when executed properly.

The X-pass works particularly well against open guard and butterfly guard positions where the guard player has extended legs.

## Mechanics

The x-pass operates by:

**Setup:** The passer establishes headquarters with good hand control.

**Leg Crossing:** The passer crosses their legs in an X pattern (one leg in front of the guard player's body, one behind).

**Hip Movement:** The passer uses the crossed leg positioning to shift hips laterally.

**Quick Advancement:** The passer rapidly advances to side control through the gap.

**Guard Clearing:** The guard is cleared out of the way in the process.

## Leg Positioning

The X-pattern is critical because:

- It creates a specific base for the pass
- It allows rapid lateral movement
- It clears the guard in the process
- It's difficult for the guard player to defend

## Variations

**X-Pass to Side Control:** The standard finish.

**X-Pass with Hand Control:** Using specific grip variations.

**X-Pass with Pressure:** Adding body weight and pressure.

## Defense

Defending against the x-pass includes:

- **Hook Prevention:** Using hooks to prevent the X-pattern
- **Hip Escape:** Creating movement to prevent passage
- **Grip Control:** Controlling the passer's grip
- **Leg Positioning:** Maintaining leg positioning

## Teaching Progression

The x-pass is typically taught as an intermediate passing technique.

## Speed Factor

The x-pass is valued for:

- Quick execution when proper timing is hit
- Effectiveness despite being well-known
- Applicability to multiple guard types
"""
    },

    "single-leg": {
        "title": "Single Leg Takedown",
        "category_slug": "takedown",
        "summary": "A fundamental takedown that attacks one leg, driving it backward or to the side.",
        "content": """## Overview

The single leg takedown is one of the most fundamental takedowns in grappling, used across wrestling, BJJ, judo, and MMA. The attacker targets one of the opponent's legs, typically either driving the leg backward or to the side, causing loss of balance and a takedown.

Single leg takedowns are taught early in most wrestling programs and remain high-percentage at all levels of competition.

## Mechanics

The single leg takedown operates by:

**Leg Targeting:** The attacker targets one of the opponent's legs.

**Grip Establishment:** The attacker wraps around the leg with both hands or one hand and the body.

**Driving:** The attacker drives forward (or to the side), pulling the leg out from under the opponent.

**Balance Loss:** The opponent loses balance and falls.

**Control:** The attacker establishes top position control.

## Variations

**High Single:** Targeting the thigh and hips, useful from distance.

**Low Single:** Targeting below the knee, useful when closer.

**Outside Single:** Attacking from the outside of the opponent's leg.

**Inside Single:** Attacking from between the opponent's legs.

## Setups

Single legs are typically set up with:

- Collar ties and head control
- Arm drags
- Distance management
- Creating the opportunity to shoot

## Defense

Single leg defenses include:

- **Sprawl:** Pushing hips back and extending legs.
- **Head Control:** Controlling the attacker's head.
- **Counter Takedown:** Using the attacker's momentum against them.
- **Lateral Movement:** Moving to the side to avoid the takedown.

## Wrestling Context

In wrestling, the single leg is foundational because:

- Multiple setup opportunities
- Effective from various distances
- Transitions to other techniques
- Works across different body types

## Teaching Progression

The single leg is typically taught very early in wrestling curricula.

## High-Percentage Nature

Single legs are among the highest-percentage takedowns because:

- Multiple entry points
- Versatile defensive counters
- Applicable across different matchups
- Reliable at all skill levels
"""
    },

    "osoto-gari": {
        "title": "Osoto Gari",
        "category_slug": "takedown",
        "summary": "A major outer reap from judo where the attacker sweeps the opponent's leg with their own leg.",
        "content": """## Overview

Osoto gari (also called major outer reap) is a fundamental judo and submission grappling takedown where the attacker uses their own leg to reap and sweep one of the opponent's legs, causing a takedown. The attacker controls the opponent's upper body while sweeping the leg, creating a dynamic takedown.

Osoto gari is considered one of the most powerful and high-percentage takedowns in judo and is also used in BJJ and submission grappling.

## Mechanics

The osoto gari operates by:

**Setup:** The attacker establishes a grip (typically collar and sleeve in judo).

**Hip Positioning:** The attacker positions their hip against the opponent's hip.

**Leg Sweep:** The attacker's leg swings behind the opponent's leg and sweeps it upward.

**Upper Body Control:** The attacker pulls the upper body forward while sweeping the leg.

**Takedown Completion:** The combination throws the opponent to the mat.

## Judo vs. Submission Grappling

In judo, osoto gari is:

- A fundamental throwing technique
- Often used in competition
- Considered a high-quality throw
- Typically results in a pin position

In submission grappling, osoto gari:

- Transitions to top position control
- Works similarly but without the impact objectives
- Often leads to positional dominance

## Variations

**Standard Osoto Gari:** The fundamental form.

**Osoto Gari to Back:** Using the throw to take the back.

**Osoto Gari from Clinch:** Setting up from standing clinch positions.

## Defense

Osoto gari defense includes:

- **Base Maintenance:** Keeping balance and not allowing hip contact
- **Grip Control:** Breaking the attacker's grips
- **Head Movement:** Preventing the upper body from being controlled
- **Footwork:** Moving to avoid the sweep

## Teaching Progression

Osoto gari is typically taught very early in judo curricula and is considered a fundamental throwing technique.

## Power and Effectiveness

Osoto gari is valued because:

- Generates significant force from body weight
- Difficult to defend once properly executed
- Works across different body types
- Remains highly effective at all levels
"""
    },

    "seoi-nage": {
        "title": "Seoi Nage",
        "category_slug": "takedown",
        "summary": "A shoulder throw from judo where the attacker pulls the opponent over their shoulder.",
        "content": """## Overview

Seoi nage (also called shoulder throw or back carry throw) is a fundamental judo throwing technique where the attacker pulls the opponent forward and over their shoulder, using the attacker's back and shoulder as the fulcrum for the throw. Seoi nage is one of the most commonly used throws in judo and is highly valued for its power and versatility.

## Mechanics

The seoi nage operates by:

**Setup:** The attacker establishes grips, typically collar and sleeve.

**Hip Positioning:** The attacker positions their hips below the opponent's hips.

**Upper Body Pull:** The attacker pulls the opponent's upper body forward and down.

**Back Carry:** The opponent is pulled over the attacker's back and shoulder.

**Throw Completion:** The opponent is thrown to the mat.

## Variations

**O Goshi Transition:** Using hip-based mechanics.

**Seoi Nage from Clinch:** Different setups from standing clinches.

**One-Armed Seoi Nage:** Using one arm instead of two for control.

## Setup Importance

Successful seoi nage depends heavily on:

- Proper grip and positioning
- Good hip placement beneath the opponent
- Timing and coordination
- Breaking the opponent's posture

## Defense

Seoi nage defense includes:

- **Hip Control:** Preventing hip placement beneath the attacker
- **Posture Maintenance:** Keeping an upright position
- **Grip Breaking:** Breaking the attacker's grips
- **Base:** Maintaining balance and footwork

## Teaching Progression

Seoi nage is taught very early in judo curricula and is considered one of the fundamental throwing techniques.

## Historical Significance

Seoi nage is one of the most iconic judo techniques, featured prominently in:

- Judo instruction
- Olympic judo
- Competition across all levels
- Cross-training in other martial arts

## Power Factors

Seoi nage generates power from:

- Hip positioning and drive
- Upper body pulling mechanics
- Timing and coordination
- Body weight distribution
"""
    },

    "arm-drag": {
        "title": "Arm Drag",
        "category_slug": "takedown",
        "summary": "A setup technique that drags the opponent's arm to create opening for takedowns or back control.",
        "content": """## Overview

The arm drag is a setup technique rather than a standalone takedown. The attacker drags one of the opponent's arms across the attacker's body, disrupting the opponent's base and creating opportunities for takedowns, back control, or position advancement. The arm drag is particularly valuable in no-gi grappling and submission wrestling.

## Mechanics

The arm drag operates by:

**Arm Control:** The attacker secures one of the opponent's arms.

**Dragging Motion:** The attacker drags the arm across their own body.

**Base Disruption:** The opponent's base is disrupted as a result of the arm being pulled.

**Follow-Up:** The attacker uses the disruption to execute takedowns or establish back control.

## Follow-Up Options

After a successful arm drag, the attacker can:

- **Back Take:** Using the position to take the back and establish back control.
- **Takedown:** Following up with a takedown using the disrupted base.
- **Guard:** Pulling guard and establishing a favorable guard position.
- **Control:** Advancing to other positions of control.

## Variations

**Arm Drag to Back:** The most common follow-up.

**Arm Drag to Takedown:** Following with a leg-based takedown.

**Arm Drag to Guard:** Pulling guard after dragging the arm.

## Setup Mechanics

The arm drag works best when:

- The opponent has extended arms
- The attacker has proper distance
- Timing is sharp
- The follow-up is immediately executed

## Defense

Defending against the arm drag includes:

- **Arm Positioning:** Keeping arms close and protected
- **Base Maintenance:** Maintaining balance despite arm disruption
- **Rotation:** Rotating with the drag instead of being pulled
- **Grip Control:** Preventing the arm from being controlled

## Teaching Progression

The arm drag is typically taught as an intermediate technique, often alongside takedown setups.

## No-Gi Value

The arm drag is particularly valuable in no-gi grappling because:

- Arm control is straightforward
- Leads clearly to back control
- Works well against standing opponents
- Highly effective in submission grappling
"""
    },

    "snap-down": {
        "title": "Snap Down",
        "category_slug": "takedown",
        "summary": "A control technique that pulls the opponent's head down to establish front headlock or takedown position.",
        "content": """## Overview

The snap down is a controlling technique where the attacker grips the opponent's head and pulls it downward forcefully, usually from the clinch. The snap down disrupts the opponent's posture and typically leads to front headlock control, guillotine choke attempts, or follow-up takedowns.

## Mechanics

The snap down operates by:

**Head Control:** The attacker grips the opponent's head, typically on the back of the neck or crown.

**Pulling Motion:** The attacker pulls the head downward suddenly.

**Posture Disruption:** The opponent's posture is broken and they are pulled forward.

**Position Establishment:** The attacker typically establishes front headlock position.

## From Standing Clinch

The snap down is commonly used:

- From standing collar tie
- When in clinch position
- When the opponent has good posture
- As a setup for further techniques

## Front Headlock Transitions

After a successful snap down, the attacker typically:

- Establishes a solid front headlock grip
- Transitions to guillotine choke attempts
- Sets up takedowns
- Gains dominant control

## Variations

**High Snap Down:** Pulling the head from the crown.

**Lateral Snap Down:** Pulling the head to the side.

**Snap Down with Body Control:** Adding body control for additional leverage.

## Defense

Defending against the snap down includes:

- **Head Awareness:** Protecting the head and neck area
- **Posture:** Maintaining good standing posture
- **Upper Body Strength:** Resisting the downward pull
- **Footwork:** Moving the feet to adjust for the pull

## Teaching Progression

The snap down is typically taught early in clinch work and submission wrestling.

## Standing Game Importance

The snap down is important because:

- It's a high-percentage standing technique
- It transitions well to ground control
- It's available in various clinch situations
- It often surprises opponents

## Transition Value

The snap down's greatest value is in:

- Transitioning from standing to ground
- Setting up multiple follow-up attacks
- Controlling aggressive opponents
- Establishing dominant ground positions
"""
    },

    "ankle-pick": {
        "title": "Ankle Pick",
        "category_slug": "takedown",
        "summary": "A low-level single leg takedown that targets the ankle, useful from distance and against sprawls.",
        "content": """## Overview

The ankle pick is a low-level takedown that targets the opponent's ankle, removing the foot from the ground and causing a takedown. It is similar to a single leg takedown but attacks the ankle specifically rather than the thigh or hip.

The ankle pick is particularly useful against opponents who are standing far away or defending against higher-level shoots.

## Mechanics

The ankle pick operates by:

**Ankle Target:** The attacker targets the opponent's ankle.

**Grip Establishment:** The attacker wraps around the ankle with their hands or arm.

**Lifting:** The attacker lifts the ankle, removing the foot from the ground.

**Balance Loss:** The opponent loses balance and falls.

**Control:** The attacker establishes top position control.

## Setup Differences from Single Leg

The ankle pick differs from standard single leg:

- Attacks lower on the leg (ankle vs. thigh)
- Works from greater distance
- Often used against sprawl defenses
- Requires less hip penetration

## Variations

**Standard Ankle Pick:** Direct ankle grip and lift.

**Ankle Pick to Foot Lock:** Converting the position to a foot lock attack.

**Ankle Pick to Single Leg:** Transitioning to a higher single leg position.

## Defense

Ankle pick defenses include:

- **Foot Awareness:** Protecting the ankle
- **Distance:** Maintaining proper distance
- **Base:** Keeping balance and spread legs
- **Hop/Movement:** Being mobile to avoid the pick

## Teaching Progression

The ankle pick is typically taught alongside other low-level takedown entries.

## Distance Advantage

The ankle pick is valuable because:

- Works from greater distance than high singles
- Effective against sprawl defense
- Requires different timing than body takedowns
- Complements other single leg variations

## Wrestling Application

In wrestling, the ankle pick is:

- A fundamental low-level technique
- Often used in folkstyle wrestling
- Effective at all skill levels
- Part of comprehensive takedown systems
"""
    },

    "guard-pull": {
        "title": "Guard Pull",
        "category_slug": "takedown",
        "summary": "A deliberate transition where the bottom player pulls guard, engaging the guard game strategically.",
        "content": """## Overview

A guard pull (also called pulling guard or engaging the guard) is a strategic tactical decision where the bottom player deliberately pulls the opponent into their guard rather than standing up or escaping. The guard player transitions from a disadvantageous position into closed guard, butterfly guard, or another guard variation.

Guard pulling is a fundamental aspect of Brazilian Jiu-Jitsu strategy and is sometimes controversial due to ruleset variations regarding guard pull scoring.

## Mechanics

The guard pull operates by:

**Engagement:** The bottom player grabs the top player (usually with grips on arms or collar/sleeve).

**Guard Establishment:** The bottom player pulls themselves into guard position.

**Grip Maintenance:** The bottom player maintains control through the transition.

**Position Lock:** The guard player locks their legs around the opponent's torso.

## Strategic Use

Guard pulling is strategic because:

- Moving from a losing position to a playable one
- Engaging the guard game where the guard player is strong
- Sometimes preventing scoring for the top player
- Controlling where the match takes place

## Guard Pull Types

**Closed Guard Pull:** Pulling into closed guard.

**Butterfly Guard Pull:** Pulling into butterfly guard.

**Collar/Sleeve Guard Pull:** Using collar and sleeve grips during the pull.

**High-Speed Guard Pull:** Pulling quickly to prevent top control.

## Ruleset Considerations

Guard pulling scoring varies:

- Some rulesets award points for taking a dominant position
- Guard pulls may be considered a takedown or guard engagement
- Different belt levels have different rules
- Modern rules often discourage some guard pulls

## Defense

Defending against a guard pull includes:

- **Grip Breaking:** Breaking the guard player's grips
- **Posture:** Maintaining upright posture
- **Foot Position:** Keeping feet in strong positions
- **Weight Distribution:** Distributing weight to prevent being pulled

## Teaching Progression

Guard pulling is typically taught as an intermediate to advanced guard engagement technique.

## Controversy

Guard pulling is sometimes controversial because:

- Some view it as avoiding the top game
- Ruleset changes have discouraged certain pulls
- Different perspectives on its value in jiu-jitsu
- Effects on match flow and spectator appeal

## Strategic Validity

From a jiu-jitsu perspective, guard pulling is valid because:

- It's a conscious strategic choice
- It transitions from bad position to playable one
- It's a fundamental part of the guard game
- It remains part of all major rulesets
"""
    },
}

CONCEPTS = {
    "frames": {
        "title": "Frames",
        "category_slug": "principle",
        "summary": "Defensive structures created using skeletal alignment to resist pressure without muscular force.",
        "content": """## Overview

Framing is the fundamental defensive concept in grappling of using the bones and skeletal structure of the body to create barriers against an opponent's pressure, rather than relying on muscular strength. A frame converts an opponent's force into a structural load borne by the skeleton, allowing a smaller grappler to withstand and redirect much larger forces than they could resist with muscle alone.

Understanding framing is essential to every aspect of grappling defense, from surviving under mount to retaining guard to escaping pins.

## Core Principles

**Bone Over Muscle:** A frame is strong when the load travels through aligned bones — forearm, upper arm, shoulder — into the ground or the opponent's body. It is weak when it depends on muscle contraction to maintain shape.

**Alignment Matters:** A frame is most effective when the force travels along the length of the bone rather than across it. An arm braced with a straight line from hand to shoulder can support enormous weight. The same arm bent at an awkward angle collapses easily.

**Frames Create Space, Not Positions:** The purpose of a frame is not to hold a position indefinitely but to create enough space to execute a movement — a shrimp, a reguard, an escape. Frames buy time and distance; movement converts them into positional improvement.

## Common Frames

**Forearm Frame Across the Neck:** Used in side control escapes. The bottom player places their forearm across the top player's throat or jaw, creating distance to hip escape.

**Knee-Elbow Connection:** Used in guard retention. The bottom player keeps their elbows tight to their knees, preventing the passer from closing the distance needed to complete a pass.

**Stiff Arm:** An extended arm against the shoulder or hip. Used to maintain distance in open guard and prevent pressure passers from closing space.

**Shin Frame (Knee Shield):** Used in half guard and knee shield positions. The shin creates a structural barrier preventing flattening.

## Framing Mistakes

The most common framing errors:

**Pushing:** Using muscle instead of structure. Pure muscle engagement tires the framer and lacks the mechanical advantage of skeletal alignment.

**Framing Too Far:** Creating leverage for the opponent by extending frames too much from the body.

**Framing Without Following Up:** Holding a static frame instead of using it to create movement and transitions.

**Forgetting Purpose:** Treating the frame as the goal rather than a tool for creating space and movement.

## Frame Development

Developing strong frames involves:

- Understanding skeletal leverage
- Practicing proper arm and leg positioning
- Learning when frames are most effective
- Transitioning frames into movement
- Recognizing when to abandon frames for other defenses

## Frame Progression

Beginning grapplers often use frames before understanding them. Advanced grapplers understand frame mechanics deeply and integrate them seamlessly into overall defense strategy.

"""
    },

    "grip-fighting": {
        "title": "Grip Fighting",
        "category_slug": "principle",
        "summary": "The strategic hand fighting that occurs in every position, determining control and attack opportunities.",
        "content": """## Overview

Grip fighting is the continuous battle for hand control that occurs in every grappling position. Rather than being a separate technique, grip fighting is the fundamental interaction that underlies all positional and technical grappling. The player who controls the grips typically controls the exchange, determines the pace, and creates opportunities for attacks.

Understanding grip fighting is essential to playing effective grappling at every level.

## Universal Principle

Grip fighting occurs:

- In the standing exchange
- Before and during takedown attempts
- During guard passing
- During guard retention
- During positional dominance
- Even during submission finishing

## Grip Types

**Collar Grips (Gi):** Control of the opponent's jacket collar, used for posture breaking, guard retention, and throwing.

**Sleeve Grips (Gi):** Control of the jacket sleeves, used for distance management, control, and sweeping.

**Belt Grips:** Control of the opponent's pants, used for positional dominance and prevention of movement.

**Head Control:** Grabbing the head, hair (not allowed), or head position for posture breaking and submission setup.

**Arm Grips:** Controlling the opponent's arms, used for preventing attacks and setting up own attacks.

**Body Grips:** Grips around the torso or sides, used for control and advancement.

## Who Wins Grip Fighting

The player who wins grip fighting typically:

- Breaks the opponent's posture more effectively
- Creates movement they want
- Prevents the opponent's primary attacks
- Establishes the foundation for their own attacks
- Controls the pace of the exchange

## Grip Breaking

Releasing or breaking the opponent's grips is essential to:

- Disrupt their positioning
- Free your own movement
- Escape submissions
- Prevent their attacks

## Grip Sequencing

Advanced grip fighting involves understanding the sequence of grips:

1. Establish initial grips
2. Control the opponent's grips
3. Break their grips when necessary
4. Establish different grips for the next phase
5. Maintain offensive grip advantage

## Grip Strength

While grip strength helps, proper grip technique is more important than brute strength. A properly placed grip held with correct mechanics is stronger than a poorly placed grip with maximum effort.

## Hand Placement Importance

Where the hands are placed on the opponent's body determines:

- What movements are possible
- What attacks are threatened
- How the opponent will respond
- What counter-attacks are available

## Modern Emphasis

Contemporary high-level grappling emphasizes grip fighting as central to all techniques. Understanding grip fighting deeply leads to better execution of all other techniques.

"""
    },

    "guard-retention": {
        "title": "Guard Retention",
        "category_slug": "principle",
        "summary": "The defensive principle of maintaining guard position against passing attempts through positioning and technique.",
        "content": """## Overview

Guard retention is the set of defensive principles and techniques used to maintain the guard position against passing attempts. Rather than a single technique, guard retention is a fundamental defensive philosophy encompassing positioning, pressure management, framing, and dynamic transitions.

Strong guard retention is essential to playing effective guard in modern jiu-jitsu, particularly against athletic passers and pressure-based passing styles.

## Core Principles

**Stay Connected:** The bottom player must remain physically connected to the top player, preventing the separation needed for effective passing.

**Manage Pressure:** Without absorbing or redirecting the top player's pressure, flattening and passing becomes possible. Managing pressure requires frames, hip movement, and constant adjustment.

**Create Angles:** Positioning the body at angles (rather than flat) prevents the top player from establishing stable passing position.

**Footwork:** Constant foot and knee positioning changes disrupt the top player's passing setup.

**Underhook Importance:** Securing an underhook is often the key to guard retention, enabling sweeping options and preventing heavy pressure positions.

## Retention Techniques

**Framing:** Using skeletal structure to create barriers against pressure.

**Cupping:** Gripping behind the knee to maintain leg position and connection.

**Shin Frames:** Placing the shin across the opponent's body (knee shield) to prevent flattening.

**Bridge:** Bridging to create space and prevent pin development.

**Shrimp Motion:** The hip escape motion that maintains separation and prevents passing advantage.

## Against Pressure Passing

Pressure passing attempts to flatten and control the guard player through weight and body position. Retention against pressure involves:

- Maintaining hip elevation
- Creating frames for space
- Using underhooks
- Timing shrimp escapes

## Against Speed Passing

Speed-based passing attempts to move laterally and bypass the legs quickly. Retention against speed involves:

- Maintaining connection
- Quick transitions
- Directional awareness
- Anticipating passing direction

## Against Leg Lock Threats

Modern guard passing often includes leg lock threats. Retention against leg locks involves:

- Understanding leg lock entry positions
- Preventing dangerous entanglement
- Quick disengagement from suspect positions
- Counterattacking when appropriate

## Transitions vs. Static Retention

While static retention (holding the guard in place) is part of the picture, dynamic retention (flowing through transitions) is often more effective. Rather than holding a single guard position indefinitely, the guard player transitions between positions while defending passing attempts.

## Guard Retention Fundamentals

Every guard player should develop:

- Strong knee-to-elbow connection
- Effective framing
- Hip mobility
- Quick positional transitions
- Understanding of when to hold vs. when to transition

## Teaching Progression

Guard retention is typically emphasized in intermediate curricula as students develop basic guard technique and face more sophisticated passing attempts.

"""
    },

    "underhooks": {
        "title": "Underhooks",
        "category_slug": "principle",
        "summary": "Inside position control achieved by placing an arm under the opponent's arm for dominant grip position.",
        "content": """## Overview

Underhooks are a fundamental grappling position where one grappler places their arm under the opponent's arm(s), gaining inside position control. Underhooks are among the most valuable positional controls in grappling, providing access to back takes, dominant position transitions, and numerous submission setups.

Understanding underhooks is essential to modern grappling at all levels.

## Why Underhooks Matter

The underhook position is valuable because:

- It puts you in inside position (more dominant than outside position)
- It prevents the opponent from escaping
- It gives access to multiple attacks and transitions
- It's defensive against many opponent attacks
- It's applicable from nearly every position

## Mechanics

An underhook is established by:

**Arm Placement:** One arm passes under the opponent's arm (underneath their armpit).

**Control Point:** The arm wraps behind the opponent's torso or around their upper back.

**Position:** The underhook creates an inside position advantage.

**Connection:** The underhook remains connected throughout subsequent movements.

## Underhook Applications

Underhooks are used for:

- **Back Takes:** One of the primary applications, using underhooks to take the back
- **Guard Passing:** Many modern guards passes use underhook control
- **Control:** Pinning and controlling the opponent
- **Submissions:** Setting up submissions from underhook positions
- **Positional Advantage:** Creating dominant positioning

## Underhook vs. Overhook

The underhook and overhook are opposites:

- Underhook is inside position (more dominant)
- Overhook is outside position (less dominant)
- Underhooks are generally preferred
- Both are valuable in different contexts

## Technical Depth

Modern grappling emphasizes underhook mastery because:

- It's fundamental to modern top position
- Many contemporary systems focus on underhook control
- It transitions to multiple attacks
- It provides comprehensive position control

## In Different Positions

Underhooks apply across:

- Clinch work and standing positions
- Guard passing scenarios
- Back take sequences
- Ground-based submissions
- Scrambles and transitions

## Teaching Progression

Underhooks are typically taught early in grappling curricula because they're foundational to modern technique and positioning principles.
"""
    },

    "pressure-passing": {
        "title": "Pressure Passing",
        "category_slug": "principle",
        "summary": "Guard passing strategy emphasizing body weight and constant pressure over technical footwork.",
        "content": """## Overview

Pressure passing is a guard passing philosophy where the passer emphasizes applying constant body weight and pressure to the guard player rather than relying on athletic footwork or complex technical sequences. The passer stays heavy and connected, using pressure to simplify the guard player's options.

Pressure passing has become increasingly dominant in modern high-level competition.

## Core Principles

Pressure passing emphasizes:

**Body Weight:** Using gravity and body weight as the primary tool rather than relying on athleticism.

**Constant Connection:** Maintaining chest-to-chest or hip-to-hip contact throughout the pass.

**Pressure:** Applying steady, unrelenting pressure that wears down the guard player.

**Simplicity:** Fewer complex foot movements, more direct pressure application.

## Advantages of Pressure Passing

Pressure passing is effective because:

- Works regardless of the passer's athleticism
- Wears down the guard player over time
- Difficult to defend against constant pressure
- Effective even when the guard player is skilled
- Scales well as the passer gains experience

## Pressure Passing vs. Athletic Passing

Athletic passing emphasizes:

- Footwork and movement
- Speed and athleticism
- Complex technical sequences

Pressure passing emphasizes:

- Body weight and connection
- Constant pressure
- Simplicity and directness

## Positioning for Pressure

Effective pressure passing requires:

- Low center of gravity (knees bent)
- Wide base for stability
- Tight connection to the guard player
- Weight distributed through the body, not the arms

## Common Pressure Passing Techniques

Pressure passing utilizes:

- Body lock passes
- Stack passes
- Over-under passes
- Pin-based passes
- Weight-distribution focused techniques

## Against Different Guards

Pressure passing works well against:

- Butterfly guard (crushes the guard)
- Closed guard (flattens the player)
- Half guard (applies constant pressure)
- Most guard variations

## Teaching Progression

Pressure passing is typically taught as a fundamental passing philosophy, often to intermediate and advanced students.

## Modern Dominance

Pressure passing has become increasingly prevalent because:

- High-level competitors use it effectively
- It's less dependent on athleticism than other methods
- It provides consistent results
- It combines well with other passing systems
"""
    },

    "base": {
        "title": "Base",
        "category_slug": "principle",
        "summary": "Positional stability and balance in grappling, the foundation for offensive and defensive work.",
        "content": """## Overview

Base in grappling refers to the stability, balance, and positional foundation a grappler establishes. A strong base provides stability for applying techniques, resisting opponent pressure, and preventing being swept or thrown. Base is fundamental to both offensive and defensive grappling.

Understanding base is essential to developing effective technique and physical stability.

## What Makes a Strong Base

A strong base includes:

**Wide Foot Position:** Feet spread wider than shoulder-width for lateral stability.

**Bent Knees:** Knees slightly bent to lower center of gravity and prevent being knocked over.

**Weight Distribution:** Weight distributed evenly across feet and base points.

**Balance:** Maintaining balance despite opponent pressure and movement.

**Connection:** Maintaining connection to the ground or mat through multiple points.

## Base in Different Positions

Base is important across positions:

- **Standing:** Wide stance, bent knees, weight forward/centered
- **Mount:** Knees on either side creating base, weight on knees
- **Side Control:** Body weight distributed across hips and shoulders
- **Guard:** Guard player's back and shoulder blades as the base
- **Open Guard:** Feet and hands creating the base

## Losing Base

Losing base happens when:

- The grappler is knocked off balance
- The base points are swept or removed
- Weight is too forward or back
- Center of gravity is too high
- The grappler is caught in compromising position

## Consequences of Poor Base

Poor base creates:

- Vulnerability to sweeps
- Difficulty applying pressure
- Easy takedowns
- Loss of positioning
- Compromised submissions

## Base and Footwork

Footwork and base are closely related:

- Good footwork maintains base
- Movement happens from a strong base
- Quick recovery of base after movement
- Continuous base management during transitions

## Teaching Progression

Base is taught very early in grappling, as it's foundational to all other techniques.

## Base as Foundation

Base is valuable because:

- It's foundational to all techniques
- Without it, most attacks fail
- It's relatively simple to teach
- It immediately improves grappling effectiveness
"""
    },

    "kuzushi": {
        "title": "Kuzushi",
        "category_slug": "principle",
        "summary": "The principle of breaking the opponent's balance to set up techniques and attacks.",
        "content": """## Overview

Kuzushi (also called off-balancing) is the principle of breaking or disrupting the opponent's balance and stability. In judo, kuzushi is foundational to throwing technique — a properly executed kuzushi often makes the throw almost automatic. In all grappling arts, kuzushi creates opportunities for takedowns, sweeps, and transitions.

## Historical Importance

Kuzushi comes from judo tradition where it's taught as:

- The first principle of throwing
- The necessary precondition for successful throws
- A distinct phase of technique execution
- A principle applicable across all grappling

## Principles of Kuzushi

Kuzushi works by:

**Disrupting Balance:** Moving the opponent's center of gravity away from their base.

**Creating Vulnerability:** Leaving the opponent momentarily unable to defend.

**Timing:** Executing at the moment of maximum vulnerability.

**Direction:** Breaking balance in a specific direction that favors the attacker.

## Methods of Creating Kuzushi

Kuzushi can be created by:

- **Pulling:** Pulling the opponent off balance
- **Pushing:** Pushing the opponent to disrupt stability
- **Lateral Movement:** Moving the opponent to the side
- **Weight Shift:** Causing the opponent to shift weight disadvantageously
- **Grip Control:** Using grips to disrupt balance

## Kuzushi in Different Contexts

Kuzushi applies to:

- **Throwing:** Breaking balance before throwing
- **Takedowns:** Disrupting base before takedowns
- **Sweeps:** Breaking balance before sweeping
- **Submissions:** Creating opportunities through disrupted balance
- **Escapes:** Disrupting opponent balance to escape

## Timing Importance

Successful kuzushi depends on:

- Proper timing (catching the opponent committed)
- Reading the opponent's weight distribution
- Using the opponent's own momentum
- Quick execution after breaking balance

## Teaching Progression

Kuzushi is taught early in judo curricula and is increasingly recognized as important in other grappling arts.

## Universal Principle

Kuzushi is valuable because:

- It applies across all grappling arts
- It's fundamental to technique effectiveness
- It can be applied at all skill levels
- It emphasizes understanding over pure strength
"""
    },

    "chain-wrestling": {
        "title": "Chain Wrestling",
        "category_slug": "principle",
        "summary": "The technique of linking attacks sequentially, where opponent defense creates the setup for the next attack.",
        "content": """## Overview

Chain wrestling is the principle of linking attacks sequentially such that each attack follows naturally from the opponent's defense against the previous attack. Rather than executing isolated techniques, chain wrestling strings together multiple attacks in a flowing sequence where each technique sets up the next.

Chain wrestling is a fundamental principle in both wrestling and judo.

## Core Concept

Chain wrestling works by:

**Primary Attack:** Executing an initial attack or technique.

**Opponent Defense:** The opponent reacts by defending against the attack.

**Follow-Up:** The opponent's defensive response creates the perfect setup for a follow-up attack.

**Flow:** Techniques flow together, continuously attacking while the opponent is responding defensively.

## Examples of Chains

Common chains include:

- **Arm Drag to Back Take:** Arm drag disrupts base, setting up the back take
- **Collar Tie to Snap Down:** Collar control leads to snap down setup
- **Attempted Takedown to Switch:** Takedown defense sets up a counter attack
- **Guard Pass to Submission:** Passing guard puts opponent in position for submission
- **Throw to Pin Transition:** Throw landing sets up immediate pinning position

## Strategic Value

Chain wrestling is valuable because:

- Opponent defense becomes the setup for the next attack
- It creates continuous pressure rather than isolated attacks
- It's difficult for the opponent to defend multiple sequential attacks
- It creates natural flow and rhythm
- It rewards understanding and positioning over pure technique

## Teaching Progression

Chain wrestling is typically taught as an intermediate to advanced concept, after foundational techniques are established.

## Mental Aspects

Successful chain wrestling requires:

- Understanding multiple techniques deeply
- Reading opponent responses
- Maintaining offensive pressure
- Staying creative and adaptable
- Anticipating defensive reactions

## Offensive Philosophy

Chain wrestling emphasizes:

- Continuous offense
- Flowing transitions
- Attacking multiple angles
- Not settling for single techniques
- Creating dilemmas (defend this, get caught by that)

## Historical Context

Chain wrestling comes from wrestling tradition where it's known as:

- "Position wrestling"
- "Continuous wrestling"
- "The flow"
- "Daisy chain attacks"

## Modern Relevance

In modern grappling, chain wrestling is:

- Increasingly recognized as a fundamental principle
- Used at all high levels of competition
- Applicable across all grappling styles
- A path to efficient, effective grappling
"""
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# RELATIONSHIP DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

RELATIONSHIPS = [
    # ═══════════════════════════════════════════════════════════════════════
    # SUBMISSIONS → submits_from → POSITIONS
    # Every submission lists every position it's commonly available from
    # ═══════════════════════════════════════════════════════════════════════

    # Armbar — available from guard, mount, side control, back
    ("armbar", "closed-guard", "submits_from"),
    ("armbar", "mount", "submits_from"),
    ("armbar", "side-control", "submits_from"),
    ("armbar", "back-control", "submits_from"),
    ("armbar", "rubber-guard", "submits_from"),

    # Triangle Choke — guard, mount, back, rubber guard
    ("triangle-choke", "closed-guard", "submits_from"),
    ("triangle-choke", "mount", "submits_from"),
    ("triangle-choke", "back-control", "submits_from"),
    ("triangle-choke", "rubber-guard", "submits_from"),

    # Guillotine — closed guard, half guard, butterfly, standing (turtle snap-down)
    ("guillotine-choke", "closed-guard", "submits_from"),
    ("guillotine-choke", "half-guard", "submits_from"),
    ("guillotine-choke", "butterfly-guard", "submits_from"),
    ("guillotine-choke", "turtle-position", "submits_from"),

    # Kimura — closed guard, half guard, side control, north-south, butterfly
    ("kimura", "closed-guard", "submits_from"),
    ("kimura", "half-guard", "submits_from"),
    ("kimura", "side-control", "submits_from"),
    ("kimura", "north-south", "submits_from"),
    ("kimura", "butterfly-guard", "submits_from"),

    # Americana — mount, side control
    ("americana", "mount", "submits_from"),
    ("americana", "side-control", "submits_from"),

    # Omoplata — closed guard, rubber guard, spider guard
    ("omoplata", "closed-guard", "submits_from"),
    ("omoplata", "rubber-guard", "submits_from"),
    ("omoplata", "spider-guard", "submits_from"),

    # D'Arce — half guard, turtle, side control, butterfly
    ("darce-choke", "half-guard", "submits_from"),
    ("darce-choke", "turtle-position", "submits_from"),
    ("darce-choke", "side-control", "submits_from"),
    ("darce-choke", "butterfly-guard", "submits_from"),

    # Anaconda — turtle, front headlock positions
    ("anaconda-choke", "turtle-position", "submits_from"),
    ("anaconda-choke", "half-guard", "submits_from"),

    # Rear Naked Choke — back control only
    ("rear-naked-choke", "back-control", "submits_from"),

    # Heel Hook — all leg entanglements
    ("heel-hook", "ashi-garami", "submits_from"),
    ("heel-hook", "50-50-guard", "submits_from"),
    ("heel-hook", "saddle-position", "submits_from"),
    ("heel-hook", "single-leg-x", "submits_from"),

    # Toe Hold — ashi, 50/50, half guard (from top)
    ("toe-hold", "ashi-garami", "submits_from"),
    ("toe-hold", "50-50-guard", "submits_from"),
    ("toe-hold", "half-guard", "submits_from"),

    # Kneebar — saddle, ashi, half guard transitions
    ("kneebar", "saddle-position", "submits_from"),
    ("kneebar", "ashi-garami", "submits_from"),
    ("kneebar", "half-guard", "submits_from"),

    # Straight Ankle Lock — ashi garami, single leg x, 50/50
    ("straight-ankle-lock", "ashi-garami", "submits_from"),
    ("straight-ankle-lock", "single-leg-x", "submits_from"),
    ("straight-ankle-lock", "50-50-guard", "submits_from"),

    # Ezekiel — mount, half guard, closed guard (inside opponent's guard)
    ("ezekiel-choke", "mount", "submits_from"),
    ("ezekiel-choke", "half-guard", "submits_from"),
    ("ezekiel-choke", "closed-guard", "submits_from"),
    ("ezekiel-choke", "side-control", "submits_from"),

    # Bow and Arrow — back control
    ("bow-and-arrow-choke", "back-control", "submits_from"),

    # Cross Collar Choke — closed guard, mount
    ("cross-collar-choke", "closed-guard", "submits_from"),
    ("cross-collar-choke", "mount", "submits_from"),

    # Loop Choke — turtle (snap-down entry), half guard top
    ("loop-choke", "turtle-position", "submits_from"),
    ("loop-choke", "half-guard", "submits_from"),

    # Arm Triangle — mount, side control, half guard
    ("arm-triangle", "mount", "submits_from"),
    ("arm-triangle", "side-control", "submits_from"),
    ("arm-triangle", "half-guard", "submits_from"),

    # North-South Choke — north-south
    ("north-south-choke", "north-south", "submits_from"),

    # Calf Slicer — half guard (lockdown counter), back control (truck)
    ("calf-slicer", "half-guard", "submits_from"),
    ("calf-slicer", "back-control", "submits_from"),

    # Wrist Lock — closed guard, mount, spider guard, side control
    ("wrist-lock", "closed-guard", "submits_from"),
    ("wrist-lock", "mount", "submits_from"),
    ("wrist-lock", "spider-guard", "submits_from"),
    ("wrist-lock", "side-control", "submits_from"),

    # Mounted Triangle (use triangle-from-bottom slug)
    ("triangle-from-bottom", "mount", "submits_from"),

    # ═══════════════════════════════════════════════════════════════════════
    # SUBMISSION VARIATIONS
    # ═══════════════════════════════════════════════════════════════════════
    ("americana", "kimura", "variation_of"),
    ("darce-choke", "anaconda-choke", "variation_of"),
    ("arm-triangle", "darce-choke", "related_to"),
    ("arm-triangle", "anaconda-choke", "related_to"),
    ("north-south-choke", "arm-triangle", "related_to"),
    ("toe-hold", "heel-hook", "related_to"),
    ("kneebar", "straight-ankle-lock", "related_to"),
    ("bow-and-arrow-choke", "cross-collar-choke", "related_to"),
    ("triangle-from-bottom", "triangle-choke", "variation_of"),

    # ═══════════════════════════════════════════════════════════════════════
    # SWEEPS — requires_position + transitions_to
    # ═══════════════════════════════════════════════════════════════════════

    # Scissor Sweep: closed guard → mount
    ("scissor-sweep", "closed-guard", "requires_position"),
    ("scissor-sweep", "mount", "transitions_to"),

    # Hip Bump: closed guard → mount (or sets up guillotine/kimura)
    ("hip-bump-sweep", "closed-guard", "requires_position"),
    ("hip-bump-sweep", "mount", "transitions_to"),

    # Butterfly Sweep: butterfly guard → side control or mount
    ("butterfly-sweep", "butterfly-guard", "requires_position"),
    ("butterfly-sweep", "mount", "transitions_to"),

    # Pendulum: closed guard → mount
    ("pendulum-sweep", "closed-guard", "requires_position"),
    ("pendulum-sweep", "mount", "transitions_to"),

    # Flower Sweep: closed guard → mount
    ("flower-sweep", "closed-guard", "requires_position"),
    ("flower-sweep", "mount", "transitions_to"),

    # Berimbolo: DLR → back control
    ("berimbolo", "de-la-riva-guard", "requires_position"),
    ("berimbolo", "back-control", "transitions_to"),

    # Tripod Sweep: open guard (DLR/spider) → top position
    ("tripod-sweep", "de-la-riva-guard", "requires_position"),
    ("tripod-sweep", "spider-guard", "requires_position"),
    ("tripod-sweep", "headquarters", "transitions_to"),

    # Sickle Sweep: open guard → top position
    ("sickle-sweep", "de-la-riva-guard", "requires_position"),
    ("sickle-sweep", "spider-guard", "requires_position"),
    ("sickle-sweep", "headquarters", "transitions_to"),

    # ═══════════════════════════════════════════════════════════════════════
    # PASSES — counters guards + transitions_to dominant positions
    # ═══════════════════════════════════════════════════════════════════════

    # Toreando: counters open guards, lands in side control
    ("toreando-pass", "de-la-riva-guard", "counters"),
    ("toreando-pass", "spider-guard", "counters"),
    ("toreando-pass", "butterfly-guard", "counters"),
    ("toreando-pass", "side-control", "transitions_to"),

    # Knee Slice: counters half guard, DLR, z-guard, lands in side control or KOB
    ("knee-slice", "half-guard", "counters"),
    ("knee-slice", "z-guard", "counters"),
    ("knee-slice", "de-la-riva-guard", "counters"),
    ("knee-slice", "side-control", "transitions_to"),
    ("knee-slice", "knee-on-belly", "transitions_to"),

    # Leg Drag: counters DLR, spider, x-guard, lands in side control
    ("leg-drag", "de-la-riva-guard", "counters"),
    ("leg-drag", "spider-guard", "counters"),
    ("leg-drag", "x-guard", "counters"),
    ("leg-drag", "side-control", "transitions_to"),

    # Over-Under: counters half guard, closed guard, lands in side control
    ("over-under-pass", "half-guard", "counters"),
    ("over-under-pass", "closed-guard", "counters"),
    ("over-under-pass", "side-control", "transitions_to"),

    # Stack Pass: counters closed guard, spider guard, lands in side control
    ("stack-pass", "closed-guard", "counters"),
    ("stack-pass", "spider-guard", "counters"),
    ("stack-pass", "side-control", "transitions_to"),

    # Long Step: counters DLR, half guard, lands in side control
    ("long-step-pass", "de-la-riva-guard", "counters"),
    ("long-step-pass", "half-guard", "counters"),
    ("long-step-pass", "side-control", "transitions_to"),

    # Body Lock: counters half guard, butterfly, closed guard
    ("body-lock-pass", "half-guard", "counters"),
    ("body-lock-pass", "butterfly-guard", "counters"),
    ("body-lock-pass", "closed-guard", "counters"),
    ("body-lock-pass", "side-control", "transitions_to"),

    # X-Pass: counters DLR, spider, butterfly, lands in side control
    ("x-pass", "de-la-riva-guard", "counters"),
    ("x-pass", "spider-guard", "counters"),
    ("x-pass", "butterfly-guard", "counters"),
    ("x-pass", "side-control", "transitions_to"),

    # ═══════════════════════════════════════════════════════════════════════
    # TAKEDOWNS → transitions_to positions
    # ═══════════════════════════════════════════════════════════════════════
    ("double-leg-takedown", "side-control", "transitions_to"),
    ("single-leg", "side-control", "transitions_to"),
    ("osoto-gari", "side-control", "transitions_to"),
    ("seoi-nage", "side-control", "transitions_to"),
    ("seoi-nage", "mount", "transitions_to"),
    ("arm-drag", "back-control", "transitions_to"),
    ("snap-down", "turtle-position", "transitions_to"),
    ("ankle-pick", "side-control", "transitions_to"),
    ("guard-pull", "closed-guard", "transitions_to"),

    # ═══════════════════════════════════════════════════════════════════════
    # POSITIONAL TRANSITIONS — how positions flow into each other
    # ═══════════════════════════════════════════════════════════════════════
    ("side-control", "mount", "transitions_to"),
    ("side-control", "knee-on-belly", "transitions_to"),
    ("side-control", "north-south", "transitions_to"),
    ("side-control", "back-control", "transitions_to"),
    ("mount", "back-control", "transitions_to"),
    ("mount", "side-control", "transitions_to"),
    ("knee-on-belly", "mount", "transitions_to"),
    ("knee-on-belly", "back-control", "transitions_to"),
    ("knee-on-belly", "side-control", "transitions_to"),
    ("back-control", "mount", "transitions_to"),
    ("north-south", "side-control", "transitions_to"),
    ("north-south", "mount", "transitions_to"),
    ("headquarters", "side-control", "transitions_to"),
    ("headquarters", "knee-on-belly", "transitions_to"),

    # ═══════════════════════════════════════════════════════════════════════
    # ESCAPES — escapes_from dominant positions into guards
    # ═══════════════════════════════════════════════════════════════════════
    ("half-guard", "side-control", "escapes_from"),
    ("half-guard", "mount", "escapes_from"),
    ("closed-guard", "side-control", "escapes_from"),
    ("turtle-position", "side-control", "escapes_from"),
    ("turtle-position", "back-control", "escapes_from"),
    ("butterfly-guard", "side-control", "escapes_from"),
    ("deep-half-guard", "side-control", "escapes_from"),
    ("deep-half-guard", "mount", "escapes_from"),

    # ═══════════════════════════════════════════════════════════════════════
    # POSITION VARIATIONS — variation_of
    # ═══════════════════════════════════════════════════════════════════════
    ("deep-half-guard", "half-guard", "variation_of"),
    ("z-guard", "half-guard", "variation_of"),
    ("rubber-guard", "closed-guard", "variation_of"),
    ("single-leg-x", "ashi-garami", "variation_of"),
    ("50-50-guard", "ashi-garami", "variation_of"),
    ("saddle-position", "ashi-garami", "variation_of"),
    ("x-guard", "single-leg-x", "related_to"),
    ("north-south", "side-control", "variation_of"),

    # ═══════════════════════════════════════════════════════════════════════
    # SETS_UP — technique A sets up technique B
    # ═══════════════════════════════════════════════════════════════════════
    ("arm-drag", "back-control", "sets_up"),
    ("arm-drag", "single-leg", "sets_up"),
    ("snap-down", "guillotine-choke", "sets_up"),
    ("snap-down", "darce-choke", "sets_up"),
    ("snap-down", "anaconda-choke", "sets_up"),
    ("hip-bump-sweep", "guillotine-choke", "sets_up"),
    ("hip-bump-sweep", "kimura", "sets_up"),
    ("kimura", "hip-bump-sweep", "sets_up"),
    ("armbar", "triangle-choke", "sets_up"),
    ("triangle-choke", "armbar", "sets_up"),
    ("triangle-choke", "omoplata", "sets_up"),
    ("omoplata", "triangle-choke", "sets_up"),
    ("omoplata", "armbar", "sets_up"),
    ("scissor-sweep", "armbar", "sets_up"),
    ("double-leg-takedown", "single-leg", "sets_up"),
    ("single-leg", "double-leg-takedown", "sets_up"),
    ("knee-on-belly", "armbar", "sets_up"),
    ("knee-on-belly", "arm-triangle", "sets_up"),
    ("x-guard", "butterfly-sweep", "sets_up"),
    ("single-leg-x", "heel-hook", "sets_up"),
    ("single-leg-x", "straight-ankle-lock", "sets_up"),
    ("de-la-riva-guard", "berimbolo", "sets_up"),
    ("de-la-riva-guard", "x-guard", "sets_up"),
    ("spider-guard", "triangle-choke", "sets_up"),
    ("spider-guard", "omoplata", "sets_up"),
    ("closed-guard", "armbar", "sets_up"),
    ("closed-guard", "triangle-choke", "sets_up"),
    ("closed-guard", "kimura", "sets_up"),
    ("closed-guard", "guillotine-choke", "sets_up"),
    ("mount", "armbar", "sets_up"),
    ("mount", "arm-triangle", "sets_up"),
    ("mount", "americana", "sets_up"),
    ("mount", "ezekiel-choke", "sets_up"),
    ("mount", "cross-collar-choke", "sets_up"),
    ("back-control", "rear-naked-choke", "sets_up"),
    ("back-control", "bow-and-arrow-choke", "sets_up"),
    ("side-control", "kimura", "sets_up"),
    ("side-control", "americana", "sets_up"),
    ("side-control", "arm-triangle", "sets_up"),
    ("north-south", "north-south-choke", "sets_up"),
    ("north-south", "kimura", "sets_up"),
    ("ashi-garami", "heel-hook", "sets_up"),
    ("ashi-garami", "straight-ankle-lock", "sets_up"),
    ("ashi-garami", "toe-hold", "sets_up"),
    ("ashi-garami", "kneebar", "sets_up"),
    ("saddle-position", "heel-hook", "sets_up"),
    ("saddle-position", "kneebar", "sets_up"),
    ("50-50-guard", "heel-hook", "sets_up"),
    ("50-50-guard", "toe-hold", "sets_up"),
    ("50-50-guard", "straight-ankle-lock", "sets_up"),

    # ═══════════════════════════════════════════════════════════════════════
    # CONCEPTS — related_to positions and techniques they apply to
    # ═══════════════════════════════════════════════════════════════════════

    # Frames — defensive concept, most relevant in guard and escapes
    ("frames", "half-guard", "related_to"),
    ("frames", "closed-guard", "related_to"),
    ("frames", "side-control", "related_to"),
    ("frames", "mount", "related_to"),
    ("frames", "guard-retention", "related_to"),

    # Underhooks — inside position, critical in half guard, butterfly, side control
    ("underhooks", "half-guard", "related_to"),
    ("underhooks", "butterfly-guard", "related_to"),
    ("underhooks", "side-control", "related_to"),
    ("underhooks", "back-control", "related_to"),

    # Guard Retention — keeping guard against passes
    ("guard-retention", "de-la-riva-guard", "related_to"),
    ("guard-retention", "spider-guard", "related_to"),
    ("guard-retention", "butterfly-guard", "related_to"),
    ("guard-retention", "half-guard", "related_to"),
    ("guard-retention", "closed-guard", "related_to"),
    ("guard-retention", "frames", "related_to"),

    # Pressure Passing — weight-based passing concept
    ("pressure-passing", "over-under-pass", "related_to"),
    ("pressure-passing", "body-lock-pass", "related_to"),
    ("pressure-passing", "stack-pass", "related_to"),
    ("pressure-passing", "knee-slice", "related_to"),
    ("pressure-passing", "side-control", "related_to"),

    # Grip Fighting — hand fighting for control
    ("grip-fighting", "spider-guard", "related_to"),
    ("grip-fighting", "de-la-riva-guard", "related_to"),
    ("grip-fighting", "closed-guard", "related_to"),
    ("grip-fighting", "butterfly-guard", "related_to"),

    # Base — stability, most relevant in top positions
    ("base", "mount", "related_to"),
    ("base", "side-control", "related_to"),
    ("base", "knee-on-belly", "related_to"),
    ("base", "headquarters", "related_to"),

    # Kuzushi — off-balancing, central to throws and sweeps
    ("kuzushi", "osoto-gari", "related_to"),
    ("kuzushi", "seoi-nage", "related_to"),
    ("kuzushi", "double-leg-takedown", "related_to"),
    ("kuzushi", "scissor-sweep", "related_to"),
    ("kuzushi", "butterfly-sweep", "related_to"),

    # Chain Wrestling — linking attacks
    ("chain-wrestling", "single-leg", "related_to"),
    ("chain-wrestling", "double-leg-takedown", "related_to"),
    ("chain-wrestling", "snap-down", "related_to"),
    ("chain-wrestling", "arm-drag", "related_to"),
    ("chain-wrestling", "ankle-pick", "related_to"),
]


def seed_comprehensive():
    """Main seeding function."""
    app = create_app()
    with app.app_context():
        # Ensure DB tables exist
        db.create_all()

        # Get admin user
        user = User.query.filter_by(username='keenan').first()
        if not user:
            user = User.query.first()
        if not user:
            print("ERROR: No user found. Run the app and create a user first.")
            return

        uid = user.id
        print(f"Seeding with user: {user.username}")

        # Create subcategories
        print("\n[Subcategories]")
        subcats = {
            "submission": get_or_create_subcategory("technique", "Submission", "submission", "Submission techniques including chokes and joint locks", uid),
            "sweep": get_or_create_subcategory("technique", "Sweep", "sweep", "Guard sweeping and reversal techniques", uid),
            "pass": get_or_create_subcategory("technique", "Pass", "pass", "Guard passing techniques", uid),
            "takedown": get_or_create_subcategory("technique", "Takedown", "takedown", "Takedown techniques from standing", uid),
            "guard": get_or_create_subcategory("position", "Guard", "guard", "Guard positions and variations", uid),
            "dominant-position": get_or_create_subcategory("position", "Dominant Position", "dominant-position", "Top positions of dominance", uid),
            "transitional": get_or_create_subcategory("position", "Transitional", "transitional", "Transitional positions", uid),
            "leg-entanglement": get_or_create_subcategory("position", "Leg Entanglement", "leg-entanglement", "Leg entanglement positions and leg lock entries", uid),
            "principle": get_or_create_subcategory("concept", "Principle", "principle", "Fundamental principles and concepts", uid),
        }

        # Seed articles
        print("\n[Positions]")
        for slug, data in POSITIONS.items():
            seed_article(data["title"], slug, data["content"], data["summary"], data["category_slug"], uid)

        print("\n[Submissions]")
        for slug, data in SUBMISSIONS.items():
            seed_article(data["title"], slug, data["content"], data["summary"], data["category_slug"], uid)

        print("\n[Sweeps & Passes]")
        for slug, data in SWEEPS_AND_PASSES.items():
            seed_article(data["title"], slug, data["content"], data["summary"], data["category_slug"], uid)

        print("\n[Concepts]")
        for slug, data in CONCEPTS.items():
            seed_article(data["title"], slug, data["content"], data["summary"], data["category_slug"], uid)

        # Create relationships
        print("\n[Relationships]")
        rel_count = 0
        for src_slug, tgt_slug, rel_type in RELATIONSHIPS:
            if add_relationship(src_slug, tgt_slug, rel_type, uid):
                rel_count += 1

        db.session.commit()

        # Statistics
        total_articles = Article.query.count()
        total_rels = ArticleRelationship.query.count()
        total_cats = Category.query.count()

        print(f"\n✓ Done!")
        print(f"  Articles: {total_articles}")
        print(f"  Relationships: {total_rels}")
        print(f"  Categories: {total_cats}")
        print(f"\nVisit http://localhost:5000 to see the wiki.")


if __name__ == '__main__':
    seed_comprehensive()

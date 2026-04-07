"""
Seed: Standing-tier articles and additional content for sparse graph tiers.
Safe to re-run — skips existing articles by slug.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Article, ArticleRevision, Category
from app.models.article import ArticleRelationship


def get_or_create_subcategory(parent_slug, name, slug, description, user_id):
    cat = Category.query.filter_by(slug=slug).first()
    if cat:
        return cat
    parent = Category.query.filter_by(slug=parent_slug).first()
    if not parent:
        print(f"  [warn] Parent '{parent_slug}' not found")
        return None
    cat = Category(name=name, slug=slug, description=description,
                   parent_id=parent.id, created_by_id=user_id)
    db.session.add(cat)
    db.session.flush()
    print(f"  [created] Subcategory: {name}")
    return cat


def seed_article(title, slug, content, summary, category_slug, author_id):
    existing = Article.query.filter_by(slug=slug).first()
    if existing:
        return existing
    cat = Category.query.filter_by(slug=category_slug).first()
    if not cat:
        print(f"  [warn] Category '{category_slug}' not found for '{title}'")
        return None
    article = Article(title=title, slug=slug, content=content.strip(),
                      summary=summary, author_id=author_id, category_id=cat.id,
                      category=category_slug, is_published=True, view_count=0)
    db.session.add(article)
    db.session.flush()
    rev = ArticleRevision(article_id=article.id, editor_id=author_id,
                          content=content.strip(), edit_summary='Initial article creation',
                          revision_number=1)
    db.session.add(rev)
    print(f"  [created] {title}")
    return article


def add_rel(src, tgt, rtype, uid):
    s = Article.query.filter_by(slug=src).first()
    t = Article.query.filter_by(slug=tgt).first()
    if not s or not t:
        return False
    if ArticleRelationship.query.filter_by(
        source_article_id=s.id, target_article_id=t.id, relationship_type=rtype
    ).first():
        return False
    db.session.add(ArticleRelationship(
        source_article_id=s.id, target_article_id=t.id,
        relationship_type=rtype, created_by_id=uid))
    return True


# ── ARTICLES ──

STANDING_ARTICLES = {
    "stance-and-posture": {
        "title": "Stance and Posture",
        "category_slug": "standing",
        "summary": "The foundational body positioning for all standing martial arts — how you stand determines everything.",
        "content": """## Overview

Stance is the foundation of all standing combat. How a fighter positions their feet, distributes their weight, and aligns their spine determines their ability to attack, defend, and react to an opponent's movement. Every martial art builds its technical system on top of a specific stance philosophy.

## Core Principles

**Base Width:** Feet roughly shoulder-width apart provides the best balance between stability and mobility. Too narrow and you're easily pushed off balance. Too wide and you can't move quickly.

**Weight Distribution:** Most grappling stances favor a slight forward lean (55-60% on the lead foot) to facilitate level changes and shot entries. Striking stances vary — boxing tends toward 50/50, while Muay Thai loads the rear leg for kicks.

**Spine Alignment:** A straight, stacked spine transmits force efficiently and resists being bent or twisted. Hunching forward exposes the neck and back. Leaning too far back removes your ability to generate forward pressure.

**Head Position:** The head should remain centered over the base. Wherever the head goes, the body follows — this is why snap downs and collar ties are so effective.

## Grappling vs. Striking Stances

In pure grappling, stances tend to be more bent at the waist and knees (lower center of gravity) with hands forward for gripping. In striking, the stance is more upright with hands protecting the head.

MMA forces a compromise: low enough to defend takedowns, upright enough to see and throw strikes. This hybrid stance is one of the sport's defining technical challenges.

## Common Mistakes

- Standing too upright with no knee bend (easy to off-balance)
- Crossing feet while moving (momentary loss of base)
- Reaching with arms while hips stay back (creates easy snap-down openings)
- Staring at the ground instead of opponent's chest/collar line
"""
    },
    "clinch": {
        "title": "Clinch",
        "category_slug": "standing",
        "summary": "Close-range standing position where both fighters grip each other's upper body — the gateway between striking and grappling.",
        "content": """## Overview

The clinch is a standing position where two fighters are in close contact, gripping each other's upper body. It is the bridge between striking range and grappling range — the place where takedowns are initiated, throws are executed, and knees and elbows find their targets.

Every grappling art has its own clinch system. Wrestling uses collar ties, underhooks, and body locks. Judo uses sleeve and lapel grips (kumi kata). Muay Thai uses the plum position for knees and elbows. Understanding clinch control is essential for dictating where a fight takes place.

## Key Positions

**Collar Tie:** One or both hands grip behind the opponent's neck. Controls the head and creates snap-down opportunities. A staple of wrestling and MMA.

**Underhook:** One arm threaded under the opponent's arm, hand on their back. Provides inside position and sets up body lock takedowns, trips, and lateral movement.

**Double Underhooks:** Both arms under the opponent's arms. Very dominant — the holder can lift, drive forward, or circle to the back. Defending double unders is critical.

**Overhook (Whizzer):** Arm wrapped over the opponent's underhook arm, squeezing tight. A defensive counter to the underhook that can be used offensively for throws.

**Body Lock:** Arms locked around the opponent's torso. Sets up suplex-style takedowns, mat returns, and body lock passes.

## Clinch Fighting Concepts

The clinch is a battle for **inside position**. The fighter whose hands and arms are closer to the opponent's centerline has the advantage. Pummeling — the cyclical fight for underhooks — is the core skill of clinch work.

**Head position** matters enormously. Whoever's head is on the inside (forehead against the opponent's chest or neck) has better posture and more control. Head-outside positions are more vulnerable to front headlocks and chokes.
"""
    },
    "wrestling": {
        "title": "Wrestling",
        "category_slug": "standing",
        "summary": "One of the oldest martial arts — the art of controlling and taking down an opponent without strikes or submissions.",
        "content": """## Overview

Wrestling is among the oldest combat sports in human history, with depictions dating back to cave paintings and ancient Egyptian tombs. In its modern competitive forms — freestyle, Greco-Roman, and folkstyle — wrestling focuses on takedowns, control, and pinning an opponent's shoulders to the mat.

In the context of MMA and submission grappling, wrestling is widely considered the most important base a fighter can have. The ability to dictate where a fight takes place — standing or on the ground — is the single most valuable skill in combat sports.

## Styles

**Freestyle Wrestling:** The international Olympic style. Attacks to legs are permitted. Emphasis on explosive takedowns, gut wrenches, and exposure (turning an opponent's back toward the mat). Points awarded for takedowns (2-5 points) and exposure.

**Greco-Roman Wrestling:** Olympic style where all attacks must be above the waist. No leg attacks, no tripping, no hooking legs. Forces upper body throws, body locks, and lifts. Produces athletes with exceptional clinch work and upper body power.

**Folkstyle (Collegiate) Wrestling:** The American scholastic and collegiate style. Unique emphasis on riding time (controlling an opponent on the mat) and escapes/reversals from bottom position. Produces grapplers with outstanding top pressure and mat control.

## Impact on Modern Grappling

Wrestling's influence on no-gi grappling and MMA cannot be overstated. The shot — a penetration step into a leg attack — is the most common takedown entry in both sports. Chain wrestling concepts (linking attacks in sequence) translate directly to submission grappling's emphasis on transitional offense.

Top wrestlers who transition to BJJ or MMA bring: explosive takedowns, relentless top pressure, the ability to stand up from bottom (crucial in MMA), and the mental toughness forged by the sport's famously brutal training culture.
"""
    },
    "judo": {
        "title": "Judo",
        "category_slug": "standing",
        "summary": "The gentle way — a Japanese martial art focused on throws, trips, and takedowns using an opponent's gi for grips.",
        "content": """## Overview

Judo (柔道, "the gentle way") was created by Jigoro Kano in 1882 as a synthesis of traditional Japanese jujutsu schools. It became an Olympic sport in 1964 and remains one of the most widely practiced martial arts in the world. Judo's technical focus is on nage-waza (throwing techniques) — using grips on the opponent's gi to off-balance and throw them.

## Technical Framework

Judo's throwing system is built on the concept of **kuzushi** (off-balancing). Before any throw can succeed, the opponent must be broken from their natural posture. Kuzushi is created through grip fighting (kumi kata), movement, and timing.

The three phases of a judo throw:
1. **Kuzushi** — break the opponent's balance
2. **Tsukuri** — enter and fit into the throwing position
3. **Kake** — execute the throw

## Major Throw Categories

**Te-waza (Hand techniques):** Seoi nage, tai otoshi, kata guruma
**Koshi-waza (Hip techniques):** O goshi, harai goshi, uchi mata
**Ashi-waza (Foot/leg techniques):** Osoto gari, ouchi gari, kouchi gari, de ashi barai
**Sutemi-waza (Sacrifice techniques):** Tomoe nage, sumi gaeshi, tani otoshi

## Judo in Modern Grappling

Judo's contributions to submission grappling include: devastating standing throws, the pin system (osaekomi-waza) which translates directly to top position control, and a submission arsenal (shimewaza/chokes, kansetsuwaza/joint locks) that remains effective at the highest levels. Many BJJ athletes study judo to improve their standing game, and several elite grapplers (including Travis Stevens and Kayla Harrison) have crossed over between the sports.
"""
    },
    "muay-thai": {
        "title": "Muay Thai",
        "category_slug": "standing",
        "summary": "The art of eight limbs — Thailand's national combat sport using punches, kicks, elbows, and knees.",
        "content": """## Overview

Muay Thai (มวยไทย, "Thai boxing") is the national sport and cultural martial art of Thailand. Known as "the art of eight limbs," it uses the entire body as a weapon: fists, elbows, knees, and shins. Its clinch system, devastating kicks, and practical effectiveness have made it the striking foundation of modern MMA.

## Technical Elements

**Kicks:** The roundhouse kick — thrown with the shin rather than the foot — is Muay Thai's signature technique. Generated by hip rotation and a step-through motion, Thai kicks carry enormous force. Low kicks target the opponent's lead leg. Body kicks attack the ribs. Head kicks aim for the knockout.

**Elbows:** Close-range cutting weapons. Thrown horizontally, vertically, diagonally, and as spinning attacks. Responsible for many of the sport's dramatic cuts and knockouts.

**Knees:** Devastating in the clinch. The straight knee (khao trong) driven into the body or head is one of combat sports' most powerful techniques. Knees are also used defensively to block body kicks.

**The Clinch (Plum):** Muay Thai's clinch system — the plum position (double collar tie with hands clasped behind the opponent's head) — is a distinct fighting range. From the plum, fighters throw knees to the body and head, sweep the opponent off their feet, and battle for positional dominance.

## Relevance to Grappling

While Muay Thai is primarily a striking art, its clinch system directly intersects with grappling. The Thai clinch teaches head control, off-balancing, and close-range fighting that translates to wrestling and judo. Many MMA fighters blend Muay Thai clinch work with wrestling to control distance and dictate exchanges.
"""
    },
    "boxing": {
        "title": "Boxing",
        "category_slug": "standing",
        "summary": "The sweet science — the art and sport of fighting with the fists, emphasizing footwork, head movement, and punching technique.",
        "content": """## Overview

Boxing is one of the oldest and most refined combat sports, with a competitive history stretching back to ancient Greece. Modern boxing focuses exclusively on punches — jabs, crosses, hooks, and uppercuts — delivered while standing. Its sophistication lies in the defensive arts: footwork, head movement, distance management, and ring generalship.

## Core Concepts

**Jab:** The lead hand punch. The most important weapon in boxing — it measures distance, disrupts the opponent's rhythm, sets up power shots, and scores points. A good jab is the foundation of everything.

**Footwork:** Boxing footwork is about angles. Pivoting off the lead foot to create new attacking angles. Cutting off the ring to corner an opponent. Circling away from the opponent's power hand. The feet do more work than the hands.

**Head Movement:** Slipping (moving the head offline to avoid a punch), rolling (dipping under hooks), and pulling (leaning back from straight punches). Good head movement makes a boxer hard to hit without retreating.

**Distance Management:** The ability to control the range of engagement. Fighting at the end of your jab range keeps you safe. Closing distance to land hooks and uppercuts requires setups. This concept translates directly to grappling's distance management principles.

## Boxing in MMA and Grappling

Boxing's influence on MMA is enormous: the jab, the cross, head movement, and footwork form the striking base for most fighters. For grapplers, understanding boxing distance helps with closing the gap for takedowns and avoiding strikes in MMA contexts. The concept of "angles" — never being directly in front of an opponent — applies equally to grappling.
"""
    },
    "grip-fighting": {
        "title": "Grip Fighting",
        "category_slug": "standing",
        "summary": "The battle for hand position that precedes every technique — whoever wins the grip fight controls the exchange.",
        "content": """## Overview

Grip fighting is the micro-battle that determines the outcome of every standing exchange in grappling. Before any throw, takedown, or pull can happen, each fighter must establish advantageous grips while denying the opponent theirs. It is the chess game within the chess game — subtle, exhausting, and decisive.

In gi grappling, grip fighting means controlling the sleeves, lapels, and collar of the opponent's jacket. In no-gi, it means fighting for collar ties, wrist control, underhooks, and overhooks. In both contexts, grip fighting is the gateway to offense.

## Key Principles

**First Grip Advantage:** The fighter who establishes the first dominant grip forces the other to react. This initiative compounds — once you're fighting to remove grips, you're not attacking.

**Two-on-One (Russian Tie):** Controlling one of the opponent's arms with both of yours. Creates a massive asymmetry — you have two free attacking lanes while they have one.

**Grip Breaking:** Stripping grips is as important as setting them. Common methods: circle-breaking (rotating the gripped limb), slapping off, posting on the bicep, and using two hands to strip one grip.

**Inside Position:** Arms and grips closer to the opponent's centerline beat outside grips. Underhooks beat overhooks because they occupy inside space.

## Gi vs. No-Gi Grip Fighting

Gi grips are more persistent — a strong lapel grip can last an entire exchange. This makes gi grip fighting a slower, more methodical battle. No-gi grips are more transient — wrists slip, necks are sweaty, and hooks can be pumped. No-gi grip fighting is faster and more dynamic, with a premium on timing over strength.
"""
    },
}

ADDITIONAL_TAKEDOWNS = {
    "uchi-mata": {
        "title": "Uchi Mata",
        "category_slug": "takedown",
        "summary": "Judo's most successful competition throw — an inner thigh reaping technique that scores more ippon than any other throw.",
        "content": """## Overview

Uchi mata (内股, "inner thigh throw") is statistically the most successful throw in judo competition history, producing more ippon (full scores) than any other technique. It is classified as an ashi-waza (foot/leg technique) and attacks by reaping the opponent's inner thigh with the back of your leg while pulling them forward over your hip.

## Execution

The throw begins with a strong pull on the opponent's lapel and sleeve, drawing them forward onto their toes (kuzushi). The thrower steps across, plants their support foot between the opponent's feet, and sweeps their reaping leg backward into the opponent's inner thigh. The throwing action combines a forward pull of the hands with an upward-backward sweep of the leg.

## Variations

**Ashi Uchi Mata:** The leg sweeps the opponent's leg directly — a more leg-focused variation.
**Koshi Uchi Mata:** The hip drives into the opponent first, making it more of a hip throw with a leg sweep finish.
**Ken Ken Uchi Mata:** The thrower hops on their support foot to chase a retreating opponent before executing the throw.

## In Grappling

Uchi mata translates well to no-gi via an overhook or whizzer entry. It's also commonly used as a counter to single leg takedowns — when an opponent shoots, the defender sprawls and whizzers, then converts to an uchi mata. This application makes it one of the most relevant judo throws for MMA.
"""
    },
    "fireman-carry": {
        "title": "Fireman's Carry",
        "category_slug": "takedown",
        "summary": "A wrestling takedown where you duck under the opponent's arm and load them across your shoulders before dumping them to the mat.",
        "content": """## Overview

The fireman's carry (kata guruma in judo) is a spectacular takedown where the attacker ducks under the opponent's arm, loads them across their shoulders, and throws them to the mat. It is a high-amplitude technique with deep roots in both wrestling and judo.

## Mechanics

From a collar tie or an underhook, the attacker drops to one or both knees, threading their head under the opponent's arm. The attacking arm reaches between the opponent's legs to grip the far thigh. From this loaded position, the attacker elevates and rotates, dumping the opponent over their shoulders and landing in a dominant position.

## Entry Points

**From a collar tie:** Snap the opponent's head down to create the arm opening, then shoot under.
**From an arm drag:** Drag the arm across, creating space to duck under on the same side.
**From a single leg defense:** When an opponent defends a single leg by pushing your head down, you can transition to a fireman's carry.

## Modern Usage

In freestyle wrestling, the fireman's carry remains a high-percentage technique, especially at lighter weight classes where the speed and flexibility requirements are easier to meet. In MMA, it appears less frequently due to the risk of giving up the back during the entry, but when it lands, it's spectacular.
"""
    },
    "high-crotch": {
        "title": "High Crotch",
        "category_slug": "takedown",
        "summary": "A leg attack where you drive into the opponent's hip crease, controlling one leg high at the inner thigh.",
        "content": """## Overview

The high crotch is a wrestling takedown where the attacker drives into the opponent's hip crease and controls one leg high at the inner thigh. It is one of the three fundamental shot-based attacks in wrestling (along with the double leg and single leg) and serves as both a primary takedown and a chain wrestling hub.

## Mechanics

The attacker shoots a penetration step toward the opponent's lead leg, driving their shoulder into the hip. The near arm wraps around the inner thigh at the hip crease (the "crotch"). The head stays tight to the outside of the opponent's hip.

## Finishes

**Lift and Turn:** Elevate the leg and circle toward the trapped side, forcing the opponent down.
**Run the Pipe:** Drive forward while pulling the trapped leg backward and across their body.
**Trip Finish:** Step behind the opponent's far leg while controlling the high crotch.
**Transition to Double:** If the opponent defends by hopping, scoop the far leg to convert to a double.

## Chain Wrestling Applications

The high crotch is perhaps the best chain wrestling position in grappling. It connects naturally to the single leg (drop the grip lower), the double leg (scoop the far leg), the mat return (from behind), and back takes. Elite wrestlers flow between these attacks seamlessly, making the high crotch a central node in their takedown network.
"""
    },
}

ADDITIONAL_GUARDS = {
    "turtle": {
        "title": "Turtle",
        "category_slug": "guard",
        "summary": "A defensive position on all fours with knees and elbows tight — a common recovery position that is also vulnerable to back takes.",
        "content": """## Overview

Turtle position is when a grappler is on their hands and knees (or knees and elbows) with their back exposed upward. It is primarily a defensive recovery position — athletes go to turtle to avoid having their guard passed or to stall a bad position. However, turtle is also a launching point for attacks in modern grappling systems.

## Defensive Turtle

The key defensive priorities in turtle are: keep the elbows tight to the knees (deny seat belt and hooks), tuck the chin (prevent chokes), and be ready to sit to guard or stand up. The bottom player wants to minimize the time spent in turtle because the back is exposed.

## Offensive Turtle

Modern grappling has developed aggressive turtle games. Eduardo Telles pioneered an entire system of sweeps and attacks from turtle, and wrestlers naturally work from this position to stand up or hit switch-style reversals.

**Common Attacks From Turtle:**
- Sit-out: spin through to face the opponent
- Granby roll: invert to recover guard
- Peterson roll: reach back and roll the top player over
- Stand up: post and drive to feet

## Attacks Against Turtle

The top player's primary goal is to take the back. Methods include: inserting hooks one at a time, using a seat belt grip to roll the turtle player to their side, and clock choke or crucifix attacks that punish a tight turtle shell.
"""
    },
    "north-south-position": {
        "title": "North-South Position",
        "category_slug": "dominant-position",
        "summary": "A chest-to-chest pin where the top player faces the opposite direction from the bottom player, head to head.",
        "content": """## Overview

North-South (also called 69 position in some traditions) is a chest-to-chest pin where the top player lies perpendicular to the bottom player's body, facing the opposite direction. The top player's chest covers the bottom player's face/chest, and their hips are near the bottom player's head.

## Control Mechanics

North-South is one of the heaviest pins in grappling. The top player distributes their weight across the bottom player's chest and face, making it extremely difficult to breathe and move. Control comes from: sprawling the hips low, keeping the chest heavy, and controlling the arms with crossface or arm wraps.

## Attacks

**North-South Choke:** The signature submission — a modified guillotine where the top player wraps the near arm around the bottom player's neck while sprawling weight. A blood choke that can be very tight.

**Kimura:** The bottom player's arms are accessible for kimura attacks from the top.

**Transition to Mount:** Walk the hips around to mount position.

**Transition to Side Control:** Slide back to standard side control for a more stable pin.

## Escapes

Escaping north-south requires creating space before the top player settles their weight. Bridge and turn to the side, frame on the hips, and shrimp to recover a guard position. Timing is critical — once the weight is settled, escape becomes extremely difficult.
"""
    },
}

ADDITIONAL_DOMINANT = {
    "front-headlock": {
        "title": "Front Headlock",
        "category_slug": "dominant-position",
        "summary": "A dominant control position where the top player controls the opponent's head and near arm from above — the gateway to guillotines, darces, and anacondas.",
        "content": """## Overview

The front headlock is a dominant control position where one fighter controls the opponent's head and near arm from above, typically after a sprawl, snap down, or failed takedown attempt. It is one of the most dangerous positions in grappling — the gateway to an entire family of chokes including the guillotine, darce, anaconda, and various neckties.

In the positional hierarchy, front headlock sits at the same level as side control and mount — it is a position of dominant control where the top player has significant submission and transition options while the bottom player is fighting to survive.

## How You Get There

**From a Sprawl:** The most common entry. When an opponent shoots a takedown, the defender sprawls their hips back and down onto the attacker's head, naturally arriving in front headlock.

**From a Snap Down:** In the clinch, snapping the opponent's head down using collar tie control drives them face-first toward the mat. The attacker follows them down into front headlock.

**From Guard Passing:** When passing guard, if the guard player turtles, the passer can circle to the head and establish front headlock control.

## Key Control Elements

**Crossface Grip:** One arm wraps around the opponent's neck, with the forearm across their face or under their jaw. This controls their head and prevents them from turning in.

**Far Arm Control:** The other hand controls the opponent's far arm — either gripping the tricep, underhooking the arm, or reaching across to the far wrist. Controlling this arm prevents the opponent from posting and creates submission entries.

**Hip Pressure:** Sprawling weight down onto the opponent's upper back and head creates enormous pressure and limits their ability to stand up or shoot through.

## Submission Threats

The front headlock is a submission hub:

**Guillotine Choke:** The classic — wrap the arm around the neck, lock hands, squeeze and arch. Available in arm-in and no-arm variations.

**D'Arce Choke:** Thread the arm under the opponent's neck and through to the far armpit. A blood choke that works when the opponent tries to turn in.

**Anaconda Choke:** Similar to the darce but threaded in the opposite direction — around the neck and arm, finished by rolling.

**Peruvian Necktie:** A devastating choke using the legs to create leverage on the head while controlling the arm.

**Japanese Necktie:** A variation of the darce finished by sprawling rather than rolling.

## Escapes

The bottom player's priorities are: get the head free (pop the head out by driving forward), clear the crossface, and either stand up or sit to guard. The longer you stay in front headlock, the more dangerous it becomes — escape early or concede the submission.

## Strategic Importance

Front headlock has become one of the most developed positional systems in modern grappling. John Danaher's front headlock system, made famous by his Death Squad athletes, treats the position as a complete offensive platform with branching decision trees based on the opponent's defensive reactions. In MMA, the front headlock is equally important — many fights end with guillotines after sprawled takedown attempts.
"""
    },
}


    "distance-management": {
        "title": "Distance Management",
        "category_slug": "principle",
        "summary": "The fundamental concept of controlling the space between you and your opponent — the meta-game of all combat sports.",
        "content": """## Overview

Distance management is the art of controlling the space between you and your opponent. It is arguably the most fundamental concept in all combat sports — everything that happens in a fight occurs at a specific distance, and the fighter who controls that distance controls the fight.

## The Distance Spectrum

In grappling, positions map to a distance spectrum:

**Far Distance (Standing):** Both fighters on their feet, out of contact range. This is where grip fighting and footwork determine first contact.

**Medium Distance (Open Guard):** One fighter is on the ground with feet and hands between them and the standing/kneeling opponent. Spider guard, de la riva, and lasso operate here.

**Close Distance (Closed Guard / Half Guard):** Bodies are in contact, legs are entangled. The guard player uses legs and grips to control posture and distance. The top player works to create space to pass.

**Zero Distance (Pins):** Chest-to-chest contact in side control, mount, or back control. The top player wants zero space. The bottom player needs to create space to escape.

## Why Distance Matters

Every technique has an optimal distance. An armbar needs close distance. A triangle needs the opponent to be partially in the guard. A berimbolo needs de la riva distance. Passing guard means compressing distance from open to closed to zero.

The fighter who forces the exchange to happen at their preferred distance holds the strategic advantage. Passers want to close distance. Guard players often want to maintain medium distance where their legs are most effective.
"""
    },
    "pressure": {
        "title": "Pressure",
        "category_slug": "principle",
        "summary": "Using body weight, angle, and connection to make an opponent uncomfortable and limit their options — the invisible force of top position.",
        "content": """## Overview

Pressure in grappling refers to using your body weight, positioning, and connection to make life miserable for the person underneath you. Good pressure doesn't require strength — it requires understanding how to concentrate your weight through small contact points and remove the opponent's space and comfort.

## Principles of Pressure

**Weight Distribution:** Effective pressure isn't about being heavy — it's about concentrating weight. A 150-pound grappler who places all their weight on the opponent's sternum through their shoulder feels heavier than a 200-pound person lying flat. The key is distributing weight through a single point of contact.

**Removing Posts:** An opponent can only resist pressure if they have posts (frames, arms, legs on the ground). Systematically removing their ability to post — through grip control, hip switches, and positional changes — makes your weight inescapable.

**Driving Through:** Pressure should flow through the opponent into the mat, not just sit on top of them. Effective pressure passers don't just lie on someone — they drive forward and down, pinning the opponent against the floor.

## Pressure in Different Contexts

**Passing:** Pressure passing (smash pass, over-under, body lock) works by closing distance and eliminating space. The passer uses weight and forward drive to flatten the guard player.

**Side Control:** The crossface — driving the forearm into the opponent's jaw to turn their head away — is pressure passing's endgame. Combined with hip-to-hip connection, it creates a pin that is exhausting to escape.

**Mount:** Pressure from mount comes from riding the opponent's movements, staying heavy on their hips, and climbing higher as they expend energy.
"""
    },
}


def run():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("[error] Admin user not found")
            return
        uid = admin.id

        # Ensure Standing category exists
        standing = Category.query.filter_by(slug='standing').first()
        if not standing:
            standing = Category(name='Standing', slug='standing',
                                description='The standing phase of combat.',
                                created_by_id=uid)
            db.session.add(standing)
            db.session.flush()
            print("  [created] Standing category")

        print("\n── Standing Articles ──")
        for slug, data in STANDING_ARTICLES.items():
            seed_article(data['title'], slug, data['content'],
                        data['summary'], data['category_slug'], uid)

        print("\n── Additional Takedowns ──")
        for slug, data in ADDITIONAL_TAKEDOWNS.items():
            seed_article(data['title'], slug, data['content'],
                        data['summary'], data['category_slug'], uid)

        print("\n── Additional Guards/Positions ──")
        for slug, data in ADDITIONAL_GUARDS.items():
            seed_article(data['title'], slug, data['content'],
                        data['summary'], data['category_slug'], uid)

        print("\n── Additional Dominant Positions ──")
        for slug, data in ADDITIONAL_DOMINANT.items():
            seed_article(data['title'], slug, data['content'],
                        data['summary'], data['category_slug'], uid)

        print("\n── Concepts ──")
        for slug, data in CONCEPTS.items():
            seed_article(data['title'], slug, data['content'],
                        data['summary'], data['category_slug'], uid)

        # ── Relationships ──
        print("\n── Relationships ──")
        rels = [
            # Standing articles
            ('stance-and-posture', 'clinch', 'related_to'),
            ('stance-and-posture', 'grip-fighting', 'related_to'),
            ('clinch', 'double-leg-takedown', 'sets_up'),
            ('clinch', 'single-leg-takedown', 'sets_up'),
            ('clinch', 'osoto-gari', 'sets_up'),
            ('clinch', 'seoi-nage', 'sets_up'),
            ('grip-fighting', 'arm-drag', 'sets_up'),
            ('grip-fighting', 'snap-down', 'sets_up'),
            ('grip-fighting', 'clinch', 'sets_up'),
            ('wrestling', 'double-leg-takedown', 'part_of_system'),
            ('wrestling', 'single-leg-takedown', 'part_of_system'),
            ('wrestling', 'high-crotch', 'part_of_system'),
            ('wrestling', 'ankle-pick', 'part_of_system'),
            ('wrestling', 'snap-down', 'part_of_system'),
            ('judo', 'osoto-gari', 'part_of_system'),
            ('judo', 'seoi-nage', 'part_of_system'),
            ('judo', 'uchi-mata', 'part_of_system'),
            ('judo', 'kuzushi', 'part_of_system'),
            ('muay-thai', 'clinch', 'part_of_system'),
            ('boxing', 'stance-and-posture', 'part_of_system'),
            # New takedowns
            ('uchi-mata', 'osoto-gari', 'related_to'),
            ('uchi-mata', 'seoi-nage', 'related_to'),
            ('high-crotch', 'double-leg-takedown', 'related_to'),
            ('high-crotch', 'single-leg-takedown', 'related_to'),
            ('fireman-carry', 'arm-drag', 'sets_up'),
            # Front headlock connections
            ('front-headlock', 'guillotine-choke', 'submits_from'),
            ('front-headlock', 'darce-choke', 'submits_from'),
            ('front-headlock', 'anaconda-choke', 'submits_from'),
            ('front-headlock', 'snap-down', 'related_to'),
            ('front-headlock', 'side-control', 'transitions_to'),
            ('front-headlock', 'back-control', 'transitions_to'),
            ('snap-down', 'front-headlock', 'sets_up'),
            # Turtle connections
            ('turtle', 'back-control', 'transitions_to'),
            ('turtle', 'front-headlock', 'transitions_to'),
            ('turtle', 'guard-retention', 'related_to'),
            # Concepts
            ('distance-management', 'guard-retention', 'related_to'),
            ('distance-management', 'grip-fighting', 'related_to'),
            ('pressure', 'side-control', 'related_to'),
            ('pressure', 'mount', 'related_to'),
            ('pressure', 'knee-slice-pass', 'related_to'),
        ]
        count = 0
        for src, tgt, rtype in rels:
            if add_rel(src, tgt, rtype, uid):
                count += 1
        print(f"  Added {count} new relationships")

        db.session.commit()
        total = Article.query.filter_by(is_published=True).count()
        total_rels = ArticleRelationship.query.count()
        print(f"\n✓ Done. Total: {total} articles, {total_rels} relationships")


if __name__ == '__main__':
    run()

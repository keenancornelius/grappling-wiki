"""
Seed script #2: add more articles to flesh out every category.
Run from project root: python scripts/seed_articles_2.py
(Run seed_articles.py first if you haven't already.)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Article, ArticleRevision, Tag

ARTICLES = [
    # ── TECHNIQUES ──────────────────────────────────────────────────
    {
        "title": "Triangle Choke",
        "slug": "triangle-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A blood choke using the legs to form a triangle around the opponent's head and one arm.",
        "content": """## Overview

The triangle choke (sankaku jime) is a submission that uses the legs to encircle the opponent's neck and one arm, creating a figure-four configuration that compresses the carotid arteries. It is one of the most versatile submissions in grappling, applicable from guard, mount, and even from the back.

## Mechanics

The attacker traps the opponent's head and one arm between their legs, locking one leg behind the opposite knee. By squeezing the knees together and pulling the opponent's head down, the attacker's thigh presses against one carotid artery while the opponent's own trapped shoulder compresses the other.

The angle is critical — the attacker must cut a perpendicular angle to the opponent's body. Without the angle, the choke becomes a squeeze rather than a blood restriction.

## Key Setups

**From closed guard:** The most classic entry. The attacker controls one wrist, opens the guard, and swings one leg over the opponent's neck while keeping the arm trapped inside.

**From mount:** The attacker isolates an arm, feeds it across, and slides into a mounted triangle. Often set up when the bottom player extends an arm to push.

**From overhook guard:** The attacker uses an overhook to control posture and create the angle needed to swing the leg over.

## Common Defenses

Posturing up before the triangle is locked, stacking the attacker to relieve pressure, and working to free the trapped arm. Once fully locked with the correct angle, the triangle is extremely difficult to escape.

## Related

See also: Armbar, Omoplata, Closed Guard, Mounted Triangle"""
    },
    {
        "title": "Guillotine",
        "slug": "guillotine",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A front headlock choke that attacks the neck using the forearm and clasped hands.",
        "content": """## Overview

The guillotine choke is a front headlock submission that can function as both an air choke and a blood choke depending on the variation. It is one of the most common submissions in MMA and no-gi grappling, prized for its speed of application and availability from standing, in the clinch, and on the ground.

## Variations

**Arm-in guillotine:** The opponent's arm is trapped inside the choke alongside their neck. This version applies more of a blood choke by compressing the carotid with the forearm while the trapped shoulder closes the other side.

**High-elbow guillotine (Marcelotine):** Popularized by Marcelo Garcia, this variation uses an elevated choking elbow and wrist-to-wrist grip to maximize pressure on the neck. Considered the highest-percentage guillotine variation.

**Standing guillotine:** Applied from the clinch or in reaction to a shot. Can be finished standing or by pulling guard.

## Mechanics

The attacker wraps one arm around the opponent's neck from the front, clasps both hands together, and drives the blade of the forearm into the throat or the side of the neck. The finishing mechanics involve pulling the hands upward toward the ceiling while arching the back.

Guard position — particularly closed guard or half guard — provides the best platform for finishing because the attacker can use their legs to prevent the opponent from circling away.

## Related

See also: Marcelo Garcia, D'Arce Choke, Anaconda Choke, Front Headlock"""
    },
    {
        "title": "Kimura",
        "slug": "kimura",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A double-wristlock shoulder lock that rotates the arm behind the opponent's back.",
        "content": """## Overview

The kimura (also called double wristlock or gyaku ude-garami) is a shoulder lock submission that isolates the opponent's arm and rotates it behind their back, attacking the shoulder joint. Named after judoka Masahiko Kimura, who used it to defeat Helio Gracie in 1951, it remains one of the most fundamental and frequently used submissions in all grappling disciplines.

## Mechanics

The attacker controls the opponent's wrist with one hand and feeds the other arm under the opponent's elbow, gripping their own wrist to form a figure-four lock. By pinning the opponent's elbow to their body and rotating the wrist away from the opponent's back, the attacker creates a rotational force on the shoulder that exceeds the joint's range of motion.

## Positions

The kimura is available from almost everywhere: closed guard (bottom), side control (top), north-south, half guard, and even standing. This ubiquity makes it one of the most important grips to understand in grappling — even when the submission itself isn't available, the kimura grip provides powerful control for sweeps, transitions, and back takes.

## The Kimura Trap System

Modern grapplers have developed entire systems around the kimura grip as a control position rather than just a submission. The kimura trap allows the attacker to chain together sweeps, back takes, and submissions while maintaining constant control of the opponent's arm.

## Related

See also: Americana, Armbar, Side Control, Closed Guard"""
    },
    {
        "title": "Omoplata",
        "slug": "omoplata",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A shoulder lock applied using the legs, rotating the opponent's arm behind their back.",
        "content": """## Overview

The omoplata (ashi sankaku garami) is a shoulder lock submission where the attacker uses their legs to isolate and rotate the opponent's arm behind their back, attacking the shoulder joint. Originally from judo but developed extensively in BJJ, the omoplata serves as both a submission and a powerful sweeping and control position.

## Mechanics

From guard, the attacker swings one leg over the opponent's shoulder while controlling the wrist, then sits up perpendicular to the opponent. By leaning forward over the opponent's back and driving the hips down, the attacker rotates the trapped shoulder beyond its natural range of motion.

## The Omoplata Position

Beyond the submission itself, the omoplata position is a versatile control point. When the opponent defends the submission by rolling, the attacker can follow to sweep. When the opponent postures, the attacker can transition to triangles or armbars. This makes the omoplata a critical junction in the guard game.

## Related

See also: Triangle Choke, Armbar, Closed Guard, Sweeps"""
    },
    {
        "title": "D'Arce Choke",
        "slug": "darce-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An arm triangle variation threaded from the opposite side, attacking the neck in a head-and-arm configuration.",
        "content": """## Overview

The D'Arce choke (also spelled Darce, technically called the no-gi brabo choke) is a head-and-arm choke applied by threading one arm under the opponent's neck and through to their armpit, then locking a figure-four grip. It attacks the neck in a similar manner to the anaconda choke but enters from the opposite side.

Named after Joe D'Arce, a black belt who popularized the technique in competition, it has become one of the most common submissions from top position in no-gi grappling.

## Mechanics

The attacker threads their choking arm under the opponent's neck, past the far armpit, and locks a rear naked choke-style grip (bicep-to-hand). The finish involves sprawling the hips back and squeezing — the opponent's own trapped arm and the attacker's forearm compress both carotid arteries.

## Common Entries

The D'Arce is most commonly entered from half guard top (when the bottom player goes for an underhook), from side control when the opponent turns in, or during scrambles when the opponent turtles. Recognizing the head-and-arm configuration during transitions is key.

## Related

See also: Anaconda Choke, Arm Triangle, Guillotine, Half Guard"""
    },
    {
        "title": "Heel Hook",
        "slug": "heel-hook",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A devastating leg lock that attacks the knee by twisting the heel and lower leg.",
        "content": """## Overview

The heel hook is a leg lock submission that attacks the knee joint by controlling the opponent's heel and rotating the lower leg while immobilizing the upper leg. It is widely considered the most dangerous submission in grappling due to the speed at which it can cause ligament damage and the difficulty of feeling the submission before injury occurs.

## Mechanics

The attacker controls the opponent's leg — typically from an ashi garami (leg entanglement) position — and cups the heel. By rotating the heel while preventing the opponent's hip from turning, torsional force is applied to the knee, attacking the ACL, MCL, and meniscus.

**Inside heel hook:** The attacker rotates the heel inward (toward the centerline of the opponent's body). Considered more dangerous because it attacks more ligaments simultaneously.

**Outside heel hook:** The attacker rotates the heel outward. Somewhat less dangerous but still highly effective.

## The Leg Lock Revolution

Heel hooks were historically banned or discouraged in many BJJ competitions and academies. The modern leg lock revolution, driven primarily by John Danaher and his students (including Gordon Ryan, Garry Tonon, and Nicky Ryan), transformed heel hooks from a niche technique into a central part of competitive no-gi grappling.

## Safety

Because knee ligament damage can occur suddenly and without the gradual pain warning that accompanies most joint locks, training heel hooks requires extra caution. Practitioners must tap early and release immediately. Many academies restrict heel hooks to advanced students.

## Related

See also: Ashi Garami, Kneebar, Toe Hold, Straight Ankle Lock, Inside Sankaku"""
    },
    {
        "title": "Scissor Sweep",
        "slug": "scissor-sweep",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A fundamental closed guard sweep using a scissoring leg motion to off-balance and reverse the opponent.",
        "content": """## Overview

The scissor sweep is one of the first sweeps taught in Brazilian Jiu-Jitsu and remains effective at all levels. From closed guard, the attacker uses a cross-collar or sleeve grip to control the opponent's posture, places one shin across the opponent's midsection as a frame, and chops the other leg at the knee line — the scissoring motion topples the opponent sideways, landing the attacker in mount.

## Mechanics

The sweep works by removing the opponent's base on one side (chopping the knee) while driving them in that direction (pushing with the shin frame and pulling with the upper body grips). The combined forces create a rotation that the top player cannot post against because their arm is controlled.

## Key Details

Grip control is everything. Without controlling the opponent's arm on the side they would post to catch themselves, the sweep fails. The most common grips are cross-collar and same-side sleeve (gi), or collar tie and wrist control (no-gi).

Timing matters — the sweep is most effective when the opponent is leaning slightly forward, loading weight onto the attacker's shin frame. Attempting it when the opponent is sitting back on their heels is much harder.

## Related

See also: Closed Guard, Hip Bump Sweep, Flower Sweep, Mount"""
    },
    {
        "title": "Double Leg Takedown",
        "slug": "double-leg-takedown",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "The most fundamental wrestling takedown — shooting in to grab both legs and drive the opponent to the mat.",
        "content": """## Overview

The double leg takedown is the most widely used takedown in wrestling and one of the most effective techniques for initiating ground fighting in any grappling discipline. The attacker shoots forward, changes levels, and wraps both arms around the opponent's legs before driving them to the mat.

## Mechanics

The takedown begins with a level change — the attacker drops their hips and drives forward, placing their head to one side of the opponent's body. Both arms encircle the opponent's legs at or above the knees. The finish involves driving forward with the legs while lifting or turning the opponent to complete the takedown.

## Variations

**Blast double:** Maximum forward drive, running through the opponent. Effective against the fence in MMA.

**Lift double:** The attacker lifts the opponent's legs off the mat before turning the corner to finish.

**Snatch double:** A quick grab-and-go variation used when the opponent's stance is wide.

## Defenses

The sprawl is the primary defense — driving the hips back and down onto the attacker's head and shoulders. Other defenses include the whizzer (overhook), crossface, and front headlock.

## Related

See also: Single Leg Takedown, Wrestling, Guard Pull, Sprawl"""
    },
    # ── POSITIONS ───────────────────────────────────────────────────
    {
        "title": "Side Control",
        "slug": "side-control",
        "category": "position",
        "tags": ["Position"],
        "summary": "A dominant top position where the passer has cleared the guard and controls the opponent from the side.",
        "content": """## Overview

Side control (also called side mount or cross-side) is a dominant top position achieved after passing the opponent's guard. The top player lies perpendicular to the bottom player, chest-to-chest, with their weight distributed to pin the bottom player to the mat. In IBJJF scoring, passing to side control awards 3 points.

## Variations

**Standard side control:** Chest-to-chest, near arm controlling the opponent's hip, far arm controlling the head or underhooking the far arm.

**Kesa gatame (scarf hold):** The top player sits their hip next to the opponent, wraps the head, and controls the near arm. A traditional judo pin that offers powerful control and submission options.

**Reverse kesa gatame:** Similar to kesa but facing the opponent's legs. Opens up different submission angles including north-south choke transitions.

**Twister side control:** The top player faces the opponent's legs, often as a transition to leg attacks or back takes.

## Attacks

Side control offers submissions including Americana, kimura, arm triangle, north-south choke, and various gi chokes. It also serves as a transition point to mount, knee on belly, and north-south.

## Escaping

The fundamental escapes are the elbow-knee escape (shrimping to reguard), the bridge and roll, and the ghost escape (going to turtle). Effective framing against the opponent's neck and hip is critical for creating the space needed to escape.

## Related

See also: Mount, Guard Passing, Americana, Knee on Belly, Frames and Framing"""
    },
    {
        "title": "Back Control",
        "slug": "back-control",
        "category": "position",
        "tags": ["Position"],
        "summary": "The single most dominant position in grappling — behind the opponent with hooks or a body triangle.",
        "content": """## Overview

Back control (back mount) is universally considered the most dominant position in grappling. The attacker is behind the opponent, typically with their chest against the opponent's back, controlling with leg hooks or a body triangle. The position awards 4 points in IBJJF competition.

The dominance of back control stems from asymmetry — the attacker has full access to the opponent's neck and arms, while the opponent cannot easily attack or even see what's coming.

## Control Methods

**Hooks:** Both feet are hooked inside the opponent's thighs, preventing them from turning or sliding down. The seatbelt grip (one arm over the shoulder, one under the armpit) controls the upper body.

**Body triangle:** One leg wraps around the opponent's waist and locks in a figure-four with the other leg. Provides extremely tight control that is harder to escape than hooks but offers slightly less mobility for the attacker.

## Attacks

The rear naked choke is the primary attack. Other options include the bow and arrow choke (gi), armbar from the back, collar chokes, and short chokes. The constant threat of the RNC forces defensive reactions that open up other attacks.

## Escapes

Escaping the back requires addressing both the hooks/body triangle and the seatbelt grip. The primary escapes involve sliding down to escape the hooks, fighting the choking hand, and turning into the attacker to reach a guard position.

## Related

See also: Rear Naked Choke, Body Triangle, Seatbelt Grip, Mount"""
    },
    {
        "title": "Butterfly Guard",
        "slug": "butterfly-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "An open guard played seated with both feet hooked inside the opponent's thighs.",
        "content": """## Overview

Butterfly guard is an open guard position where the bottom player sits upright with both feet hooked inside the opponent's thighs. It is one of the most dynamic and offense-oriented guards in grappling, offering powerful sweeps, back takes, and submission entries.

Butterfly guard was elevated to elite status primarily through Marcelo Garcia's competitive career, where it became the launching pad for his devastating arm drags and sweeps.

## Mechanics

The guard works on the principle of using the hooks (feet inside the thighs) as elevating levers. Combined with upper body grips (underhooks, collar ties, or arm drags), the bottom player can off-balance and elevate the top player, creating sweep opportunities.

The seated posture is critical — if the butterfly guard player is flattened onto their back, the position loses much of its offensive potential. Maintaining an upright, engaged posture with active hooks is the foundation.

## Key Attacks

**Butterfly sweep:** Using an underhook and the corresponding hook, the attacker loads the opponent's weight onto them, then elevates with the hook while falling to the side. One of the highest-percentage sweeps in competition.

**Arm drag to back take:** The attacker drags the opponent's arm across their body, clearing a path to circle behind for back control.

**Guillotine and front headlock entries:** When the top player drives forward into the butterfly guard, they expose their neck to guillotine attacks.

## Related

See also: Marcelo Garcia, X-Guard, Arm Drag, Half Butterfly, Sweeps"""
    },
    {
        "title": "De La Riva Guard",
        "slug": "de-la-riva-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "An open guard using an outside leg hook around the opponent's lead leg, named after Ricardo de la Riva.",
        "content": """## Overview

De La Riva guard (DLR) is an open guard position where the bottom player hooks one leg around the outside of the standing opponent's lead leg, wrapping at the knee or thigh. Named after Ricardo de la Riva, the Brazilian black belt who systematized the position in the 1980s, DLR has become one of the most widely played open guards in modern BJJ.

## Mechanics

The defining element is the outside hook — the bottom player's foot wraps behind the opponent's lead knee from the outside, creating a connection point that controls distance and limits the top player's ability to retreat or change angle. The other foot typically pushes on the opponent's hip, bicep, or far knee to manage distance and create off-balancing opportunities.

Grip fighting is essential in DLR. Common grips include the ankle of the hooked leg, the far sleeve or collar, and the belt or back of the pants.

## Attacks

DLR guard offers sweeps (berimbolo, ankle pick, tripod sweep), back takes (berimbolo, kiss of the dragon), and transitions to other guards (X-guard, single leg X, deep De La Riva). It is particularly effective against standing opponents and is a cornerstone of modern sport BJJ guard play.

## Related

See also: Berimbolo, X-Guard, Spider Guard, Open Guard, Ricardo de la Riva"""
    },
    {
        "title": "Turtle Position",
        "slug": "turtle-position",
        "category": "position",
        "tags": ["Position"],
        "summary": "A defensive position on hands and knees, protecting the neck and limbs from attack.",
        "content": """## Overview

The turtle position occurs when a grappler is on their hands and knees, typically with their elbows tucked tight and chin protected. While often considered purely defensive — a position people end up in rather than choose — turtle has evolved into a strategic position with its own offensive options, particularly in wrestling and judo.

## Defensive Turtle

In BJJ, turtle is most commonly reached when a guard pass is nearly completed and the bottom player turns to their knees rather than conceding side control. The defensive priorities are protecting the neck (preventing chokes), keeping the elbows tight (preventing arm attacks), and preventing the opponent from inserting hooks (preventing back takes).

## Offensive Turtle

Modern grappling has developed offensive options from turtle including sit-outs, granby rolls, Peterson rolls, and various leg attack entries. Some competitors deliberately pull into turtle to initiate scrambles or access leg entanglements.

In wrestling and judo, turtle (or par terre) is a well-developed position with systematic attacks and escapes.

## Related

See also: Back Control, Sprawl, Granby Roll, Guard Recovery"""
    },
    {
        "title": "Knee on Belly",
        "slug": "knee-on-belly",
        "category": "position",
        "tags": ["Position"],
        "summary": "A dominant control position with one knee driving into the opponent's torso, worth 2 points in IBJJF.",
        "content": """## Overview

Knee on belly (knee on stomach, knee ride) is a dominant top position where the attacker places one knee on the opponent's torso — usually the solar plexus or lower ribs — while the other foot posts on the mat for base. It awards 2 points in IBJJF competition.

Despite being a transition-heavy position rather than a static pin, knee on belly is extremely effective for maintaining pressure, creating submission openings, and forcing reactions. The concentrated weight through a single knee point is deeply uncomfortable, often forcing panicked responses that create attack opportunities.

## Attacks

The pressure itself forces reactions — when the bottom player pushes against the knee, they expose their arms to armbars and kimuras. When they turn away, they give up their back. Common submissions from knee on belly include cross collar chokes, baseball bat chokes, armbars, and far-side kimuras.

## Related

See also: Side Control, Mount, Guard Passing"""
    },
    # ── CONCEPTS ────────────────────────────────────────────────────
    {
        "title": "Underhooks",
        "slug": "underhooks",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "One of the most important grip concepts in grappling — controlling the inside position with an arm under the opponent's arm.",
        "content": """## Overview

An underhook is achieved when a grappler threads their arm under the opponent's arm, typically at the armpit, and controls the opponent's body from underneath. Underhooks are one of the most fundamental and important concepts in all grappling — from wrestling to BJJ to judo, winning the underhook battle frequently determines who controls the position.

## Why Underhooks Matter

The underhook provides inside position — the arm is closer to the opponent's center of mass, offering superior leverage for controlling posture, initiating takedowns, and preventing the opponent from establishing their own offense.

In wrestling, the underhook is the basis of most tie-ups, throws, and takedown entries. In BJJ, the underhook battle in half guard is often the defining strategic contest — if the bottom player wins the underhook, they can sweep or take the back; if the top player wins it, they can flatten and pass.

## Applications

**Standing:** Underhooks enable single legs, body locks, hip throws, and snap-downs. A double underhook gives the wrestler a body lock with dominant inside position.

**Half guard bottom:** The underhook allows the bottom player to come up to their knees, threatening sweeps and back takes.

**Half guard top:** The crossface combined with an underhook (or whizzer to prevent the bottom player's underhook) enables smash passing and flattening.

## Related

See also: Half Guard, Pummeling, Overhooks, Grip Fighting, Wrestling"""
    },
    {
        "title": "Shrimping",
        "slug": "shrimping",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The fundamental hip escape movement — the most important defensive motion in grappling.",
        "content": """## Overview

Shrimping (also called the hip escape) is a ground movement where the grappler bridges onto one shoulder and drives their hips away from the opponent by pushing off one foot. The movement resembles the shape of a shrimp, hence the name. It is widely regarded as the single most important defensive movement in BJJ and grappling.

## Mechanics

From a bottom position, the grappler turns onto one hip and shoulder, plants one foot on the mat near their hip, and explosively drives the hips backward — away from the opponent. This creates space between the grappler's body and the opponent, which can be filled with frames, knees, or guard recovery.

## Applications

Shrimping is the engine behind almost every bottom escape and guard recovery: escaping side control, escaping mount, reguarding from half guard, and creating distance when being smashed. A grappler who cannot shrimp effectively will struggle to escape any pin.

The movement is so fundamental that it is drilled extensively in warm-ups at virtually every BJJ academy in the world.

## Related

See also: Frames and Framing, Bridging, Guard Retention, Side Control"""
    },
    {
        "title": "Grip Fighting",
        "slug": "grip-fighting",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The battle to establish, maintain, and strip grips — the invisible war that determines who controls the match.",
        "content": """## Overview

Grip fighting is the contest to establish favorable grips while denying or stripping the opponent's grips. It is often called the invisible battle because spectators rarely notice it, yet experienced grapplers recognize that the outcome of most exchanges is determined before the technique even begins — whoever wins the grip fight wins the position.

## Principles

**Establish first, deny second.** An active grip fighter is always working to get their own grips while preventing the opponent from settling into comfortable grips.

**Two on one.** When stripping grips, using both hands against one of the opponent's grips creates a mechanical advantage.

**Grip, don't grab.** Effective grips use specific fingers and hand positions optimized for the task — lapel grips, sleeve grips, collar ties, wrist controls all have distinct mechanics.

## Applications

In gi grappling, grip fighting involves collar grips, sleeve grips, lapel grips, and pant grips, each enabling different attacks and guards. In no-gi, grip fighting centers around collar ties, wrist controls, underhooks, overhooks, and two-on-one controls. In judo, kumi-kata (grip fighting) is a highly developed discipline with its own strategies and tactics.

## Related

See also: Underhooks, Closed Guard, Judo, Kuzushi"""
    },
    {
        "title": "Base and Posture",
        "slug": "base-and-posture",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The twin pillars of positional stability — maintaining structural integrity against sweeps, submissions, and off-balancing.",
        "content": """## Overview

Base and posture are the foundational concepts governing stability in grappling. Base refers to the distribution of weight and the positioning of support points (feet, knees, hands) to resist being swept, pushed, or pulled off balance. Posture refers to the alignment of the spine and head relative to the opponent — maintaining an upright, structurally sound position that resists submission attempts.

## Base

Good base means the grappler's center of gravity is low and centered over a wide support platform. On the feet, this means a staggered stance with knees bent. On the ground, it means distributing weight across multiple contact points and keeping the hips engaged.

The fundamental rule: if you can draw a line from your center of mass straight down and it falls outside your support points, you can be swept in that direction.

## Posture

Posture is most critical inside the opponent's guard. When the top player maintains an upright spine with their head up and hips forward, they neutralize most guard attacks. When posture is broken (pulled forward or tilted sideways), submissions and sweeps become available.

## Related

See also: Closed Guard, Guard Passing, Kuzushi, Sweeps"""
    },
    # ── PEOPLE ──────────────────────────────────────────────────────
    {
        "title": "Helio Gracie",
        "slug": "helio-gracie",
        "category": "person",
        "tags": ["Person"],
        "summary": "Founding patriarch of the Gracie family's Brazilian Jiu-Jitsu lineage, who adapted judo techniques for smaller practitioners.",
        "content": """## Overview

Helio Gracie (1913-2009) was a Brazilian martial artist and one of the founders of Brazilian Jiu-Jitsu. Along with his brothers, most notably Carlos Gracie, Helio adapted the techniques of Japanese judo and jiu-jitsu to emphasize leverage, timing, and ground fighting over strength and athleticism. His modifications created the foundation of what became the Gracie family's fighting system.

## Contributions

Helio's primary contribution was refining techniques to work for a smaller, physically weaker practitioner. Standing 5'10" and weighing approximately 140 pounds for much of his career, he could not rely on strength or explosive athleticism. His adaptations emphasized:

- Using the guard (fighting from the back) as an offensive weapon
- Maximizing leverage in every technique
- Emphasizing patience and energy conservation in fights
- Developing a hierarchy of positions based on control and finishing potential

## Legacy

Helio Gracie is revered as a central figure in the development of BJJ. His competitive career spanned decades, including legendary matches against larger opponents. His sons — Rickson, Royler, Royce, and others — continued the family legacy in competition and instruction, with Royce Gracie's UFC performances introducing BJJ to the world.

## Related

See also: Brazilian Jiu-Jitsu, Carlos Gracie, Royce Gracie, Rickson Gracie"""
    },
    {
        "title": "Gordon Ryan",
        "slug": "gordon-ryan",
        "category": "person",
        "tags": ["Person"],
        "summary": "Dominant no-gi grappler and multiple ADCC champion, known for his systematic approach to submission grappling.",
        "content": """## Overview

Gordon Ryan is an American submission grappler widely considered the most dominant no-gi competitor of his generation. A multiple-time ADCC world champion across weight classes and the absolute division, Ryan has established an unprecedented level of dominance in professional grappling.

## Career

A student of John Danaher, Ryan rose to prominence as part of the Danaher Death Squad — a team that revolutionized leg lock techniques and systematic approaches to no-gi grappling. His competitive record features an extraordinary finishing rate, with victories coming via submission against virtually every elite competitor of his era.

Ryan's game is characterized by suffocating top pressure, a systematic passing approach (particularly body lock passing), and the ability to submit opponents from every position. His back-taking ability and body triangle control are considered among the best in the history of the sport.

## Impact

Beyond competition, Ryan has been influential in demonstrating that submission grappling can be a viable professional career. His instructional content and competitive analysis have contributed to the growing sophistication of no-gi training methodology worldwide.

## Related

See also: ADCC, John Danaher, Heel Hook, Body Lock Pass, No-Gi Grappling"""
    },
    {
        "title": "John Danaher",
        "slug": "john-danaher",
        "category": "person",
        "tags": ["Person"],
        "summary": "Influential grappling instructor known for systematizing submission techniques and developing multiple world champions.",
        "content": """## Overview

John Danaher is a New Zealand-born Brazilian Jiu-Jitsu instructor widely regarded as one of the most influential coaches in the history of submission grappling. Based for decades in New York City, Danaher developed a systematic, principle-based approach to grappling instruction that produced multiple world champions and fundamentally changed how the sport is taught and practiced.

## Teaching Philosophy

Danaher's approach emphasizes understanding the underlying principles and mechanics of grappling rather than memorizing individual techniques in isolation. His system organizes grappling into interconnected subsystems — legs, back attacks, front headlocks, guard passing, pins — each with its own decision trees and tactical frameworks.

This systems-based methodology contrasted with the more traditional approach of teaching techniques individually, and its success at the highest levels of competition demonstrated the value of organized, strategic thinking in grappling instruction.

## The Leg Lock Revolution

Perhaps Danaher's most significant contribution was the development and popularization of a comprehensive leg lock system. While leg locks existed before Danaher, his systematic approach — connecting entries, control positions (ashi garami), and finishing mechanics into a coherent framework — transformed leg attacks from a niche specialization into a core component of elite no-gi grappling.

## Related

See also: Gordon Ryan, Heel Hook, Ashi Garami, Marcelo Garcia Academy"""
    },
    {
        "title": "Roger Gracie",
        "slug": "roger-gracie",
        "category": "person",
        "tags": ["Person"],
        "summary": "Ten-time IBJJF world champion considered by many the greatest BJJ competitor of all time.",
        "content": """## Overview

Roger Gracie is a Brazilian Jiu-Jitsu black belt and member of the Gracie family who is widely considered the greatest BJJ competitor of all time. His record of ten IBJJF World Championship gold medals — including multiple absolute division titles — is unmatched in the sport's history.

## Competitive Style

What made Roger extraordinary was not the complexity of his game but its perfection. He won world championships with fundamental techniques — closed guard, mount, cross collar choke from mount — executed at a level of precision and timing that the best competitors in the world could not stop even when they knew exactly what was coming.

His ability to take mount against elite black belts and finish with the cross collar choke became legendary. It demonstrated a principle that resonates throughout grappling: mastery of fundamentals beats novelty of technique.

## Legacy

Roger Gracie's career is often cited as evidence that deep mastery of basic positions and submissions is the most reliable path to competitive success. In an era of increasing technical specialization and exotic positions, his dominance with classical technique provided a counterpoint that continues to influence training philosophy.

## Related

See also: Brazilian Jiu-Jitsu, Mount, Cross Collar Choke, IBJJF Worlds, Gracie Family"""
    },
    # ── COMPETITIONS ────────────────────────────────────────────────
    {
        "title": "IBJJF World Championship",
        "slug": "ibjjf-world-championship",
        "category": "competition",
        "tags": ["Competition"],
        "summary": "The most prestigious gi Brazilian Jiu-Jitsu tournament, commonly known as the Mundials.",
        "content": """## Overview

The IBJJF World Jiu-Jitsu Championship (commonly called the Mundials or Worlds) is the most prestigious Brazilian Jiu-Jitsu tournament in the gi. Organized by the International Brazilian Jiu-Jitsu Federation, it has been held annually since 1996 and serves as the definitive test of gi grappling at every belt level from white through black.

## Format

The tournament uses a single-elimination bracket format with matches scored under IBJJF rules — points for sweeps, passes, mount, back mount, and knee on belly, with advantages as a secondary scoring criterion. Matches are decided by submission, points, advantages, or referee decision.

Weight classes range from rooster weight to ultra-heavy, plus an absolute (open weight) division where competitors of any weight can enter.

## Significance

Winning a black belt World Championship is considered the highest achievement in gi BJJ. The tournament has historically been dominated by Brazilian competitors but has become increasingly international as the sport has grown globally.

Multiple World Championship titles are the primary criterion by which gi competitors are ranked historically. Roger Gracie (10 gold medals), Buchecha (13 gold medals), and Marcelo Garcia are among the most decorated champions.

## Related

See also: ADCC, Roger Gracie, Brazilian Jiu-Jitsu, Pan American Championship"""
    },
    {
        "title": "EBI",
        "slug": "ebi",
        "category": "competition",
        "tags": ["Competition"],
        "summary": "Eddie Bravo Invitational — a submission-only tournament format designed to produce finishes.",
        "content": """## Overview

The Eddie Bravo Invitational (EBI) is a professional submission grappling tournament created by Eddie Bravo in 2014. Designed to eliminate the conservative, stalling-heavy dynamics that can plague points-based tournaments, EBI features a submission-only format with a unique overtime system that guarantees a finish in every match.

## Format

EBI uses a 16-person single-elimination bracket. Regulation matches are 10 minutes with no points — only submissions count. If no submission occurs in regulation, the match goes to overtime.

In overtime, each competitor gets a turn starting in a dominant position — back control with hooks (spider web) or an armbar position. The competitor must finish the submission or the defending competitor escapes. Whoever finishes fastest (or escapes fastest if neither finishes) wins.

## Impact

EBI's overtime rules created some of the most exciting competitive grappling moments and helped popularize professional submission grappling as a spectator sport. The format forced competitors to develop both offensive finishing ability and defensive escape skills under pressure.

## Related

See also: ADCC, Eddie Bravo, Submission Grappling, No-Gi Grappling"""
    },
    # ── STYLES ──────────────────────────────────────────────────────
    {
        "title": "Judo",
        "slug": "judo",
        "category": "style",
        "tags": ["Style"],
        "summary": "The Japanese martial art of throwing, founded by Jigoro Kano, and a direct ancestor of Brazilian Jiu-Jitsu.",
        "content": """## Overview

Judo is a Japanese martial art and Olympic sport founded by Jigoro Kano in 1882. Derived from traditional Japanese jujitsu, judo emphasizes throws (nage-waza), pins (osaekomi-waza), chokes (shime-waza), and joint locks (kansetsu-waza). It is the direct ancestor of Brazilian Jiu-Jitsu and remains one of the most widely practiced grappling arts in the world.

## Philosophy

Kano founded judo on two key principles: maximum efficiency with minimum effort (seiryoku zenyo) and mutual welfare and benefit (jita kyoei). These principles shaped both the technical approach — using the opponent's force and momentum against them — and the educational philosophy of the art.

## Technical Framework

Judo's technical curriculum is vast, encompassing over 60 recognized throwing techniques organized by the body mechanics used: hand techniques (te-waza), hip techniques (koshi-waza), foot and leg techniques (ashi-waza), and sacrifice techniques (sutemi-waza).

The concept of kuzushi (off-balancing) is central to judo — before any throw can succeed, the opponent must first be broken from their natural balance point. This principle of disrupting equilibrium before applying technique resonates across all grappling disciplines.

## Ground Fighting

While competition rules have increasingly limited ground fighting time in judo, the art includes a comprehensive ground fighting (ne-waza) system including pins, chokes, and armlocks. Many of the ground techniques used in BJJ originated in judo's ne-waza curriculum.

## Related

See also: Brazilian Jiu-Jitsu, Kuzushi, Osoto Gari, Seoi Nage, Kodokan"""
    },
    {
        "title": "Wrestling",
        "slug": "wrestling",
        "category": "style",
        "tags": ["Style"],
        "summary": "The world's oldest combat sport — a grappling discipline focused on takedowns, throws, and pins.",
        "content": """## Overview

Wrestling is one of the oldest forms of combat sport, with origins tracing back thousands of years. Modern competitive wrestling encompasses several distinct styles — freestyle, Greco-Roman, and folkstyle (collegiate) — each with its own ruleset, but all sharing the core objective of taking the opponent down and controlling them on the mat.

## Styles

**Freestyle wrestling:** The most internationally practiced style and an Olympic sport. Allows attacks on the entire body, including leg attacks. Emphasis on explosive takedowns, turns, and exposure (putting the opponent's back toward the mat).

**Greco-Roman wrestling:** An Olympic style that prohibits all attacks below the waist. Emphasizes upper body throws, clinch work, and par terre (ground) techniques. Produces some of the most spectacular throws in combat sports.

**Folkstyle (collegiate):** Practiced primarily in American high schools and colleges. Emphasizes riding time (controlling the opponent on the ground), escapes, and a more complete ground game than international styles.

## Impact on Grappling

Wrestling's emphasis on takedowns, top pressure, pace, and physical conditioning has made it an invaluable cross-training discipline for BJJ and MMA competitors. Many of the most successful MMA fighters have wrestling backgrounds, and wrestling-based passing and top control have become increasingly prominent in competitive BJJ.

## Related

See also: Double Leg Takedown, Single Leg Takedown, Freestyle Wrestling, Greco-Roman"""
    },
    {
        "title": "Sambo",
        "slug": "sambo",
        "category": "style",
        "tags": ["Style"],
        "summary": "A Russian martial art combining judo, wrestling, and folk styles, known for its leg lock expertise.",
        "content": """## Overview

Sambo (an acronym for SAMozashchita Bez Oruzhiya — self-defense without weapons) is a Russian martial art developed in the early Soviet era by combining techniques from judo, wrestling, and various folk wrestling styles from across the Soviet Union. It exists in two primary forms: Sport Sambo and Combat Sambo.

## Styles

**Sport Sambo** resembles a hybrid of judo and wrestling. Competitors wear a jacket (kurtka) similar to a judo gi top but paired with shorts rather than pants. The rules allow throws, pins, and a wide range of leg locks but prohibit chokes — a key distinction from both judo and BJJ.

**Combat Sambo** adds strikes and is closer to a complete fighting system, bearing resemblance to modern MMA. It includes punches, kicks, throws, ground fighting, and submissions including chokes.

## Leg Lock Legacy

Sambo's most significant contribution to the broader grappling world is its sophisticated leg lock system. Because sambo rules allowed leg locks (including heel hooks and kneebars) while simultaneously prohibiting chokes, sambo practitioners developed leg attacks to a higher degree than practitioners of other arts during much of the 20th century.

## Related

See also: Judo, Wrestling, Heel Hook, Kneebar, Combat Sambo"""
    },
    # ── MORE TECHNIQUES ─────────────────────────────────────────────
    {
        "title": "Berimbolo",
        "slug": "berimbolo",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An inverted back-take from De La Riva guard that revolutionized modern sport BJJ.",
        "content": """## Overview

The berimbolo is an inverted rolling back-take technique typically initiated from De La Riva guard. The attacker uses the DLR hook and upper body grips to invert underneath the opponent, then uses the rotation to off-balance them and come up behind them in back control. The technique transformed competitive sport BJJ when the Mendes brothers and others began using it to devastating effect in the early 2010s.

## Mechanics

The berimbolo begins with a De La Riva hook and grip on the far leg or belt. The attacker inverts (rolls onto their shoulders/upper back), using the DLR hook as the fulcrum. As the attacker rotates, they use the momentum and leg hooks to spin underneath and behind the opponent, ultimately securing back control with hooks.

## Controversy and Impact

The berimbolo sparked debate about the direction of sport BJJ — critics argued it prioritized acrobatic movements over practical grappling, while supporters pointed to its effectiveness at the highest levels of competition. Regardless of the debate, the berimbolo fundamentally changed guard play by introducing a new vector of attack (inversion and rotation) that demanded new defensive skills from top players.

## Related

See also: De La Riva Guard, Back Control, Kiss of the Dragon, Inversions"""
    },
    {
        "title": "Toreando Pass",
        "slug": "toreando-pass",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A speed-based guard pass that redirects the opponent's legs to the side like a matador with a bull.",
        "content": """## Overview

The toreando (or toreada, bullfighter pass) is a speed-based guard pass where the passer grips both of the opponent's legs (typically at the knees or ankles) and redirects them to one side while stepping around to the opposite side to achieve a dominant position. The name references the bullfighter's motion of redirecting the bull's charge.

## Mechanics

The passer establishes grips on both legs, drives them to one side, and simultaneously circles to the other side to clear the legs entirely. Speed and grip strength are essential — the pass works by moving the legs faster than the guard player can re-establish frames or hooks.

The toreando is most effective when the guard player's legs are extended or when the passer can break the guard player's grips first. It chains naturally with other speed passes like the leg drag and X-pass.

## Related

See also: Guard Passing, Leg Drag, Speed Passing, Open Guard"""
    },
    {
        "title": "Americana",
        "slug": "americana",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A shoulder lock applied from top position, bending the opponent's arm into an L-shape and rotating it toward the mat.",
        "content": """## Overview

The Americana (also called ude garami or keylock) is a shoulder lock submission applied from a top position — most commonly mount or side control. The attacker pins the opponent's arm to the mat in an L-shape, then uses a figure-four grip to rotate the wrist toward the mat, attacking the shoulder joint.

## Mechanics

The attacker controls the opponent's wrist with one hand, pinning it to the mat. The other arm threads under the opponent's elbow and grips their own wrist, forming a figure-four. The submission is applied by sliding the opponent's wrist toward their hip while keeping the elbow pinned — this rotational force exceeds the shoulder's range of motion.

## Position

The Americana works best from top positions where the attacker's bodyweight can assist in pinning the arm. From mount and side control, gravity aids both the pin and the finish. The technique is less common from bottom positions because the attacker lacks the weight advantage needed to isolate and control the arm.

## Relationship to Kimura

The Americana is mechanically the reverse of the kimura — the Americana pushes the wrist toward the mat (external rotation), while the kimura pulls the wrist toward the back (internal rotation). Together, they form a complementary pair of shoulder attacks from dominant positions.

## Related

See also: Kimura, Mount, Side Control, Shoulder Lock"""
    },
    {
        "title": "Straight Ankle Lock",
        "slug": "straight-ankle-lock",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "The most fundamental leg lock — a submission that hyperextends the ankle joint.",
        "content": """## Overview

The straight ankle lock (also called the Achilles lock or ashi gatame) is the most basic leg lock submission, targeting the ankle by hyperextending the joint. It is typically the first leg lock taught to beginners because it is legal at all belt levels in IBJJF competition and carries lower injury risk than rotational knee attacks.

## Mechanics

The attacker controls the opponent's leg in ashi garami or a similar leg entanglement, wraps their forearm around the Achilles tendon, and clasps their hands together. The finish involves arching back while driving the wrist blade into the Achilles tendon and extending the hips to hyperextend the ankle.

## Significance

While considered a basic technique, the straight ankle lock has experienced a renaissance as modern leg lock systems have elevated the position and control associated with all lower body attacks. High-level competitors have demonstrated that with proper positioning and finishing mechanics, the straight ankle lock remains effective at the highest levels.

## Related

See also: Heel Hook, Kneebar, Toe Hold, Ashi Garami"""
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Get admin user (created by seed_articles.py)
        admin = User.query.filter_by(username='GrapplingWiki').first()
        if not admin:
            admin = User(username='GrapplingWiki', email='admin@grapplingwiki.com')
            admin.set_password('grapplingwiki2026')
            db.session.add(admin)
            db.session.flush()
            print("Created admin user: GrapplingWiki")

        # Get existing tags
        tag_map = {}
        for tag in Tag.query.all():
            tag_map[tag.name] = tag

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

            for tag_name in data.get("tags", []):
                if tag_name in tag_map:
                    article.tags.append(tag_map[tag_name])

            db.session.add(article)
            db.session.flush()

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
        total = Article.query.count()
        print(f"\nDone! Created {created} new articles. Total articles: {total}")


if __name__ == '__main__':
    seed()

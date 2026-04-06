"""
Seed script: expand the wiki with more techniques, positions, and concepts.
Run from project root: python scripts/seed_articles_3.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Article, ArticleRevision, Category

ARTICLES = [
    # ── UPPER BODY TAKEDOWNS ──
    {
        "title": "Osoto Gari",
        "slug": "osoto-gari",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A major outer reap — one of judo's most powerful and commonly used throws.",
        "content": "## Overview\n\nOsoto Gari is a reaping throw where the attacker drives the opponent backward while sweeping their supporting leg. It is classified as an upper body takedown initiated from the clinch.\n\n## Mechanics\n\nThe attacker controls the opponent's upper body (typically sleeve and lapel, or collar tie and underhook in no-gi), drives their weight onto the opponent's far leg, then reaps that leg while driving through with the chest."
    },
    {
        "title": "Seoi Nage",
        "slug": "seoi-nage",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A shoulder throw — one of the most spectacular and effective takedowns in grappling.",
        "content": "## Overview\n\nSeoi Nage is a shoulder throw where the attacker turns in beneath the opponent's center of gravity and throws them over their shoulder. It requires winning the grip fight to create the entry angle.\n\n## Mechanics\n\nThe attacker turns their back to the opponent, loads them onto their hips/shoulder, and throws by pulling forward and down while extending the legs."
    },
    {
        "title": "Uchi Mata",
        "slug": "uchi-mata",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An inner thigh throw — arguably the most versatile throw in all of grappling.",
        "content": "## Overview\n\nUchi Mata is an inner thigh throw that uses rotational momentum and a lifting leg sweep to unbalance the opponent. It is effective in both gi and no-gi contexts.\n\n## Mechanics\n\nThe attacker enters with a turning motion, sweeping the opponent's inner thigh with their leg while pulling with the upper body to create a rotational throw."
    },
    {
        "title": "Snap Down",
        "slug": "snap-down",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A front headlock takedown that collapses the opponent's posture and exposes the back.",
        "content": "## Overview\n\nThe snap down uses a collar tie or head control to violently pull the opponent's head downward, collapsing their posture. It typically leads to front headlock position or back exposure.\n\n## Mechanics\n\nFrom collar tie position, the attacker snaps the opponent's head down while circling to the side, aiming to get behind them or establish a front headlock."
    },
    {
        "title": "Arm Drag",
        "slug": "arm-drag",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A fundamental grip-based transition that clears the opponent's arm to access the back or set up takedowns.",
        "content": "## Overview\n\nThe arm drag is a versatile technique used from standing, seated guard, and many other positions. By controlling the opponent's wrist and tricep, the attacker drags them past to create an angle advantage.\n\n## Mechanics\n\nGrip the opponent's wrist with one hand and tricep/elbow with the other, then explosively pull their arm across your body while stepping to the side, exposing their back."
    },
    {
        "title": "Single Leg Takedown",
        "slug": "single-leg-takedown",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A foundational lower body takedown that attacks one of the opponent's legs.",
        "content": "## Overview\n\nThe single leg takedown is one of the most versatile and commonly used takedowns in wrestling and no-gi grappling. The attacker shoots in to capture one of the opponent's legs and works to bring them to the ground.\n\n## Mechanics\n\nLevel change, penetration step to close distance, head on the inside, arms locked around one leg. Finish by running the pipe, tripping, or lifting."
    },
    {
        "title": "Ankle Pick",
        "slug": "ankle-pick",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A low-risk takedown that uses misdirection to grab the opponent's ankle while pushing them off balance.",
        "content": "## Overview\n\nThe ankle pick is a quick, efficient takedown that doesn't require a deep level change. The attacker uses upper body pressure to shift the opponent's weight onto one foot, then picks that ankle.\n\n## Mechanics\n\nFrom collar tie or two-on-one, push the opponent's weight to one side, then drop level and grab the weighted ankle while pulling them forward."
    },
    {
        "title": "High Crotch",
        "slug": "high-crotch",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A wrestling takedown attacking the opponent's hip crease — a versatile chain wrestling entry.",
        "content": "## Overview\n\nThe high crotch is a powerful takedown where the attacker drives into the opponent's hip while controlling the inner thigh. It chains seamlessly into single legs, double legs, and back takes.\n\n## Mechanics\n\nLevel change and penetration step, head on the inside, arm wraps the inner thigh at the hip crease. Lift and turn the corner to finish."
    },
    # ── FAR DISTANCE GUARDS ──
    {
        "title": "Spider Guard",
        "slug": "spider-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A far-distance guard using sleeve grips and feet on biceps to control and off-balance the opponent.",
        "content": "## Overview\n\nSpider Guard is an open guard position where the bottom player controls both of the opponent's sleeves while placing their feet on the biceps. This creates a strong framework for sweeps, submissions, and transitions.\n\n## Distance Spectrum\n\nFar distance — maximum extension between players. Requires gi grips to maintain control at range."
    },
    {
        "title": "X-Guard",
        "slug": "x-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A powerful sweeping guard played underneath the opponent with legs forming an X shape on one leg.",
        "content": "## Overview\n\nX-Guard is an open guard where the bottom player positions underneath the opponent, hooking both legs around one of the opponent's legs in an X configuration. It generates tremendous sweeping leverage.\n\n## Distance Spectrum\n\nFar to mid distance — the guard player is beneath the standing opponent with maximum mechanical leverage on one leg."
    },
    {
        "title": "Single Leg X",
        "slug": "single-leg-x",
        "category": "position",
        "tags": ["Position"],
        "summary": "A guard position controlling one leg with an outside ashi garami configuration — the gateway to leg attacks.",
        "content": "## Overview\n\nSingle Leg X (also called Ashi Garami or Outside Ashi) is a guard position where the bottom player controls one of the opponent's legs. It is the primary entry point to the leg lock game.\n\n## Distance Spectrum\n\nFar distance — players are connected only through the leg entanglement."
    },
    {
        "title": "Lasso Guard",
        "slug": "lasso-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A gi-based guard where the leg wraps around the opponent's arm, creating powerful leverage for sweeps.",
        "content": "## Overview\n\nLasso Guard uses a deep leg wrap around the opponent's arm combined with sleeve control. The lasso leg creates a powerful lever that controls the opponent's posture and limits their passing options.\n\n## Distance Spectrum\n\nFar distance — the leg wrap maintains separation while providing offensive control."
    },
    {
        "title": "Reverse De La Riva",
        "slug": "reverse-de-la-riva",
        "category": "position",
        "tags": ["Position"],
        "summary": "An inverted DLR hook used to off-balance the passer and create back take opportunities.",
        "content": "## Overview\n\nReverse De La Riva (RDLR) uses an inside hook on the opponent's lead leg (opposite side from standard DLR). It is primarily used as a reaction to the opponent attempting to pass to one side.\n\n## Distance Spectrum\n\nFar distance — connected through the leg hook with options to invert or take the back."
    },
    # ── MID DISTANCE GUARDS ──
    {
        "title": "Z-Guard",
        "slug": "z-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A half guard variation with a knee shield frame creating space and offensive angles.",
        "content": "## Overview\n\nZ-Guard (or Knee Shield Half Guard) uses a diagonal knee frame across the opponent's body from half guard. The knee shield prevents the top player from closing distance and creates angles for sweeps and back takes.\n\n## Distance Spectrum\n\nMid distance — the knee frame maintains space within the half guard entanglement."
    },
    {
        "title": "Deep Half Guard",
        "slug": "deep-half-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A half guard variation where the bottom player dives underneath the opponent for powerful sweeps.",
        "content": "## Overview\n\nDeep Half Guard is entered when the bottom player in half guard dives beneath the opponent's center of gravity. By getting underneath, the bottom player gains tremendous sweeping leverage.\n\n## Distance Spectrum\n\nMid to close distance — the bottom player is directly beneath the opponent's hips."
    },
    # ── CLOSE DISTANCE GUARDS ──
    {
        "title": "Rubber Guard",
        "slug": "rubber-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A flexible closed guard variation using the leg over the opponent's shoulder to control posture.",
        "content": "## Overview\n\nRubber Guard (developed by Eddie Bravo) uses extreme hip flexibility to place the shin behind the opponent's head from closed guard. This eliminates the need for gi grips in controlling posture.\n\n## Distance Spectrum\n\nClose distance — the guard player's leg behind the head forces chest-to-chest proximity."
    },
    # ── CLOSE DISTANCE GUARDS (additional) ──
    {
        "title": "Worm Guard",
        "slug": "worm-guard",
        "category": "position",
        "tags": ["Position"],
        "summary": "A lapel-based closed guard where the gi tail wraps around the opponent's leg, creating a closed-circuit control system.",
        "content": "## Overview\n\nWorm Guard (developed by Keenan Cornelius) uses the opponent's own lapel, threaded under their leg and gripped by the guard player. This creates a closed control loop — the gi essentially extends the guard player's leg reconnection through the fabric, making it functionally a closed guard despite appearances.\n\n## Leg Reconnection\n\nThe lapel acts as an extension of the guard player's grip system, creating a closed circuit of control similar to closed guard. The opponent cannot simply disengage because the fabric locks the position.\n\n## Distance Spectrum\n\nClose distance — the lapel wrap forces proximity and prevents the passer from creating distance."
    },
    # ── DOMINANT POSITIONS ──
    {
        "title": "North-South",
        "slug": "north-south",
        "category": "position",
        "tags": ["Position"],
        "summary": "A chest-to-chest pin where the top player is inverted relative to the bottom player.",
        "content": "## Overview\n\nNorth-South is a dominant pinning position where the top player lies chest-to-chest but facing the opposite direction from the bottom player. It provides excellent control and submission opportunities.\n\n## Distance Spectrum\n\nClose distance — maximum surface contact, extremely difficult to escape."
    },
    # ── SIDE CONTROL POSITION VARIANTS ──
    {
        "title": "Kesa Gatame",
        "slug": "kesa-gatame",
        "category": "position",
        "tags": ["Position"],
        "summary": "The scarf hold — a side control variant using a head-and-arm clinch with the hips turned toward the opponent's head.",
        "content": "## Overview\n\nKesa Gatame (scarf hold) is a judo-derived side control variant where the top player sits with their hip against the opponent's side, controlling the head under their arm and gripping around the far arm. The hips face toward the opponent's head rather than perpendicular.\n\n## Game State\n\nSide control variant. The unique hip angle creates different submission and transition opportunities compared to standard cross-body side control.\n\n## Unified Theory\n\nThe turned hip position creates a different force vector — weight is applied diagonally rather than straight down, making certain escapes harder while opening others."
    },
    {
        "title": "Reverse Kesa Gatame",
        "slug": "reverse-kesa-gatame",
        "category": "position",
        "tags": ["Position"],
        "summary": "A side control variant where the top player faces the opponent's legs, controlling the far hip.",
        "content": "## Overview\n\nReverse Kesa Gatame flips the orientation of the scarf hold — the top player faces toward the opponent's legs instead of their head. This gives access to leg attacks and north-south transitions while maintaining strong top pressure.\n\n## Game State\n\nSide control variant with unique transition opportunities toward leg attacks and north-south."
    },
    {
        "title": "Double Under Side Control",
        "slug": "double-under-side-control",
        "category": "position",
        "tags": ["Position"],
        "summary": "A crushing side control variation with both arms threaded under the opponent's body.",
        "content": "## Overview\n\nDouble Under Side Control threads both underhooks beneath the opponent while in side mount. This eliminates the bottom player's frames entirely — both arms are trapped above the underhooks, removing their primary escape tools.\n\n## Game State\n\nSide control variant. Extremely high pressure. The double underhook removes the opponent's ability to frame on the near hip or crossface side.\n\n## Unified Theory\n\nThis is maximum option compression from side control — the bottom player's primary escape mechanisms (hip frames, arm frames, bridging space) are all neutralized simultaneously."
    },
    {
        "title": "Reverse Side Control",
        "slug": "reverse-side-control",
        "category": "position",
        "tags": ["Position"],
        "summary": "A side control variant where the top player faces away from the opponent's head, back toward their legs.",
        "content": "## Overview\n\nReverse Side Control (also called Twister Side Control or Reverse Crossbody) positions the top player perpendicular but facing the opponent's feet instead of their head. This opens leg lock entries and truck/twister transitions.\n\n## Game State\n\nSide control variant. Unusual orientation that confuses standard escape patterns."
    },
    {
        "title": "Shoulder Pressure",
        "slug": "shoulder-pressure",
        "category": "position",
        "tags": ["Position"],
        "summary": "A side control refinement that drives the crossface shoulder into the opponent's jaw to create suffocating pressure.",
        "content": "## Overview\n\nShoulder Pressure is a specific side control detail where the top player drives their crossface shoulder under the opponent's chin and into their jaw/neck. Combined with chest-to-chest contact and sprawled legs, this creates immense top pressure that makes breathing difficult and saps the bottom player's will to escape.\n\n## Unified Theory\n\nThis is the physics of top position distilled — the top player's shoulder creates a focused force vector directly into the opponent's neck while their body weight pins the torso. It represents the concept of efficient pressure: maximum force through minimum contact area."
    },
    # ── MORE SUBMISSIONS ──
    {
        "title": "Bow and Arrow Choke",
        "slug": "bow-and-arrow-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "One of the highest-percentage chokes from back control, using the collar and leg to create a powerful strangle.",
        "content": "## Overview\n\nThe Bow and Arrow Choke is a devastating gi choke applied from back control. The attacker grips the collar with one hand and the far leg with the other, stretching the opponent like a bow to tighten the choke.\n\n## Force Vector\n\nArterial compression — bilateral pressure on the carotid arteries through the collar grip, amplified by the stretching action."
    },
    {
        "title": "Cross Collar Choke",
        "slug": "cross-collar-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A fundamental gi choke using crossed grips on the collar, available from mount and guard.",
        "content": "## Overview\n\nThe Cross Collar Choke uses both hands gripping deep into the opponent's collar in a crossed configuration. The forearms create a scissoring pressure on the carotid arteries.\n\n## Force Vector\n\nArterial compression — the crossed forearms create bilateral pressure on the neck."
    },
    {
        "title": "Anaconda Choke",
        "slug": "anaconda-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An arm-in head and arm choke similar to the D'Arce but with opposite arm threading.",
        "content": "## Overview\n\nThe Anaconda Choke is a compression choke where the attacker threads their arm under the opponent's neck and through the armpit, locking a figure-four grip. The attacker then rolls to tighten.\n\n## Force Vector\n\nCompression/wedge — the opponent's own shoulder is driven into the carotid artery."
    },
    {
        "title": "Ezekiel Choke",
        "slug": "ezekiel-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A sneaky inside-sleeve choke that can be applied from mount, guard, and even inside the opponent's guard.",
        "content": "## Overview\n\nThe Ezekiel Choke uses the sleeve of the gi as a lever, with one hand threaded inside the sleeve gripping the wrist, while the forearm applies pressure to the throat.\n\n## Force Vector\n\nCompression/wedge — the forearm and sleeve create a crushing mechanism against the trachea and arteries."
    },
    {
        "title": "North-South Choke",
        "slug": "north-south-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A suffocating chest-pressure choke applied from north-south position.",
        "content": "## Overview\n\nThe North-South Choke uses the attacker's shoulder and arm to compress the opponent's neck while the chest drives downward. Made famous by Marcelo Garcia.\n\n## Force Vector\n\nArterial compression — the attacker's shoulder drives into the carotid while the arm wraps the head."
    },
    {
        "title": "Arm Triangle",
        "slug": "arm-triangle",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A head-and-arm choke using the opponent's own shoulder as one side of the strangle.",
        "content": "## Overview\n\nThe Arm Triangle (Kata Gatame) traps the opponent's arm against their neck, then the attacker closes the triangle with their arms, using the opponent's own shoulder as one wall of the choke.\n\n## Force Vector\n\nArterial compression — the opponent's shoulder compresses one carotid while the attacker's arm compresses the other."
    },
    {
        "title": "Kneebar",
        "slug": "kneebar",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A leg lock that hyperextends the knee joint — the armbar of the lower body.",
        "content": "## Overview\n\nThe Kneebar is a leg submission that hyperextends the opponent's knee by controlling the leg between the attacker's legs and hips, then bridging to apply pressure against the natural bend.\n\n## Force Vector\n\nExtension — hyperextension of the knee joint, mechanically identical to an armbar applied to the leg."
    },
    {
        "title": "Toe Hold",
        "slug": "toe-hold",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A foot lock that applies torsion to the ankle and knee through rotational pressure on the foot.",
        "content": "## Overview\n\nThe Toe Hold grips the opponent's foot and rotates it inward (toward the centerline), creating torsional stress on the ankle and knee ligaments.\n\n## Force Vector\n\nTorsion — rotational force on the ankle/knee complex."
    },
    {
        "title": "Calf Slicer",
        "slug": "calf-slicer",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A compression lock that wedges the shin bone into the opponent's calf muscle, folding the knee.",
        "content": "## Overview\n\nThe Calf Slicer places the attacker's shin or forearm behind the opponent's knee, then folds the leg to create extreme compression on the calf muscle and pressure on the knee joint.\n\n## Force Vector\n\nCompression/wedge — a fulcrum is inserted behind the knee and the leg is folded around it."
    },
    {
        "title": "Wrist Lock",
        "slug": "wrist-lock",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A joint lock attacking the wrist — available from virtually every position.",
        "content": "## Overview\n\nWrist Locks attack the wrist joint by bending it past its comfortable range. They are available from nearly every position and are often caught when the opponent is focused on defending other submissions.\n\n## Force Vector\n\nExtension — hyperflexion or hyperextension of the wrist joint."
    },
    {
        "title": "Buggy Choke",
        "slug": "buggy-choke",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An unorthodox choke from bottom side control using the legs to trap the head and arm.",
        "content": "## Overview\n\nThe Buggy Choke is a relatively new submission executed from bottom side control. The bottom player threads their far leg over the opponent's head and under the near-side arm, creating a triangle-like squeeze.\n\n## Force Vector\n\nCompression/wedge — the leg and arm create bilateral compression on the neck."
    },
    # ── MORE SWEEPS ──
    {
        "title": "Hip Bump Sweep",
        "slug": "hip-bump-sweep",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An explosive sweep from closed guard using a sit-up motion to topple the opponent.",
        "content": "## Overview\n\nThe Hip Bump Sweep is executed from closed guard. The bottom player opens guard, sits up explosively, and bumps the opponent with their hip while posting on one hand, driving them over.\n\n## Polarity Flip\n\nFrom closed guard (close distance) to mount — reverses top/bottom dynamic."
    },
    {
        "title": "Flower Sweep",
        "slug": "flower-sweep",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A fundamental closed guard sweep using sleeve control and leg elevation to roll the opponent.",
        "content": "## Overview\n\nThe Flower Sweep (Pendulum Sweep) uses a sleeve grip and same-side collar grip from closed guard. The bottom player opens guard, swings their leg high to create momentum, and rolls the opponent.\n\n## Polarity Flip\n\nFrom closed guard (close distance) to mount — clean polarity reversal."
    },
    {
        "title": "Tripod Sweep",
        "slug": "tripod-sweep",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "An open guard sweep using a push-pull action with feet on hip and behind the ankle.",
        "content": "## Overview\n\nThe Tripod Sweep is a foundational open guard sweep. One foot pushes the opponent's hip while the other hooks behind their ankle. Combined with a collar or sleeve grip pulling them forward, the opponent is toppled.\n\n## Polarity Flip\n\nFrom open guard (far distance) to top position."
    },
    {
        "title": "Knee Slice Pass",
        "slug": "knee-slice-pass",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "One of the most fundamental and high-percentage guard passes in modern grappling.",
        "content": "## Overview\n\nThe Knee Slice (or Knee Cut) pass slides the knee across the opponent's thigh while controlling the upper body. It compresses the distance spectrum from mid/far to past guard.\n\n## Distance Compression\n\nFrom half/open guard → side control. One of the most reliable distance compressions in grappling."
    },
    {
        "title": "Leg Drag Pass",
        "slug": "leg-drag-pass",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A powerful passing technique that pins both opponent's legs to one side, opening a clear lane past guard.",
        "content": "## Overview\n\nThe Leg Drag controls the opponent's far leg and drags it across their body, pinning both legs to one side. This creates a clear lane to pass to side control or the back.\n\n## Distance Compression\n\nFrom open guard (far distance) → side control or back control."
    },
    {
        "title": "Body Lock Pass",
        "slug": "body-lock-pass",
        "category": "technique",
        "tags": ["Technique"],
        "summary": "A pressure-based passing system using a tight body lock grip to smash through guard.",
        "content": "## Overview\n\nThe Body Lock Pass uses a tight body lock (gable grip around the opponent's torso) from inside their guard. The passer drives forward, smashing the guard open with pressure and hip switching to clear the legs.\n\n## Distance Compression\n\nFrom closed/half guard → side control through pure pressure."
    },
    # ── LEG ENTANGLEMENT POSITIONS ──
    {
        "title": "Ashi Garami",
        "slug": "ashi-garami",
        "category": "position",
        "tags": ["Position"],
        "summary": "The foundational leg entanglement — controlling the opponent's leg between your legs for leg lock attacks.",
        "content": "## Overview\n\nAshi Garami (foot entanglement) is the base position of the leg lock game. The attacker controls one of the opponent's legs between their own, with hips close to the knee line. From here, heel hooks, kneebars, toe holds, and ankle locks become available.\n\n## Distance Spectrum\n\nFar distance — players are connected only through the leg entanglement. Upper bodies are separated.\n\n## Unified Theory\n\nAshi garami is a guard position where the grip battle is fought with the legs rather than the hands. The attacker's legs isolate the opponent's leg from their body structure, creating the precondition for leg lock submissions."
    },
    {
        "title": "Inside Sankaku",
        "slug": "inside-sankaku",
        "category": "position",
        "tags": ["Position"],
        "summary": "The saddle position — the highest-control leg entanglement, triangling the opponent's leg.",
        "content": "## Overview\n\nInside Sankaku (also called the Saddle, Honeyhole, or 411) is the most dominant leg entanglement. The attacker triangles the opponent's leg between their own, creating maximum control and isolation for heel hook attacks.\n\n## Distance Spectrum\n\nFar to mid distance — tighter control than standard ashi garami.\n\n## Unified Theory\n\nThe saddle is to leg locks what mount is to upper body submissions — the highest-control position in its subsystem. The triangled legs prevent the opponent from extracting their knee, compressing their options toward zero."
    },
    {
        "title": "50/50",
        "slug": "fifty-fifty",
        "category": "position",
        "tags": ["Position"],
        "summary": "A symmetrical leg entanglement where both players have equal leg lock threats.",
        "content": "## Overview\n\n50/50 is a symmetrical guard position where both players' legs are entangled in mirror fashion. Both have equal access to heel hooks, toe holds, and sweeps. Named because the position is theoretically equal.\n\n## Distance Spectrum\n\nMid distance — players are connected through mirrored leg hooks.\n\n## Unified Theory\n\n50/50 is unique in the grappling map — it is one of the only ground positions where the option space is truly symmetrical, like standing neutral. The grip fight within 50/50 determines who attacks first."
    },
    {
        "title": "Outside Ashi",
        "slug": "outside-ashi",
        "category": "position",
        "tags": ["Position"],
        "summary": "A leg entanglement controlling the opponent's leg from the outside — ideal for straight ankle locks.",
        "content": "## Overview\n\nOutside Ashi Garami positions the attacker's legs on the outside of the opponent's trapped leg, with hips facing away. It provides strong control for straight ankle locks and transitions to other entanglements.\n\n## Distance Spectrum\n\nFar distance — maximum separation with control through the outside leg hook."
    },
    {
        "title": "Cross Ashi",
        "slug": "cross-ashi",
        "category": "position",
        "tags": ["Position"],
        "summary": "A cross-body leg entanglement that exposes the heel for outside heel hook attacks.",
        "content": "## Overview\n\nCross Ashi Garami (also called Outside Sankaku or Cross Ashi) involves controlling the opponent's leg while crossing to the opposite side. This exposes the heel for outside heel hooks.\n\n## Distance Spectrum\n\nFar distance — connected through a cross-body leg configuration."
    },
    # ── CONCEPTS ──
    {
        "title": "Guard Retention",
        "slug": "guard-retention",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The defensive skill of maintaining guard position against passing attempts — distance creation in action.",
        "content": "## Overview\n\nGuard Retention is the art of preventing the opponent from passing your guard. It is fundamentally about creating and maintaining distance when the passer is trying to compress it.\n\n## Unified Theory\n\nGuard retention is the defensive counterpart to passing. It resists distance compression, using frames, hip movement, and reguarding to maintain the guard player's option space."
    },
    {
        "title": "Chain Wrestling",
        "slug": "chain-wrestling",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The art of linking takedown attempts in sequence — when one fails, the next begins.",
        "content": "## Overview\n\nChain Wrestling is the practice of linking takedown attempts together in rapid succession. Each failed attempt creates a reaction that opens the next attack. It is tempo-driven: the attacker maintains initiative by never letting the exchange reset.\n\n## Unified Theory\n\nChain wrestling is option compression applied to standing. Each attack narrows the defender's responses, and each response feeds the next attack."
    },
    {
        "title": "Pressure",
        "slug": "pressure",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The application of body weight through optimal contact points to limit the opponent's movement options.",
        "content": "## Overview\n\nPressure in grappling is the strategic application of body weight through specific contact points. Effective pressure makes the opponent carry your weight in positions where they cannot generate escape force.\n\n## Unified Theory\n\nPressure is the physics of top position. The top player positions their center of mass to create force vectors that directly oppose the opponent's escape vectors."
    },
    {
        "title": "Weight Distribution",
        "slug": "weight-distribution",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The skill of directing body weight to specific contact points for maximum control efficiency.",
        "content": "## Overview\n\nWeight Distribution is the moment-to-moment skill of choosing where to place your weight relative to the opponent. It is the active, dynamic aspect of top control.\n\n## Unified Theory\n\nThis is the real-time balancing game described in the Physics of Top Position. The top player continuously adjusts their center of mass to shut down escape vectors."
    },
    {
        "title": "Inside Position",
        "slug": "inside-position",
        "category": "concept",
        "tags": ["Concept"],
        "summary": "The principle that the player whose limbs are inside (closer to centerline) has the structural advantage.",
        "content": "## Overview\n\nInside Position refers to having your arms, knees, or feet positioned between the opponent's limbs, closer to their centerline. Whoever controls inside position has a structural advantage — better frames, better grips, better leverage.\n\n## Unified Theory\n\nInside position is a grip state advantage. The inside player can apply force vectors closer to the opponent's center of mass, making their techniques more efficient."
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='GrapplingWiki').first()
        if not admin:
            admin = User(username='GrapplingWiki', email='admin@grapplingwiki.com')
            admin.set_password('grapplingwiki2026')
            db.session.add(admin)
            db.session.flush()

        cat_map = {}
        for cat in Category.query.all():
            cat_map[cat.slug] = cat

        created = 0
        for data in ARTICLES:
            existing = Article.query.filter_by(slug=data["slug"]).first()
            if existing:
                print(f"  Skipping (exists): {data['title']}")
                continue

            cat_slug = data["category"]
            cat = cat_map.get(cat_slug)

            article = Article(
                title=data["title"],
                slug=data["slug"],
                content=data["content"].strip(),
                summary=data["summary"],
                author_id=admin.id,
                category=data["category"],
                category_id=cat.id if cat else None,
                is_published=True,
                view_count=0
            )

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
        print(f"\nDone! Created {created} new articles.")


if __name__ == '__main__':
    seed()

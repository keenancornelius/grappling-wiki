"""
Backfill taxonomy fields on existing articles.
Maps each article slug to its mechanism, target, spatial_qualifier, and graph_tier.

Run:  python scripts/backfill_taxonomy.py
Safe to run multiple times — overwrites taxonomy data each time.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'grappling_wiki.db')

# ══════════════════════════════════════════════════════════
# TAXONOMY DATA
#
# Each entry: slug → (mechanism, target, spatial_qualifier, graph_tier)
# graph_tier is a comma-separated list of sys_ node IDs.
# ══════════════════════════════════════════════════════════

TAXONOMY = {
    # ── CONCEPTS ──
    'grip-fighting':       ('concept', 'body',     None,      'sys_standing'),
    'underhooks':          ('concept', 'body',     'inner',   'sys_standing,sys_upper_td'),
    'base-and-posture':    ('concept', 'body',     None,      'sys_standing'),
    'inside-position':     ('concept', 'body',     'inner',   'sys_standing,sys_mid_guard'),
    'chain-wrestling':     ('concept', 'body',     None,      'sys_standing,sys_upper_td,sys_lower_td'),
    'frames-and-framing':  ('concept', 'body',     None,      'sys_close_guard,sys_side_control'),
    'shrimping':           ('concept', 'hip',      None,      'sys_close_guard,sys_side_control'),
    'guard-retention':     ('concept', 'leg',      None,      'sys_far_guard,sys_mid_guard,sys_close_guard'),
    'pressure':            ('concept', 'body',     None,      'sys_side_control,sys_mount'),
    'weight-distribution': ('concept', 'body',     None,      'sys_side_control,sys_mount,sys_kob'),
    'guard-passing':       ('pass',    'body',     None,      'sys_far_guard,sys_side_control'),

    # ── POSITIONS ──
    # Close guard
    'closed-guard':        ('pin',     'leg',      None,      'sys_close_guard'),
    'rubber-guard':        ('pin',     'leg',      None,      'sys_close_guard'),
    'worm-guard':          ('pin',     'leg',      None,      'sys_close_guard'),
    # Mid guard
    'half-guard':          ('pin',     'leg',      None,      'sys_mid_guard'),
    'deep-half-guard':     ('pin',     'leg',      None,      'sys_mid_guard'),
    'z-guard':             ('pin',     'leg',      None,      'sys_mid_guard'),
    'butterfly-guard':     ('pin',     'leg',      None,      'sys_mid_guard,sys_far_guard'),
    # Far guard
    'de-la-riva-guard':    ('hook',    'leg',      'outer',   'sys_far_guard'),
    'reverse-de-la-riva':  ('hook',    'leg',      'inner',   'sys_far_guard'),
    'spider-guard':        ('pin',     'leg',      None,      'sys_far_guard'),
    'x-guard':             ('hook',    'leg',      'cross',   'sys_far_guard'),
    'lasso-guard':         ('entanglement', 'leg', None,      'sys_far_guard'),
    'single-leg-x':        ('hook',    'leg',      None,      'sys_leg_entangle'),
    # Leg entanglements
    'ashi-garami':         ('entanglement', 'leg', None,      'sys_leg_entangle'),
    'inside-sankaku':      ('entanglement', 'leg', 'inner',   'sys_leg_entangle'),
    'fifty-fifty':         ('entanglement', 'leg', None,      'sys_leg_entangle'),
    'outside-ashi':        ('entanglement', 'leg', 'outer',   'sys_leg_entangle'),
    'cross-ashi':          ('entanglement', 'leg', 'cross',   'sys_leg_entangle'),
    # Dominant positions
    'side-control':        ('pin',     'body',     'side',    'sys_side_control'),
    'north-south':         ('pin',     'body',     'forward', 'sys_side_control'),
    'kesa-gatame':         ('pin',     'body',     'side',    'sys_side_control'),
    'reverse-kesa-gatame': ('pin',     'body',     'rear',    'sys_side_control'),
    'double-under-side-control': ('pin','body',    'side',    'sys_side_control'),
    'reverse-side-control':('pin',     'body',     'rear',    'sys_side_control'),
    'shoulder-pressure':   ('pin',     'shoulder', 'cross',   'sys_side_control'),
    'mount':               ('pin',     'body',     None,      'sys_mount'),
    'knee-on-belly':       ('pin',     'body',     None,      'sys_kob'),
    'back-control':        ('pin',     'body',     'rear',    'sys_back_control'),
    'turtle-position':     ('pin',     'body',     'rear',    'sys_back_control'),

    # ── UPPER BODY TAKEDOWNS ──
    'osoto-gari':          ('reap',    'leg',      'major',   'sys_upper_td'),   # Major Outer Reap
    'seoi-nage':           ('throw',   'shoulder', 'forward', 'sys_upper_td'),   # Shoulder Throw
    'uchi-mata':           ('throw',   'leg',      'inner',   'sys_upper_td'),   # Inner Thigh Throw
    'snap-down':           ('drop',    'neck',     'forward', 'sys_upper_td,sys_back_control'),
    'arm-drag':            ('hook',    'arm',      None,      'sys_upper_td,sys_back_control'),

    # ── LOWER BODY TAKEDOWNS ──
    'double-leg-takedown': ('throw',   'leg',      None,      'sys_lower_td'),
    'single-leg-takedown': ('throw',   'leg',      None,      'sys_lower_td'),
    'ankle-pick':          ('hook',    'ankle',    None,      'sys_lower_td'),
    'high-crotch':         ('throw',   'leg',      None,      'sys_lower_td'),

    # ── SWEEPS (polarity flips) ──
    'scissor-sweep':       ('sweep',   'body',     'cross',   'sys_close_guard,sys_mount'),
    'hip-bump-sweep':      ('sweep',   'body',     'forward', 'sys_close_guard,sys_mount'),
    'flower-sweep':        ('sweep',   'body',     None,      'sys_close_guard,sys_mount'),
    'tripod-sweep':        ('sweep',   'leg',      None,      'sys_far_guard,sys_side_control'),
    'berimbolo':           ('sweep',   'body',     'rear',    'sys_far_guard,sys_back_control'),

    # ── PASSES (distance compressions) ──
    'toreando-pass':       ('pass',    'leg',      'outer',   'sys_far_guard,sys_side_control'),
    'knee-slice-pass':     ('pass',    'leg',      'cross',   'sys_mid_guard,sys_side_control'),
    'leg-drag-pass':       ('pass',    'leg',      'outer',   'sys_far_guard,sys_side_control,sys_back_control'),
    'body-lock-pass':      ('pass',    'body',     None,      'sys_close_guard,sys_mid_guard,sys_side_control'),

    # ── SUBMISSIONS: CHOKES (Jime) ──
    'triangle-choke':      ('choke',   'neck',     'triangle','sys_close_guard'),
    'guillotine':          ('choke',   'neck',     'forward', 'sys_close_guard,sys_standing,sys_front_headlock'),
    'darce-choke':         ('choke',   'neck',     'side',    'sys_front_headlock,sys_side_control,sys_mid_guard'),
    'anaconda-choke':      ('choke',   'neck',     'forward', 'sys_front_headlock,sys_side_control'),
    'ezekiel-choke':       ('choke',   'neck',     'cross',   'sys_mount,sys_close_guard'),
    'north-south-choke':   ('choke',   'neck',     'forward', 'sys_side_control'),
    'cross-collar-choke':  ('choke',   'neck',     'cross',   'sys_mount,sys_close_guard'),
    'rear-naked-choke':    ('choke',   'neck',     'rear',    'sys_back_control'),
    'bow-and-arrow-choke': ('choke',   'neck',     'rear',    'sys_back_control'),
    'buggy-choke':         ('choke',   'neck',     'side',    'sys_side_control'),
    'arm-triangle':        ('choke',   'neck',     'side',    'sys_side_control,sys_mount'),

    # ── SUBMISSIONS: LOCKS (Gatame) ──
    'armbar':              ('lock',    'arm',      'cross',   'sys_close_guard,sys_mount'),
    'kneebar':             ('lock',    'knee',     None,      'sys_leg_entangle'),
    'straight-ankle-lock': ('lock',    'ankle',    None,      'sys_leg_entangle'),

    # ── SUBMISSIONS: ENTANGLEMENTS (Garami) ──
    'kimura':              ('entanglement', 'shoulder', 'rear', 'sys_side_control,sys_close_guard'),
    'americana':           ('entanglement', 'shoulder', 'forward', 'sys_mount,sys_side_control'),
    'omoplata':            ('entanglement', 'shoulder', None,  'sys_close_guard'),
    'heel-hook':           ('entanglement', 'knee',     None,  'sys_leg_entangle'),
    'toe-hold':            ('entanglement', 'ankle',    None,  'sys_leg_entangle'),
    'wrist-lock':          ('entanglement', 'wrist',    None,  'sys_mount,sys_close_guard'),

    # ── SUBMISSIONS: COMPRESSIONS ──
    'calf-slicer':         ('compression', 'leg',     None,   'sys_leg_entangle'),
}


def run():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verify columns exist
    cursor.execute("PRAGMA table_info(articles)")
    cols = {row[1] for row in cursor.fetchall()}
    if 'mechanism' not in cols:
        print("[ERROR] taxonomy columns not present. Run migrate_taxonomy.py first.")
        sys.exit(1)

    updated = 0
    missing = []
    for slug, (mechanism, target, spatial, graph_tier) in TAXONOMY.items():
        taxonomy_complete = 1 if (mechanism and graph_tier) else 0
        cursor.execute("""
            UPDATE articles
            SET mechanism = ?, target = ?, spatial_qualifier = ?,
                graph_tier = ?, taxonomy_complete = ?
            WHERE slug = ?
        """, (mechanism, target, spatial, graph_tier, taxonomy_complete, slug))
        if cursor.rowcount > 0:
            updated += 1
        else:
            missing.append(slug)

    conn.commit()
    conn.close()

    print(f"[OK] Updated taxonomy on {updated} articles.")
    if missing:
        print(f"[WARN] {len(missing)} slugs not found in DB: {', '.join(missing[:10])}{'...' if len(missing) > 10 else ''}")
    print("[DONE]")


if __name__ == '__main__':
    run()

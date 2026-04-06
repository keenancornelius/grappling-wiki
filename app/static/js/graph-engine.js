/**
 * GrapplingWiki 3D Knowledge Graph Engine
 * Interactive neural point-cloud with 3D rotation, perspective projection.
 * Rendered on Canvas 2D for performance. White / steel-blue / silver palette.
 *
 * Usage:
 *   GWGraph.init(canvasId, tooltipId, articles, options)
 *
 * Options:
 *   mode: 'full' | 'home' | 'article'
 *   focusSlug: null | 'article-slug'
 *   height: number | null
 *   interactive: true | false
 *   particleCount: number
 *   onNodeClick: function(slug) {}
 */
var GWGraph = (function() {
  'use strict';

  // Track active instances to prevent duplicate draw loops
  var activeInstances = {};

  // ── Palette: complementary cool tones anchored to white/blue/silver ──
  // MECHANISM-DRIVEN: every node is colored by its mechanism field.
  // Category colors are fallbacks for articles without taxonomy data.
  var C = {
    // Core
    system:      { r: 74,  g: 158, b: 255 },   // steel blue — system/structural nodes
    silver:      { r: 192, g: 192, b: 192 },   // silver — labels, dimmed elements
    grid:        { r: 74,  g: 158, b: 255 },   // blue grid lines

    // ── Mechanism colors — PRIMARY coloring for all nodes ──
    // Submissions (force vector types)
    mech_choke:        { r: 190, g: 100, b: 100 },   // desaturated crimson — blood/air restriction
    mech_lock:         { r: 210, g: 140, b: 110 },   // warm coral — hyperextension (armbar, kneebar)
    mech_entanglement: { r: 200, g: 175, b: 100 },   // amber — joint rotation (kimura, heel hook)
    mech_compression:  { r: 100, g: 180, b: 175 },   // cool teal — crushing tissue (calf slicer)
    // Positional control
    mech_pin:          { r: 160, g: 140, b: 220 },   // muted lavender — holding positions (mount, side control)
    mech_hook:         { r: 110, g: 190, b: 180 },   // warm teal — hooking control (DLR, arm drag)
    // Transitions
    mech_throw:        { r: 100, g: 150, b: 220 },   // steel blue — throwing (seoi nage, uchi mata)
    mech_reap:         { r: 140, g: 130, b: 210 },   // blue-violet — reaping (osoto gari)
    mech_sweep:        { r: 120, g: 210, b: 190 },   // seafoam — polarity flips (scissor sweep)
    mech_pass:         { r: 100, g: 195, b: 140 },   // cool green — distance compressions (toreando)
    mech_drop:         { r: 130, g: 155, b: 195 },   // slate blue — snap downs, level drops
    mech_wheel:        { r: 150, g: 170, b: 200 },   // dusty blue — wheel/rotational throws
    // Concepts
    mech_concept:      { r: 200, g: 195, b: 150 },   // warm silver — principles and strategies

    // ── Category fallbacks — used when mechanism is not set ──
    technique:   { r: 120, g: 210, b: 190 },   // seafoam
    position:    { r: 160, g: 140, b: 220 },   // muted lavender
    concept:     { r: 200, g: 195, b: 150 },   // warm silver
    style:       { r: 130, g: 195, b: 210 },   // ice blue
    glossary:    { r: 170, g: 170, b: 180 },   // cool gray

    // ── Force vector colors — kept for FORCE_VECTORS lookup compatibility ──
    fv_arterial:     { r: 190, g: 100, b: 100 },
    fv_extension:    { r: 210, g: 140, b: 110 },
    fv_torsion:      { r: 200, g: 175, b: 100 },
    fv_compression:  { r: 100, g: 180, b: 175 },
  };

  // ── Excluded categories (not mapped in the graph) ──
  var EXCLUDED_CATEGORIES = ['person', 'competition', 'style'];

  // ══════════════════════════════════════════════════════════
  // ── CONCENTRIC SPHERE MODEL (Inside-Out Option Expansion) ──
  // ══════════════════════════════════════════════════════════
  //
  // The graph is organized as concentric spheres radiating outward:
  //
  //   INNERMOST  = Standing (core — maximum optionality, everything starts here)
  //   SHELL 1    = Takedowns (first actions from standing)
  //   SHELL 2    = Guards + Front Headlock (where the fight goes to ground)
  //   SHELL 3    = Dominant Positions (passed guard / control achieved)
  //   OUTERMOST  = Submissions (terminal endpoints — the fight ends here)
  //
  // Angular position on each sphere encodes:
  //   theta (horizontal) = guard distance spectrum (close→far) / logical grouping
  //   phi (vertical)     = spread within tier
  //
  // System nodes are INVISIBLE structural anchors — they define where
  // article nodes cluster on each sphere but are not drawn.
  //
  // Sweeps = polarity flips (edges between guard shell and dominant shell).
  // Passes = distance compressions (edges from guard shell → dominant shell).
  // ──────────────────────────────────────────────────────────

  // Tier → sphere radius. Inside-out: standing smallest, submissions largest.
  var TIER_RADII = { 0: 60, 1: 140, 2: 230, 3: 310, sub: 400 };

  // Convert spherical coordinates to Cartesian
  // theta = horizontal angle (longitude), phi = polar angle from top (0=north pole)
  function spherePos(R, theta, phi) {
    return {
      x: R * Math.sin(phi) * Math.cos(theta),
      y: -R * Math.cos(phi),
      z: R * Math.sin(phi) * Math.sin(theta)
    };
  }

  var SYSTEM_NODES = [
    // ── Tier 0: Standing — innermost core ──
    // Small sphere, near north pole so it sits visually at center-top
    { id: 'sys_standing', label: 'Standing\nNeutral', tier: 0, theta: 0, phi: 1.2 },

    // ── Tier 1: Takedowns — second shell ──
    { id: 'sys_upper_td', label: 'Upper Body\nTakedowns', tier: 1, theta: -0.9, phi: 1.0 },
    { id: 'sys_lower_td', label: 'Lower Body\nTakedowns', tier: 1, theta:  0.9, phi: 1.0 },

    // ── Tier 2: Guards + Front Headlock — third shell ──
    // Theta spread encodes guard distance: close (left) → far (right)
    { id: 'sys_close_guard',    label: 'Close Distance\nGuards', tier: 2, theta: -2.2, phi: 1.57 },
    { id: 'sys_mid_guard',      label: 'Mid Distance\nGuards',   tier: 2, theta: -1.1, phi: 1.57 },
    { id: 'sys_leg_entangle',   label: 'Leg\nEntanglements',     tier: 2, theta: -0.1, phi: 1.4 },
    { id: 'sys_far_guard',      label: 'Far Distance\nGuards',   tier: 2, theta:  0.9, phi: 1.57 },
    { id: 'sys_front_headlock', label: 'Front\nHeadlock',        tier: 2, theta:  2.0, phi: 1.57 },

    // ── Tier 3: Dominant Positions — fourth shell ──
    { id: 'sys_side_control', label: 'Side\nControl',  tier: 3, theta: -1.5, phi: 1.8 },
    { id: 'sys_mount',        label: 'Mount',          tier: 3, theta: -0.4, phi: 1.8 },
    { id: 'sys_kob',          label: 'Knee on\nBelly', tier: 3, theta:  0.6, phi: 1.8 },
    { id: 'sys_back_control', label: 'Back\nControl',  tier: 3, theta:  1.5, phi: 1.8 },

    // Submissions orbit on the outermost shell (TIER_RADII.sub).
    // They are article nodes, not system nodes.
  ];

  var SYSTEM_EDGES = [
    // ── Standing → takedowns ──
    ['sys_standing', 'sys_upper_td'],
    ['sys_standing', 'sys_lower_td'],

    // ── Standing ↔ far guard (guard pull / wrestle-up) ──
    ['sys_standing', 'sys_far_guard'],        // guard pull → open guard
    ['sys_far_guard', 'sys_standing'],        // wrestle-up → back to feet

    // ── Upper body TDs → positions ──
    ['sys_upper_td', 'sys_side_control'],     // throw → land in side control
    ['sys_upper_td', 'sys_back_control'],     // snap down → back exposure
    ['sys_upper_td', 'sys_close_guard'],      // failed throw → land in guard
    ['sys_upper_td', 'sys_mid_guard'],        // sprawl → half guard

    // ── Lower body TDs → positions ──
    ['sys_lower_td', 'sys_side_control'],     // double leg → pass to side control
    ['sys_lower_td', 'sys_mid_guard'],        // single leg → land in half guard
    ['sys_lower_td', 'sys_far_guard'],        // guard pull → open guard
    ['sys_lower_td', 'sys_close_guard'],      // takedown → closed guard
    ['sys_lower_td', 'sys_leg_entangle'],     // imanari roll, failed shot → leg entangle

    // ── Guard transitions along X spectrum (openness) ──
    // Moving right = opening guard, moving left = closing guard
    ['sys_close_guard', 'sys_mid_guard'],     // open up from closed → half
    ['sys_mid_guard', 'sys_leg_entangle'],    // half guard → leg entangle
    ['sys_mid_guard', 'sys_far_guard'],       // half → open guard (recover)
    ['sys_leg_entangle', 'sys_far_guard'],    // disengage legs → open guard
    ['sys_far_guard', 'sys_mid_guard'],       // opponent closes distance → half
    ['sys_close_guard', 'sys_leg_entangle'],  // closed guard → leg entangle entry

    // ── Guard → passed (passes drop DOWN on Y) ──
    ['sys_far_guard', 'sys_side_control'],    // pass: far → past guard
    ['sys_mid_guard', 'sys_side_control'],    // pass: mid → past guard
    ['sys_close_guard', 'sys_side_control'],  // pass: close → past guard

    // ── Dominant position transitions ──
    ['sys_side_control', 'sys_mount'],        // advance
    ['sys_side_control', 'sys_kob'],          // advance
    ['sys_side_control', 'sys_back_control'], // take back from side
    ['sys_mount', 'sys_back_control'],        // take back from mount
    ['sys_kob', 'sys_mount'],                 // advance KOB → mount

    // ── Back control access from guards (berimbolo, etc.) ──
    ['sys_far_guard', 'sys_back_control'],
    ['sys_mid_guard', 'sys_back_control'],

    // ── Front headlock — face-to-back control zone ──
    // Entries: snap down from standing, sprawl on shots, failed clinch
    ['sys_standing', 'sys_front_headlock'],    // snap down → front headlock
    ['sys_lower_td', 'sys_front_headlock'],    // sprawl on shot → front headlock
    ['sys_upper_td', 'sys_front_headlock'],    // clinch fight → front headlock
    // Exits: advance to dominant positions
    ['sys_front_headlock', 'sys_side_control'], // snap to mat → side control
    ['sys_front_headlock', 'sys_back_control'], // spin behind → back control
    // Recovery: opponent pulls guard from front headlock
    ['sys_front_headlock', 'sys_close_guard'],  // opponent pulls guard
    ['sys_front_headlock', 'sys_mid_guard'],    // scramble → half guard

  ];

  // ── Article → Combat Zone mapping ──
  // Each article connects to the Combat Zone(s) where it lives in the tree.
  // Submissions connect to every position they're available from.
  // Sweeps are polarity flips: connect guard origin → dominant position destination.
  // Passes connect guard → dominant position (distance compression).
  var ARTICLE_CONNECTIONS = {
    // ══════════════════════════════════════════════════════════
    // STANDING CONCEPTS
    // ══════════════════════════════════════════════════════════
    'grip-fighting':        ['sys_standing'],
    'underhooks':           ['sys_standing', 'sys_upper_td'],
    'base-and-posture':     ['sys_standing'],
    'inside-position':      ['sys_standing', 'sys_mid_guard'],
    'chain-wrestling':      ['sys_standing', 'sys_upper_td', 'sys_lower_td'],

    // ══════════════════════════════════════════════════════════
    // UPPER BODY TAKEDOWNS (throws, clinch takedowns)
    // ══════════════════════════════════════════════════════════
    'osoto-gari':           ['sys_upper_td'],
    'seoi-nage':            ['sys_upper_td'],
    'uchi-mata':            ['sys_upper_td'],
    'snap-down':            ['sys_upper_td', 'sys_back_control'],
    'arm-drag':             ['sys_upper_td', 'sys_back_control'],

    // ══════════════════════════════════════════════════════════
    // LOWER BODY TAKEDOWNS (shots, leg attacks)
    // ══════════════════════════════════════════════════════════
    'double-leg-takedown':  ['sys_lower_td'],
    'single-leg-takedown':  ['sys_lower_td'],
    'ankle-pick':           ['sys_lower_td'],
    'high-crotch':          ['sys_lower_td'],

    // ══════════════════════════════════════════════════════════
    // FAR DISTANCE GUARDS
    // ══════════════════════════════════════════════════════════
    'de-la-riva-guard':     ['sys_far_guard'],
    'spider-guard':         ['sys_far_guard'],
    'x-guard':              ['sys_far_guard'],
    'lasso-guard':          ['sys_far_guard'],
    'reverse-de-la-riva':   ['sys_far_guard'],

    // ══════════════════════════════════════════════════════════
    // MID DISTANCE GUARDS
    // ══════════════════════════════════════════════════════════
    'half-guard':           ['sys_mid_guard'],
    'butterfly-guard':      ['sys_mid_guard', 'sys_far_guard'],
    'z-guard':              ['sys_mid_guard'],
    'deep-half-guard':      ['sys_mid_guard'],

    // ══════════════════════════════════════════════════════════
    // CLOSE DISTANCE GUARDS
    // ══════════════════════════════════════════════════════════
    'closed-guard':         ['sys_close_guard'],
    'rubber-guard':         ['sys_close_guard'],
    'worm-guard':           ['sys_close_guard'],

    // ══════════════════════════════════════════════════════════
    // LEG ENTANGLEMENT POSITIONS (the leg lock game)
    // These are guard positions where control is through leg-on-leg.
    // ══════════════════════════════════════════════════════════
    'single-leg-x':         ['sys_leg_entangle'],
    'ashi-garami':          ['sys_leg_entangle'],
    'inside-sankaku':       ['sys_leg_entangle'],
    'fifty-fifty':          ['sys_leg_entangle'],
    'outside-ashi':         ['sys_leg_entangle'],
    'cross-ashi':           ['sys_leg_entangle'],

    // ══════════════════════════════════════════════════════════
    // DOMINANT POSITIONS
    // ══════════════════════════════════════════════════════════
    'side-control':         ['sys_side_control'],
    'north-south':          ['sys_side_control'],
    'kesa-gatame':          ['sys_side_control'],
    'reverse-kesa-gatame':  ['sys_side_control'],
    'double-under-side-control': ['sys_side_control'],
    'reverse-side-control': ['sys_side_control'],
    'shoulder-pressure':    ['sys_side_control'],
    'mount':                ['sys_mount'],
    'knee-on-belly':        ['sys_kob'],
    'back-control':         ['sys_back_control'],
    'turtle-position':      ['sys_back_control'],

    // ══════════════════════════════════════════════════════════
    // POLARITY FLIPS (sweeps) — guard origin → position achieved
    // ══════════════════════════════════════════════════════════
    'scissor-sweep':        ['sys_close_guard', 'sys_mount'],
    'hip-bump-sweep':       ['sys_close_guard', 'sys_mount'],
    'flower-sweep':         ['sys_close_guard', 'sys_mount'],
    'tripod-sweep':         ['sys_far_guard', 'sys_side_control'],
    'berimbolo':            ['sys_far_guard', 'sys_back_control'],

    // ══════════════════════════════════════════════════════════
    // DISTANCE COMPRESSIONS (passes) — guard → past guard
    // ══════════════════════════════════════════════════════════
    'guard-passing':        ['sys_far_guard', 'sys_side_control'],
    'toreando-pass':        ['sys_far_guard', 'sys_side_control'],
    'knee-slice-pass':      ['sys_mid_guard', 'sys_side_control'],
    'leg-drag-pass':        ['sys_far_guard', 'sys_side_control', 'sys_back_control'],
    'body-lock-pass':       ['sys_close_guard', 'sys_mid_guard', 'sys_side_control'],

    // ══════════════════════════════════════════════════════════
    // CONCEPTS (connect to where the concept is most contested)
    // ══════════════════════════════════════════════════════════
    'frames-and-framing':   ['sys_close_guard', 'sys_side_control'],
    'shrimping':            ['sys_close_guard', 'sys_side_control'],
    'guard-retention':      ['sys_far_guard', 'sys_mid_guard', 'sys_close_guard'],
    'pressure':             ['sys_side_control', 'sys_mount'],
    'weight-distribution':  ['sys_side_control', 'sys_mount', 'sys_kob'],

    // ══════════════════════════════════════════════════════════
    // SUBMISSIONS — connect to the positions they're available from.
    // These are terminal endpoints (green technique nodes).
    // Lightning travels to these as final destinations.
    // ══════════════════════════════════════════════════════════

    // Guard submissions
    'triangle-choke':       ['sys_close_guard'],
    'omoplata':             ['sys_close_guard'],
    'guillotine':           ['sys_close_guard', 'sys_standing', 'sys_front_headlock'],
    'armbar':               ['sys_close_guard', 'sys_mount'],
    'buggy-choke':          ['sys_side_control'],

    // Leg lock submissions (from leg entanglements)
    'heel-hook':            ['sys_leg_entangle'],
    'straight-ankle-lock':  ['sys_leg_entangle'],
    'kneebar':              ['sys_leg_entangle'],
    'toe-hold':             ['sys_leg_entangle'],
    'calf-slicer':          ['sys_leg_entangle'],

    // Front headlock submissions
    'darce-choke':          ['sys_front_headlock', 'sys_side_control', 'sys_mid_guard'],
    'anaconda-choke':       ['sys_front_headlock', 'sys_side_control'],
    'peruvian-necktie':     ['sys_front_headlock'],
    'japanese-necktie':     ['sys_front_headlock'],

    // Top submissions (from dominant positions)
    'kimura':               ['sys_side_control', 'sys_close_guard'],
    'americana':            ['sys_mount', 'sys_side_control'],
    'ezekiel-choke':        ['sys_mount', 'sys_close_guard'],
    'north-south-choke':    ['sys_side_control'],
    'arm-triangle':         ['sys_side_control', 'sys_mount'],
    'cross-collar-choke':   ['sys_mount', 'sys_close_guard'],
    'wrist-lock':           ['sys_mount', 'sys_close_guard'],

    // Back submissions
    'rear-naked-choke':     ['sys_back_control'],
    'bow-and-arrow-choke':  ['sys_back_control'],
  };

  // ── Submission slugs — lightning endpoints ──
  // Every submission article slug. Lightning bolts travel down
  // the tree and terminate at these green nodes with a flash.
  var SUBMISSION_SLUGS = [
    'triangle-choke', 'omoplata', 'guillotine', 'armbar', 'buggy-choke',
    'heel-hook', 'straight-ankle-lock', 'kneebar', 'toe-hold', 'calf-slicer',
    'kimura', 'americana', 'darce-choke', 'anaconda-choke', 'ezekiel-choke',
    'north-south-choke', 'arm-triangle', 'cross-collar-choke', 'wrist-lock',
    'rear-naked-choke', 'bow-and-arrow-choke',
    'peruvian-necktie', 'japanese-necktie',
  ];

  // ── Force vector classification ──
  // Determines submission node color. Each force vector type
  // maps to a distinct hue so you can read the finish mechanic at a glance.
  //
  //   arterial    = chokes (blood/air restriction)
  //   extension   = hyperextension of a joint (armbar, kneebar)
  //   torsion     = rotation of a joint (kimura, heel hook)
  //   compression = crushing tissue against bone (slicers, can opener)
  //
  var FORCE_VECTORS = {
    // Arterial compression (chokes)
    'triangle-choke':       'arterial',
    'guillotine':           'arterial',
    'darce-choke':          'arterial',
    'anaconda-choke':       'arterial',
    'ezekiel-choke':        'arterial',
    'north-south-choke':    'arterial',
    'cross-collar-choke':   'arterial',
    'rear-naked-choke':     'arterial',
    'bow-and-arrow-choke':  'arterial',
    'buggy-choke':          'arterial',
    'arm-triangle':         'arterial',
    'peruvian-necktie':     'arterial',
    'japanese-necktie':     'arterial',

    // Extension (hyperextension)
    'armbar':               'extension',
    'kneebar':              'extension',
    'straight-ankle-lock':  'extension',

    // Torsion (rotation)
    'kimura':               'torsion',
    'americana':            'torsion',
    'omoplata':             'torsion',
    'heel-hook':            'torsion',
    'toe-hold':             'torsion',
    'wrist-lock':           'torsion',

    // Compression / wedge
    'calf-slicer':          'compression',
  };

  function rgba(c, a) { return 'rgba(' + c.r + ',' + c.g + ',' + c.b + ',' + a + ')'; }

  // ══════════════════════════════════════════════════════════
  // ── 3D MATH ──
  // ══════════════════════════════════════════════════════════
  function rotateY(x, y, z, angle) {
    var c = Math.cos(angle), s = Math.sin(angle);
    return { x: x * c + z * s, y: y, z: -x * s + z * c };
  }
  function rotateX(x, y, z, angle) {
    var c = Math.cos(angle), s = Math.sin(angle);
    return { x: x, y: y * c - z * s, z: y * s + z * c };
  }

  // ══════════════════════════════════════════════════════════
  // ── BUILD GRAPH ──
  // ══════════════════════════════════════════════════════════
  function buildGraph(articles, opts) {
    var nodes = [], edges = [], nodeMap = {};
    var scale = opts.mode === 'article' ? 0.6 : 1;

    // System nodes — INVISIBLE structural anchors on concentric spheres.
    // Positions computed from spherical coordinates (tier → radius, theta/phi → angle).
    // These are not drawn but serve as gravity centers for article node placement.
    SYSTEM_NODES.forEach(function(sn) {
      var R = (TIER_RADII[sn.tier] || 200) * scale;
      var pos = spherePos(R, sn.theta, sn.phi);
      var node = {
        id: sn.id, label: sn.label,
        x: pos.x, y: pos.y, z: pos.z,
        radius: 0,       // invisible — no drawn dot
        color: C.system, type: 'system',
        slug: null, summary: null, category: null,
        tier: sn.tier, pulse: Math.random() * Math.PI * 2,
        dimmed: false, hidden: true,  // flag: skip during rendering
      };
      nodes.push(node); nodeMap[sn.id] = node;
    });

    // Filter out excluded categories
    var filtered = articles.filter(function(a) {
      var cat = (a.category || '').toLowerCase();
      return EXCLUDED_CATEGORIES.indexOf(cat) === -1;
    });

    // ── Article nodes on concentric spheres ──
    // Each article is placed on the sphere corresponding to its tier.
    // Submissions always go to the outermost sphere (TIER_RADII.sub).
    // Angular position is driven by:
    //   1. Parent system node(s) — gives a base direction on the sphere
    //   2. spatial_qualifier — shifts theta (inner→left, outer→right, etc.)
    //   3. target body part — shifts phi for sub-clustering within a region

    // Spatial qualifier → angular offsets on the sphere
    var SPATIAL_THETA = {
      'inner': -0.3, 'outer': 0.3, 'cross': 0.15, 'major': -0.2,
      'minor': 0.2, 'forward': 0, 'rear': 0, 'side': 0.25, 'triangle': -0.15,
    };
    var SPATIAL_PHI = {
      'forward': -0.2, 'rear': 0.2, 'cross': 0.1, 'triangle': -0.1,
    };

    // Target body part → phi offset for sub-clustering
    var TARGET_PHI = {
      'neck': -0.25, 'shoulder': -0.15, 'arm': -0.05,
      'wrist': 0.05, 'body': 0.12, 'hip': 0.18,
      'leg': 0.25, 'knee': 0.3, 'ankle': 0.35,
    };

    filtered.forEach(function(a) {
      var connections = ARTICLE_CONNECTIONS[a.slug];
      if (!connections && a.graphTier) {
        connections = a.graphTier.split(',').map(function(t) { return t.trim(); }).filter(Boolean);
      }

      var spatial = (a.spatial || '').toLowerCase();
      var target  = (a.target  || '').toLowerCase();
      var mech    = (a.mechanism || '').toLowerCase();

      // Determine if this is a submission (outermost shell)
      var isSub = SUBMISSION_SLUGS.indexOf(a.slug) !== -1;

      // Slug hash for deterministic spread
      var slugHash = 0;
      for (var si = 0; si < a.slug.length; si++) slugHash += a.slug.charCodeAt(si);

      var cx, cy, cz;

      if (connections && connections.length > 0) {
        // Find the average direction of connected system nodes
        var avgTheta = 0, avgPhi = 0, maxTier = 0, cnt = 0;
        connections.forEach(function(sid) {
          var sn = nodeMap[sid];
          if (!sn) return;
          // Recover the system node's theta/phi from SYSTEM_NODES
          for (var si2 = 0; si2 < SYSTEM_NODES.length; si2++) {
            if (SYSTEM_NODES[si2].id === sid) {
              avgTheta += SYSTEM_NODES[si2].theta;
              avgPhi += SYSTEM_NODES[si2].phi;
              if (SYSTEM_NODES[si2].tier > maxTier) maxTier = SYSTEM_NODES[si2].tier;
              cnt++;
              break;
            }
          }
        });
        if (cnt > 0) { avgTheta /= cnt; avgPhi /= cnt; }

        // Sphere radius: submissions go to outermost, others go to their tier's shell
        var R;
        if (isSub) {
          R = TIER_RADII.sub * scale;
        } else {
          R = (TIER_RADII[maxTier] || 230) * scale;
        }

        // Apply spatial qualifier offsets
        var thetaOff = SPATIAL_THETA[spatial] || 0;
        var phiOff = SPATIAL_PHI[spatial] || 0;

        // Apply target body part clustering
        phiOff += TARGET_PHI[target] || 0;

        // Per-node spread so nodes don't overlap
        var spread = ((slugHash % 53) / 53 - 0.5) * 0.5;  // ±0.25 rad
        var spreadPhi = ((slugHash % 37) / 37 - 0.5) * 0.3;

        var finalTheta = avgTheta + thetaOff + spread;
        var finalPhi = avgPhi + phiOff + spreadPhi;

        // Clamp phi to avoid poles (0.2 to 2.9)
        finalPhi = Math.max(0.2, Math.min(2.9, finalPhi));

        var pos = spherePos(R, finalTheta, finalPhi);
        cx = pos.x; cy = pos.y; cz = pos.z;
      } else {
        // No connections — scatter on outermost shell
        var fallbackTheta = (slugHash % 628) / 100;
        var fallbackPhi = 0.5 + ((slugHash % 200) / 200) * 2.0;
        var fallbackR = TIER_RADII.sub * scale;
        var pos2 = spherePos(fallbackR, fallbackTheta, fallbackPhi);
        cx = pos2.x; cy = pos2.y; cz = pos2.z;
      }

      // ── Mechanism-driven color ──
      var cat = (a.category || 'glossary').toLowerCase();
      var nodeColor = C[cat] || C.glossary;
      var fv = FORCE_VECTORS[a.slug];

      if (mech && C['mech_' + mech]) {
        nodeColor = C['mech_' + mech];
      }
      if (!fv && mech) {
        var mechToFv = {
          'choke': 'arterial', 'lock': 'extension',
          'entanglement': 'torsion', 'compression': 'compression'
        };
        fv = mechToFv[mech] || null;
      }
      if (fv) {
        nodeColor = C['fv_' + fv] || nodeColor;
      }

      var node = {
        id: 'art_' + a.slug, label: a.title,
        x: cx, y: cy, z: cz,
        radius: (isSub ? 4.5 : 3.5) * scale,
        color: nodeColor, type: 'article',
        slug: a.slug, summary: a.summary, category: a.category,
        mechanism: mech || null, target: target || null, spatial: spatial || null,
        forceVector: fv || null,
        tags: a.tags, pulse: Math.random() * Math.PI * 2,
        dimmed: false,
      };
      nodes.push(node); nodeMap['art_' + a.slug] = node;
    });

    // System edges
    SYSTEM_EDGES.forEach(function(e) {
      if (nodeMap[e[0]] && nodeMap[e[1]])
        edges.push({ from: nodeMap[e[0]], to: nodeMap[e[1]], type: 'system', strength: 1 });
    });

    // Article-to-system edges
    filtered.forEach(function(a) {
      var conns = ARTICLE_CONNECTIONS[a.slug];
      if (!conns) return;
      var artNode = nodeMap['art_' + a.slug];
      if (!artNode) return;
      conns.forEach(function(sid) {
        var sn = nodeMap[sid];
        if (sn) edges.push({ from: artNode, to: sn, type: 'article', strength: 0.5 });
      });
    });

    // Peer edges (shared system connections)
    var slugs = filtered.map(function(a) { return a.slug; });
    for (var i = 0; i < slugs.length; i++) {
      for (var j = i + 1; j < slugs.length; j++) {
        var cA = ARTICLE_CONNECTIONS[slugs[i]];
        var cB = ARTICLE_CONNECTIONS[slugs[j]];
        if (!cA || !cB) continue;
        var shared = cA.filter(function(c) { return cB.indexOf(c) !== -1; });
        if (shared.length > 0) {
          var nA = nodeMap['art_' + slugs[i]];
          var nB = nodeMap['art_' + slugs[j]];
          if (nA && nB) edges.push({ from: nA, to: nB, type: 'peer', strength: shared.length * 0.15 });
        }
      }
    }

    // Center X and Z only — preserve Y for tree vertical structure
    if (nodes.length > 0) {
      var cx = 0, cz = 0;
      nodes.forEach(function(n) { cx += n.x; cz += n.z; });
      cx /= nodes.length; cz /= nodes.length;
      nodes.forEach(function(n) { n.x -= cx; n.z -= cz; });
    }

    return { nodes: nodes, edges: edges, nodeMap: nodeMap };
  }

  // ── Focus mode ──
  function applyFocus(graph, focusSlug) {
    if (!focusSlug) return null;
    var focusNode = graph.nodeMap['art_' + focusSlug];
    if (!focusNode) return null;

    var connectedIds = {};
    connectedIds[focusNode.id] = true;
    var artConns = ARTICLE_CONNECTIONS[focusSlug] || [];
    artConns.forEach(function(sid) { connectedIds[sid] = true; });
    graph.edges.forEach(function(e) {
      if (e.from === focusNode) connectedIds[e.to.id] = true;
      if (e.to === focusNode) connectedIds[e.from.id] = true;
    });

    graph.nodes.forEach(function(n) {
      n.dimmed = !connectedIds[n.id];
    });

    focusNode.radius = 12;
    graph.nodes.forEach(function(n) {
      if (!n.dimmed && n !== focusNode && n.type !== 'system') {
        n.radius = Math.max(n.radius, 5);
      }
    });

    return focusNode;
  }

  // ══════════════════════════════════════════════════════════
  // ── INIT ──
  // ══════════════════════════════════════════════════════════
  function init(canvasId, tooltipId, articles, opts) {
    // Cancel any existing draw loop on this canvas (survives script re-execution)
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;
    if (canvas._gwInstance) {
      canvas._gwInstance.cancelled = true;
    }
    var instance = { cancelled: false };
    canvas._gwInstance = instance;

    opts = opts || {};
    opts.mode = opts.mode || 'full';
    opts.focusSlug = opts.focusSlug || null;
    opts.particleCount = opts.particleCount || (opts.mode === 'article' ? 12 : 35);
    opts.interactive = opts.interactive !== false;
    opts.onNodeClick = opts.onNodeClick || function(slug) { window.location.href = '/wiki/' + slug; };

    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var container = canvas.parentElement;
    var W, H;

    function resize() {
      var rect = container.getBoundingClientRect();
      W = rect.width || container.offsetWidth || 800;
      H = opts.height || rect.height || 500;
      if (W < 10) W = 800; // Fallback if container not yet laid out
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = W + 'px';
      canvas.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    // Build & filter
    var graph = buildGraph(articles, opts);
    var nodes = graph.nodes, edges = graph.edges;

    // Focus
    var focusNode = opts.focusSlug ? applyFocus(graph, opts.focusSlug) : null;

    // Camera: 3D rotation angles + zoom
    var cam = {
      rotY: 0.3, rotX: -0.1,                      // current rotation — subtle tilt for 3D depth
      targetRotY: 0.3, targetRotX: -0.1,
      zoom: 1.05, targetZoom: 1.05,
      perspective: 800,                           // perspective distance
      panX: 0, panY: -30, targetPanX: 0, targetPanY: -30,
      autoRotate: true,                             // always auto-rotate for 3D effect
    };

    if (focusNode) {
      cam.zoom = cam.targetZoom = opts.mode === 'article' ? 1.4 : 1.1;
    }

    // ── Project 3D → 2D ──
    function project(x, y, z) {
      // Apply camera rotation
      var p = rotateY(x, y, z, cam.rotY);
      p = rotateX(p.x, p.y, p.z, cam.rotX);
      // Perspective
      var d = cam.perspective + p.z;
      if (d < 50) d = 50;
      var scale = cam.perspective / d * cam.zoom;
      return {
        x: p.x * scale + W / 2 + cam.panX,
        y: p.y * scale + H / 2 + cam.panY,
        scale: scale,
        depth: p.z,
      };
    }

    // ── Unproject screen → ray for hit testing ──
    function findNodeAt(sx, sy) {
      var rect = canvas.getBoundingClientRect();
      var lx = sx - rect.left, ly = sy - rect.top;
      var best = null, bestDist = Infinity;
      for (var i = 0; i < nodes.length; i++) {
        var p = project(nodes[i].x, nodes[i].y, nodes[i].z);
        var dx = p.x - lx, dy = p.y - ly;
        var dist = Math.sqrt(dx * dx + dy * dy);
        var hitR = (nodes[i].radius * p.scale) + 8;
        if (dist < hitR && dist < bestDist) { best = nodes[i]; bestDist = dist; }
      }
      return best;
    }

    // Particles
    var particles = [];
    if (edges.length > 0) {
      for (var p = 0; p < opts.particleCount; p++) {
        particles.push({
          edge: edges[Math.floor(Math.random() * edges.length)],
          t: Math.random(),
          speed: 0.002 + Math.random() * 0.003,
          reverse: Math.random() > 0.5,
        });
      }
    }

    // Tooltip
    var hoveredNode = null;
    var tooltip = tooltipId ? document.getElementById(tooltipId) : null;
    var ttTitle, ttSummary, ttCategory, ttHint;
    if (tooltip) {
      ttTitle = tooltip.querySelector('.graph-tooltip-title');
      ttSummary = tooltip.querySelector('.graph-tooltip-summary');
      ttCategory = tooltip.querySelector('.graph-tooltip-category');
      ttHint = tooltip.querySelector('.graph-tooltip-hint');
    }

    // ── Interaction ──
    var dragging = false, dragStart = { x: 0, y: 0 };

    canvas.addEventListener('mousemove', function(e) {
      if (dragging) return;
      var node = findNodeAt(e.clientX, e.clientY);
      hoveredNode = node;
      if (node && tooltip) {
        canvas.style.cursor = node.slug ? 'pointer' : 'default';
        ttTitle.textContent = node.label.replace(/\n/g, ' ');
        var catLabel = node.category || (node.type === 'system' ? 'Combat Zone' : '');
        // Build mechanism-driven label: "Spatial Target Mechanism" (e.g., "Cross Arm Lock")
        if (node.mechanism) {
          var mechLabels = {
            choke: 'Choke', lock: 'Lock', entanglement: 'Entanglement', compression: 'Compression',
            throw: 'Throw', reap: 'Reap', sweep: 'Sweep', pass: 'Pass', hook: 'Hook',
            drop: 'Drop', wheel: 'Wheel', pin: 'Pin', concept: 'Concept'
          };
          var parts = [];
          if (node.spatial) parts.push(node.spatial.charAt(0).toUpperCase() + node.spatial.slice(1));
          if (node.target) parts.push(node.target.charAt(0).toUpperCase() + node.target.slice(1));
          parts.push(mechLabels[node.mechanism] || node.mechanism.charAt(0).toUpperCase() + node.mechanism.slice(1));
          catLabel = parts.join(' ');
        } else if (node.forceVector) {
          var fvLabels = { arterial: 'Arterial', extension: 'Extension', torsion: 'Torsion', compression: 'Compression' };
          catLabel = (fvLabels[node.forceVector] || node.forceVector) + ' Submission';
        }
        ttCategory.textContent = catLabel;
        ttSummary.textContent = node.summary || '';
        if (ttHint) ttHint.style.display = node.slug ? '' : 'none';
        var tx = e.clientX + 16, ty = e.clientY - 10;
        if (tx + 290 > window.innerWidth) tx = e.clientX - 296;
        if (ty < 10) ty = 10;
        tooltip.style.left = tx + 'px'; tooltip.style.top = ty + 'px';
        tooltip.style.display = 'block';
        ttCategory.style.color = rgba(node.color, 1);
        tooltip.style.borderColor = rgba(C.system, 0.3);
      } else {
        canvas.style.cursor = opts.interactive ? 'grab' : 'default';
        if (tooltip) tooltip.style.display = 'none';
      }
    });

    canvas.addEventListener('mouseleave', function() {
      hoveredNode = null;
      if (tooltip) tooltip.style.display = 'none';
    });

    canvas.addEventListener('click', function(e) {
      if (dragging) return;
      var node = findNodeAt(e.clientX, e.clientY);
      if (editorMouseHandler && editorMouseHandler.onClick) {
        editorMouseHandler.onClick(e, node);
        return;
      }
      if (node && node.slug) opts.onNodeClick(node.slug);
    });

    if (opts.interactive) {
      canvas.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        var node = findNodeAt(e.clientX, e.clientY);
        if (editorMouseHandler && editorMouseHandler.onMouseDown) {
          editorMouseHandler.onMouseDown(e, node);
          return;
        }
        if (node) return;
        dragging = true;
        dragStart.x = e.clientX; dragStart.y = e.clientY;
        canvas.style.cursor = 'grabbing';
        cam.autoRotate = false;
      });
      window.addEventListener('mousemove', function(e) {
        if (editorMouseHandler && editorMouseHandler.onMouseMove) {
          editorMouseHandler.onMouseMove(e);
        }
        if (!dragging) return;
        var dx = e.clientX - dragStart.x;
        var dy = e.clientY - dragStart.y;
        cam.targetRotY += dx * 0.005;
        cam.targetRotX += dy * 0.003;
        // Clamp vertical rotation
        cam.targetRotX = Math.max(-1.2, Math.min(1.2, cam.targetRotX));
        dragStart.x = e.clientX; dragStart.y = e.clientY;
      });
      window.addEventListener('mouseup', function(e) {
        if (editorMouseHandler && editorMouseHandler.onMouseUp) {
          editorMouseHandler.onMouseUp(e);
        }
        if (dragging) { dragging = false; canvas.style.cursor = 'grab'; }
      });
      canvas.addEventListener('wheel', function(e) {
        e.preventDefault();
        var factor = e.deltaY > 0 ? 0.92 : 1.08;
        cam.targetZoom = Math.max(0.3, Math.min(3.5, cam.targetZoom * factor));
      }, { passive: false });
    }

    // ══════════════════════════════════════════════════════════
    // ── LIGHTNING / ELECTRICITY PATH SYSTEM ──
    // ══════════════════════════════════════════════════════════
    // Lightning travels DOWN the tree from sys_standing through
    // game states, then jumps to a green submission article node
    // as the terminal endpoint. Flash on arrival.

    // Build downward adjacency from SYSTEM_EDGES
    var adjDown = {};
    SYSTEM_EDGES.forEach(function(e) {
      var fromNode = graph.nodeMap[e[0]];
      var toNode = graph.nodeMap[e[1]];
      if (!fromNode || !toNode) return;
      if (toNode.tier > fromNode.tier || (toNode.tier === fromNode.tier && toNode.y > fromNode.y)) {
        if (!adjDown[e[0]]) adjDown[e[0]] = [];
        adjDown[e[0]].push(e[1]);
      }
    });

    // Build map of submission article IDs and which system nodes they connect to
    var subArticleIds = {};  // 'art_slug' → true
    var subBySystem = {};    // 'sys_xxx' → ['art_slug1', 'art_slug2', ...]
    SUBMISSION_SLUGS.forEach(function(slug) {
      var artId = 'art_' + slug;
      if (!graph.nodeMap[artId]) return; // article not in graph
      subArticleIds[artId] = true;
      var conns = ARTICLE_CONNECTIONS[slug] || [];
      conns.forEach(function(sysId) {
        if (!subBySystem[sysId]) subBySystem[sysId] = [];
        subBySystem[sysId].push(artId);
      });
    });

    // Add edges from system nodes → their connected submission articles
    // These are the final hops in lightning paths
    Object.keys(subBySystem).forEach(function(sysId) {
      if (!adjDown[sysId]) adjDown[sysId] = [];
      subBySystem[sysId].forEach(function(artId) {
        adjDown[sysId].push(artId);
      });
    });

    // Find all paths from sys_standing to submission article nodes via DFS
    var lightningPaths = [];
    function findPaths(current, path) {
      path.push(current);
      if (subArticleIds[current]) {
        lightningPaths.push(path.slice()); // clone — reached a submission
      }
      var children = adjDown[current] || [];
      for (var i = 0; i < children.length; i++) {
        if (path.indexOf(children[i]) === -1) { // no cycles
          findPaths(children[i], path);
        }
      }
      path.pop();
    }
    findPaths('sys_standing', []);

    // Active lightning bolts
    var lightningBolts = [];
    var lightningFlashes = []; // {nodeId, startTime, duration}
    var lightningTimer = 0;
    var lightningInterval = 1.2; // seconds between new bolts

    function spawnLightningBolt() {
      if (lightningPaths.length === 0) return;
      var pathIds = lightningPaths[Math.floor(Math.random() * lightningPaths.length)];
      // Build path of node references
      var pathNodes = [];
      for (var i = 0; i < pathIds.length; i++) {
        var n = graph.nodeMap[pathIds[i]];
        if (n) pathNodes.push(n);
      }
      if (pathNodes.length < 2) return;

      // Calculate total path length for consistent speed
      var totalLen = 0;
      for (var j = 1; j < pathNodes.length; j++) {
        var dx = pathNodes[j].x - pathNodes[j-1].x;
        var dy = pathNodes[j].y - pathNodes[j-1].y;
        var dz = pathNodes[j].z - pathNodes[j-1].z;
        totalLen += Math.sqrt(dx*dx + dy*dy + dz*dz);
      }

      lightningBolts.push({
        path: pathNodes,
        pathIds: pathIds,
        t: 0,                          // 0 = at start, 1 = at end
        speed: 0.008 + 0.003 / Math.max(1, pathNodes.length - 1), // ~2-3 seconds to traverse
        totalLen: totalLen,
        forkSeed: Math.random() * 100,  // for jagged offsets
        width: 1.5 + Math.random() * 1.5,
        opacity: 0.8 + Math.random() * 0.2,
      });
    }

    // ══════════════════════════════════════════════════════════
    // ── DRAW LOOP ──
    // ══════════════════════════════════════════════════════════
    var time = 0;
    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function draw() {
      if (instance.cancelled) return; // Stop if a newer init replaced us
      // Schedule next frame FIRST so the loop never dies on errors
      requestAnimationFrame(draw);
      time += 0.016;

      // Auto-rotate
      if (cam.autoRotate && !reducedMotion) {
        cam.targetRotY += 0.003;
      }

      // Smooth camera
      cam.rotY += (cam.targetRotY - cam.rotY) * 0.08;
      cam.rotX += (cam.targetRotX - cam.rotX) * 0.08;
      cam.zoom += (cam.targetZoom - cam.zoom) * 0.08;
      cam.panX += (cam.targetPanX - cam.panX) * 0.08;
      cam.panY += (cam.targetPanY - cam.panY) * 0.08;

      ctx.clearRect(0, 0, W, H);

      // ── Concentric sphere wireframes ──
      // Draw faint circle outlines for each tier's sphere to show the shell structure.
      // We draw equatorial rings (XZ plane) and a meridian ring (XY plane) for each tier.
      var tierKeys = [0, 1, 2, 3, 'sub'];
      var tierAlphas = { 0: 0.08, 1: 0.06, 2: 0.06, 3: 0.06, sub: 0.04 };
      var ringSegments = 64;
      for (var ti = 0; ti < tierKeys.length; ti++) {
        var tR = TIER_RADII[tierKeys[ti]] * scale;
        var tAlpha = tierAlphas[tierKeys[ti]];
        ctx.strokeStyle = rgba(C.grid, tAlpha);
        ctx.lineWidth = 0.6;

        // Equatorial ring (XZ plane, y=0)
        ctx.beginPath();
        for (var ri = 0; ri <= ringSegments; ri++) {
          var rAngle = (ri / ringSegments) * Math.PI * 2;
          var rp = project(Math.cos(rAngle) * tR, 0, Math.sin(rAngle) * tR);
          if (ri === 0) ctx.moveTo(rp.x, rp.y); else ctx.lineTo(rp.x, rp.y);
        }
        ctx.stroke();

        // Meridian ring (XY plane, z=0)
        ctx.beginPath();
        for (var ri2 = 0; ri2 <= ringSegments; ri2++) {
          var rAngle2 = (ri2 / ringSegments) * Math.PI * 2;
          var rp2 = project(Math.cos(rAngle2) * tR, Math.sin(rAngle2) * tR, 0);
          if (ri2 === 0) ctx.moveTo(rp2.x, rp2.y); else ctx.lineTo(rp2.x, rp2.y);
        }
        ctx.stroke();
      }

      // ── Edges ──
      for (var ei = 0; ei < edges.length; ei++) {
        var edge = edges[ei];
        var ef = project(edge.from.x, edge.from.y, edge.from.z);
        var et = project(edge.to.x, edge.to.y, edge.to.z);
        var bothDimmed = edge.from.dimmed && edge.to.dimmed;
        var neitherDimmed = !edge.from.dimmed && !edge.to.dimmed;
        var touchesFocus = focusNode && (edge.from === focusNode || edge.to === focusNode);

        var alpha, lw;
        if (touchesFocus) {
          alpha = 0.5; lw = 1.6;
        } else if (neitherDimmed) {
          alpha = edge.type === 'system' ? 0.2 : edge.type === 'article' ? 0.1 : 0.06;
          lw = edge.type === 'system' ? 1.2 : 0.6;
        } else if (bothDimmed) {
          alpha = 0.03; lw = 0.3;
        } else {
          alpha = 0.04; lw = 0.5;
        }

        // Depth fade
        var avgDepth = (ef.depth + et.depth) / 2;
        var depthFade = Math.max(0.25, Math.min(1, 1 - avgDepth / 1400));
        alpha *= depthFade;

        if (hoveredNode && (edge.from === hoveredNode || edge.to === hoveredNode)) {
          ctx.strokeStyle = rgba(C.system, 0.5); lw = 2;
        } else if (touchesFocus) {
          ctx.strokeStyle = rgba(C.system, alpha);
        } else {
          ctx.strokeStyle = rgba(C.silver, alpha);
        }
        ctx.lineWidth = lw;
        ctx.beginPath(); ctx.moveTo(ef.x, ef.y); ctx.lineTo(et.x, et.y); ctx.stroke();
      }

      // ── Particles ──
      if (!reducedMotion) {
        for (var pi = 0; pi < particles.length; pi++) {
          var part = particles[pi];
          part.t += part.speed;
          if (part.t >= 1) {
            part.edge = edges[Math.floor(Math.random() * edges.length)];
            part.t = 0; part.reverse = Math.random() > 0.5; continue;
          }
          var pt = part.reverse ? (1 - part.t) : part.t;
          var pe = part.edge;
          var ppx = pe.from.x + (pe.to.x - pe.from.x) * pt;
          var ppy = pe.from.y + (pe.to.y - pe.from.y) * pt;
          var ppz = pe.from.z + (pe.to.z - pe.from.z) * pt;
          var pp = project(ppx, ppy, ppz);
          var pAlpha = (1 - Math.abs(pt - 0.5) * 2) * 0.5;
          if (pe.from.dimmed && pe.to.dimmed) pAlpha *= 0.1;
          var pDepthFade = Math.max(0.2, Math.min(1, 1 - pp.depth / 1200));
          pAlpha *= pDepthFade;
          ctx.beginPath();
          ctx.arc(pp.x, pp.y, Math.max(0.8, 1.5 * pp.scale), 0, Math.PI * 2);
          ctx.fillStyle = rgba(C.system, pAlpha);
          ctx.fill();
        }
      }

      // ── Lightning bolts ──
      if (!reducedMotion) {
        lightningTimer += 0.016;
        if (lightningTimer >= lightningInterval) {
          lightningTimer = 0;
          spawnLightningBolt();
          // Vary interval slightly for organic feel
          lightningInterval = 0.8 + Math.random() * 1.0;
        }

        // Update and draw active bolts
        for (var bi = lightningBolts.length - 1; bi >= 0; bi--) {
          var bolt = lightningBolts[bi];
          bolt.t += bolt.speed; // per frame (~60fps)
          bolt.t = Math.min(bolt.t, 1);

          var pathNodes = bolt.path;
          var segCount = pathNodes.length - 1;
          // How far along the path (in segments) has the bolt reached
          var headPos = bolt.t * segCount;
          var tailPos = Math.max(0, headPos - 1.8); // trailing fade

          // Draw each segment the bolt has reached
          for (var si = 0; si < segCount; si++) {
            // Skip segments the bolt hasn't reached
            if (si > headPos) break;

            var segStart = si;
            var segEnd = si + 1;
            var fromN = pathNodes[segStart];
            var toN = pathNodes[segEnd];

            // Segment visibility (fade in head, fade out tail)
            var segMid = si + 0.5;
            var headDist = headPos - segMid;
            var tailDist = segMid - tailPos;
            var segAlpha = Math.min(1, headDist * 2) * Math.min(1, tailDist * 0.8);
            if (segAlpha <= 0) continue;
            segAlpha *= bolt.opacity;

            // Project endpoints
            var pf = project(fromN.x, fromN.y, fromN.z);
            var pt = project(toN.x, toN.y, toN.z);

            // Draw jagged lightning between the two projected points
            var steps = 8;
            var jag = 6 * (pf.scale + pt.scale) * 0.5; // scale jag with perspective

            ctx.beginPath();
            ctx.moveTo(pf.x, pf.y);
            for (var k = 1; k < steps; k++) {
              var frac = k / steps;
              var mx = pf.x + (pt.x - pf.x) * frac;
              var my = pf.y + (pt.y - pf.y) * frac;
              // Deterministic-ish jag based on seed + segment + step + time
              var jagAngle = Math.sin(bolt.forkSeed * 7.3 + si * 13.7 + k * 5.1 + time * 8) * jag;
              var jagAngle2 = Math.cos(bolt.forkSeed * 11.1 + si * 9.3 + k * 3.7 + time * 6) * jag * 0.5;
              // Perpendicular offset
              var edx = pt.x - pf.x, edy = pt.y - pf.y;
              var edLen = Math.sqrt(edx*edx + edy*edy) || 1;
              var perpX = -edy / edLen, perpY = edx / edLen;
              mx += perpX * jagAngle + perpY * jagAngle2 * 0.3;
              my += perpY * jagAngle + perpX * jagAngle2 * 0.3;
              ctx.lineTo(mx, my);
            }
            ctx.lineTo(pt.x, pt.y);

            // Bright core
            ctx.strokeStyle = 'rgba(180,220,255,' + (segAlpha * 0.9) + ')';
            ctx.lineWidth = bolt.width * (pf.scale + pt.scale) * 0.4;
            ctx.stroke();

            // Outer glow
            ctx.strokeStyle = 'rgba(74,158,255,' + (segAlpha * 0.4) + ')';
            ctx.lineWidth = bolt.width * (pf.scale + pt.scale) * 1.2;
            ctx.stroke();
          }

          // If bolt reached the end, trigger flash at endpoint
          if (bolt.t >= 1) {
            var endNode = pathNodes[pathNodes.length - 1];
            lightningFlashes.push({
              node: endNode,
              startTime: time,
              duration: 0.6,
            });
            lightningBolts.splice(bi, 1);
          }
        }

        // Draw flashes at submission endpoints
        for (var fi = lightningFlashes.length - 1; fi >= 0; fi--) {
          var flash = lightningFlashes[fi];
          var flashProgress = (time - flash.startTime) / flash.duration;
          if (flashProgress >= 1) {
            lightningFlashes.splice(fi, 1);
            continue;
          }
          var fn = flash.node;
          var fp = project(fn.x, fn.y, fn.z);

          // Flash: bright expanding ring + core burst
          var flashAlpha = 1 - flashProgress;
          flashAlpha = flashAlpha * flashAlpha; // ease-out curve
          var flashR = (15 + flashProgress * 40) * fp.scale;

          // Outer ring
          var ringGrad = ctx.createRadialGradient(fp.x, fp.y, 0, fp.x, fp.y, flashR);
          ringGrad.addColorStop(0, 'rgba(180,220,255,' + (flashAlpha * 0.6) + ')');
          ringGrad.addColorStop(0.3, 'rgba(74,158,255,' + (flashAlpha * 0.3) + ')');
          ringGrad.addColorStop(1, 'rgba(74,158,255,0)');
          ctx.beginPath(); ctx.arc(fp.x, fp.y, flashR, 0, Math.PI * 2);
          ctx.fillStyle = ringGrad; ctx.fill();

          // Bright core
          var coreR = (4 + flashProgress * 8) * fp.scale;
          ctx.beginPath(); ctx.arc(fp.x, fp.y, coreR, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(255,255,255,' + (flashAlpha * 0.8) + ')';
          ctx.fill();

          // Spark lines radiating outward
          var sparkCount = 6;
          for (var spi = 0; spi < sparkCount; spi++) {
            var sparkAngle = (spi / sparkCount) * Math.PI * 2 + flash.startTime * 3;
            var sparkLen = (10 + flashProgress * 25) * fp.scale;
            var sparkInner = flashR * 0.3;
            var sx1 = fp.x + Math.cos(sparkAngle) * sparkInner;
            var sy1 = fp.y + Math.sin(sparkAngle) * sparkInner;
            var sx2 = fp.x + Math.cos(sparkAngle) * sparkLen;
            var sy2 = fp.y + Math.sin(sparkAngle) * sparkLen;
            ctx.beginPath(); ctx.moveTo(sx1, sy1); ctx.lineTo(sx2, sy2);
            ctx.strokeStyle = 'rgba(180,220,255,' + (flashAlpha * 0.5) + ')';
            ctx.lineWidth = 1.5 * fp.scale;
            ctx.stroke();
          }
        }
      }

      // ── Nodes (sorted back-to-front for proper depth) ──
      var projected = [];
      for (var ni = 0; ni < nodes.length; ni++) {
        var nd = nodes[ni];
        var np = project(nd.x, nd.y, nd.z);
        projected.push({ node: nd, p: np });
      }
      projected.sort(function(a, b) { return b.p.depth - a.p.depth; }); // back first

      for (var pi2 = 0; pi2 < projected.length; pi2++) {
        var item = projected[pi2];
        var node = item.node;
        var ns = item.p;

        if (ns.x < -80 || ns.x > W + 80 || ns.y < -80 || ns.y > H + 80) continue;

        var r = node.radius * ns.scale;
        if (r < 0.5) continue;

        var isHovered = (node === hoveredNode);
        var isFocused = (focusNode && node === focusNode);

        if (!reducedMotion) node.pulse += 0.02;
        var pulseScale = reducedMotion ? 1 : (1 + Math.sin(node.pulse) * 0.06);

        // Depth-based alpha
        var depthAlpha = Math.max(0.3, Math.min(1, 1 - ns.depth / 1400));
        var nodeAlpha = node.dimmed ? 0.12 : 0.9;
        if (isHovered || isFocused) nodeAlpha = 1;
        nodeAlpha *= depthAlpha;

        var col = node.color;

        // Glow
        if (!node.dimmed && (isHovered || isFocused || opts.focusSlug)) {
          var glowR = r * (isFocused ? 5 : isHovered ? 4 : 2.5) * pulseScale;
          var glow = ctx.createRadialGradient(ns.x, ns.y, r * 0.3, ns.x, ns.y, glowR);
          var glowA = isFocused ? 0.35 : (isHovered ? 0.25 : 0.1);
          glow.addColorStop(0, rgba(col, glowA * depthAlpha));
          glow.addColorStop(1, rgba(col, 0));
          ctx.beginPath(); ctx.arc(ns.x, ns.y, glowR, 0, Math.PI * 2);
          ctx.fillStyle = glow; ctx.fill();
        }

        // Circle
        var drawR = r * (isHovered ? 1.4 : (isFocused ? 1.3 : 1)) * pulseScale;
        ctx.beginPath(); ctx.arc(ns.x, ns.y, drawR, 0, Math.PI * 2);
        ctx.fillStyle = rgba(col, nodeAlpha);
        if (isFocused) { ctx.shadowColor = rgba(col, 0.7); ctx.shadowBlur = 25; }
        else if (isHovered) { ctx.shadowColor = rgba(col, 0.5); ctx.shadowBlur = 15; }
        ctx.fill(); ctx.shadowBlur = 0;

        // Bright core
        if (!node.dimmed && (isHovered || isFocused)) {
          var coreA = isFocused ? 0.9 : (isHovered ? 0.8 : 0.5);
          ctx.beginPath(); ctx.arc(ns.x, ns.y, drawR * 0.35, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(255,255,255,' + (coreA * depthAlpha) + ')'; ctx.fill();
        }

        // Labels (system nodes are hidden — only article nodes get labels)
        var showLabel = !node.dimmed && node.type !== 'system' && (
          isFocused || isHovered ||
          (opts.focusSlug && !node.dimmed) ||
          (r > 3)
        );
        if (showLabel && depthAlpha > 0.35) {
          var fs = isFocused ? Math.max(9, 11 * ns.scale) :
                   Math.max(7, 8.5 * ns.scale);
          var weight = isFocused ? '600 ' : '400 ';
          ctx.font = weight + fs + 'px Inter,sans-serif';
          ctx.textAlign = 'center';
          var lines = node.label.split('\n');
          var labelY = ns.y + drawR + fs + 2;
          var labelAlpha = (isHovered || isFocused) ? 1 : depthAlpha * 0.8;
          for (var li = 0; li < lines.length; li++) {
            var ly = labelY + li * (fs + 1);
            // Shadow
            ctx.fillStyle = 'rgba(0,0,0,0.7)';
            ctx.fillText(lines[li], ns.x + 1, ly + 1);
            // Text
            if (isHovered || isFocused) {
              ctx.fillStyle = '#fff';
            } else if (node.type === 'system') {
              ctx.fillStyle = rgba(C.silver, labelAlpha);
            } else {
              ctx.fillStyle = rgba(node.color || C.silver, labelAlpha * 0.8);
            }
            ctx.fillText(lines[li], ns.x, ly);
          }
        }
      }
      // ── Editor overlay (called at end of every frame) ──
      if (editorOverlayFn) editorOverlayFn(ctx, project, W, H, cam);
    }
    // Start draw loop — use both rAF and a setTimeout fallback
    // to handle cases where rAF is deferred (e.g. during page transitions)
    requestAnimationFrame(draw);
    setTimeout(function() {
      if (instance.cancelled) return;
      // If canvas is still blank after 500ms, force-start
      var img = ctx.getImageData(0, 0, Math.min(canvas.width, 10), 1);
      var hasContent = false;
      for (var k = 0; k < img.data.length; k += 4) {
        if (img.data[k] > 0 || img.data[k+1] > 0 || img.data[k+2] > 0) { hasContent = true; break; }
      }
      if (!hasContent) {
        resize();
        draw();
      }
    }, 500);

    var api = {
      resetView: function() {
        cam.targetRotY = 0; cam.targetRotX = -0.15;
        cam.targetZoom = 1; cam.targetPanX = 0; cam.targetPanY = 0;
      },
      nodeCount: nodes.length,
      edgeCount: edges.length,
      // ── Editor API ──
      // Expose internals for graph-editor.js
      graph: graph,
      cam: cam,
      canvas: canvas,
      ctx: ctx,
      project: project,
      findNodeAt: findNodeAt,
      resize: resize,
      getW: function() { return W; },
      getH: function() { return H; },
      setRotation: function(rx, ry) {
        cam.targetRotX = rx; cam.targetRotY = ry;
        cam.autoRotate = false;
      },
      setEditorOverlay: function(fn) {
        // fn(ctx, project, W, H, cam) called at end of each draw frame
        editorOverlayFn = fn;
      },
      setEditorMouseHandler: function(handler) {
        // handler = { onMouseDown, onMouseMove, onMouseUp, onClick }
        editorMouseHandler = handler;
      },
      // Export graph state as JSON
      exportState: function() {
        var sysNodes = [];
        SYSTEM_NODES.forEach(function(sn) {
          var n = graph.nodeMap[sn.id];
          if (n) sysNodes.push({ id: sn.id, label: sn.label, tier: sn.tier, x: n.x, y: n.y, z: n.z });
        });
        return {
          systemNodes: sysNodes,
          systemEdges: SYSTEM_EDGES.slice(),
          articleConnections: JSON.parse(JSON.stringify(ARTICLE_CONNECTIONS)),
          submissionSlugs: SUBMISSION_SLUGS.slice(),
          forceVectors: JSON.parse(JSON.stringify(FORCE_VECTORS)),
        };
      },
    };

    // Editor overlay hook — called at end of each draw frame
    var editorOverlayFn = null;
    var editorMouseHandler = null;

    return api;
  }

  return { init: init, COLORS: C, SYSTEM_NODES: SYSTEM_NODES, SYSTEM_EDGES: SYSTEM_EDGES, ARTICLE_CONNECTIONS: ARTICLE_CONNECTIONS, SUBMISSION_SLUGS: SUBMISSION_SLUGS, FORCE_VECTORS: FORCE_VECTORS };
})();

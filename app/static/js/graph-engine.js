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
  var C = {
    // Core
    system:      { r: 74,  g: 158, b: 255 },   // steel blue — system/structural nodes
    silver:      { r: 192, g: 192, b: 192 },   // silver — labels, dimmed elements
    grid:        { r: 74,  g: 158, b: 255 },   // blue grid lines
    // Category accents — desaturated, cool-shifted to complement the core palette
    technique:   { r: 120, g: 210, b: 190 },   // seafoam — techniques (submissions, sweeps, etc.)
    position:    { r: 160, g: 140, b: 220 },   // muted lavender — positions
    concept:     { r: 200, g: 195, b: 150 },   // warm silver — concepts
    style:       { r: 130, g: 195, b: 210 },   // ice blue — styles/disciplines
    glossary:    { r: 170, g: 170, b: 180 },   // cool gray — glossary/uncategorized
  };

  // ── Excluded categories (not mapped in the graph) ──
  var EXCLUDED_CATEGORIES = ['person', 'competition', 'style'];

  // ══════════════════════════════════════════════════════════
  // ── INVERSE TREE: OPTION COMPRESSION MODEL ──
  // ══════════════════════════════════════════════════════════
  // Standing Neutral at top (max optionality, highest Y).
  // Tree branches downward through takedowns → positions →
  // submissions (zero options = tap).
  //
  // Y axis = optionality. High = many options. Low = end state.
  // Guards sorted by distance: far (higher) → close (lower).
  // Sweeps = polarity flips (edges between positions).
  // Passes = distance compressions (edges between guard tiers).
  //
  // Coordinates are explicit (x, y, z) for tree layout.
  // Negative Y = top of screen. Positive Y = bottom.
  // ──────────────────────────────────────────────────────────

  var SYSTEM_NODES = [
    // ── Tier 0: Standing — max optionality, top of tree ──
    { id: 'sys_standing', label: 'Standing\nNeutral', tier: 0, x: 0, y: -320, z: 0 },

    // ── Tier 1: Takedown types ──
    { id: 'sys_upper_td', label: 'Upper Body\nTakedowns', tier: 1, x: -160, y: -180, z: 40 },
    { id: 'sys_lower_td', label: 'Lower Body\nTakedowns', tier: 1, x: 160,  y: -180, z: -40 },

    // ── Tier 2: Guards — sorted by distance, descending Y ──
    { id: 'sys_far_guard',   label: 'Far Distance\nGuards',   tier: 2, x: -340, y: -30,  z: -50 },
    { id: 'sys_mid_guard',   label: 'Mid Distance\nGuards',   tier: 2, x: -200, y: 50,   z: 30 },
    { id: 'sys_close_guard', label: 'Close Distance\nGuards', tier: 2, x: -70,  y: 120,  z: -20 },

    // ── Tier 2: Passed / dominant positions ──
    { id: 'sys_side_control', label: 'Side\nControl',  tier: 2, x: 100,  y: 20,  z: 50 },
    { id: 'sys_mount',        label: 'Mount',          tier: 2, x: 240,  y: 70,  z: -30 },
    { id: 'sys_kob',          label: 'Knee on\nBelly', tier: 2, x: 360,  y: 10,  z: 30 },
    { id: 'sys_back_control', label: 'Back\nControl',  tier: 2, x: 400,  y: 110, z: -60 },

    // ── Tier 3: Submission end states — bottom of tree ──
    { id: 'sys_guard_subs', label: 'Guard\nSubmissions', tier: 3, x: -200, y: 270, z: 0 },
    { id: 'sys_top_subs',   label: 'Top\nSubmissions',   tier: 3, x: 170,  y: 270, z: 20 },
    { id: 'sys_back_subs',  label: 'Back\nSubmissions',  tier: 3, x: 400,  y: 270, z: -30 },
  ];

  var SYSTEM_EDGES = [
    // ── Standing → takedowns ──
    ['sys_standing', 'sys_upper_td'],
    ['sys_standing', 'sys_lower_td'],

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

    // ── Distance transitions (passes compress, escapes create distance) ──
    ['sys_far_guard', 'sys_mid_guard'],       // pass: far → mid
    ['sys_mid_guard', 'sys_close_guard'],     // pass: mid → close
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

    // ── Guards → guard submissions ──
    ['sys_far_guard', 'sys_guard_subs'],
    ['sys_mid_guard', 'sys_guard_subs'],
    ['sys_close_guard', 'sys_guard_subs'],

    // ── Dominant positions → top submissions ──
    ['sys_side_control', 'sys_top_subs'],
    ['sys_mount', 'sys_top_subs'],
    ['sys_kob', 'sys_top_subs'],

    // ── Back → back submissions ──
    ['sys_back_control', 'sys_back_subs'],
  ];

  // ── Article → system node mapping ──
  // Each article connects to where it lives in the tree.
  // Submissions connect to their position + the submission zone below it.
  // Sweeps are polarity flips: connect guard origin → dominant position destination.
  // Passes connect far guard → dominant position (distance compression).
  var ARTICLE_CONNECTIONS = {
    // ── Standing concepts ──
    'grip-fighting':        ['sys_standing'],
    'underhooks':           ['sys_standing', 'sys_upper_td'],
    'base-and-posture':     ['sys_standing'],

    // ── Upper body takedowns ──
    'double-leg-takedown':  ['sys_lower_td'],

    // ── Far distance guards ──
    'de-la-riva-guard':     ['sys_far_guard'],
    'butterfly-guard':      ['sys_mid_guard', 'sys_far_guard'],

    // ── Mid distance guards ──
    'half-guard':           ['sys_mid_guard'],
    'closed-guard':         ['sys_close_guard'],

    // ── Dominant positions ──
    'side-control':         ['sys_side_control'],
    'mount':                ['sys_mount'],
    'knee-on-belly':        ['sys_kob'],
    'back-control':         ['sys_back_control'],
    'turtle-position':      ['sys_back_control'],

    // ── Polarity flips (sweeps) — guard → position achieved ──
    'scissor-sweep':        ['sys_close_guard', 'sys_mount'],
    'berimbolo':            ['sys_far_guard', 'sys_back_control'],

    // ── Distance compressions (passes) — guard → past guard ──
    'guard-passing':        ['sys_far_guard', 'sys_side_control'],
    'toreando-pass':        ['sys_far_guard', 'sys_side_control'],

    // ── Concepts ──
    'frames-and-framing':   ['sys_close_guard', 'sys_side_control'],
    'shrimping':            ['sys_close_guard', 'sys_side_control'],

    // ── Guard submissions ──
    'triangle-choke':       ['sys_close_guard', 'sys_guard_subs'],
    'omoplata':             ['sys_close_guard', 'sys_guard_subs'],
    'guillotine':           ['sys_close_guard', 'sys_guard_subs'],
    'armbar':               ['sys_close_guard', 'sys_guard_subs', 'sys_mount', 'sys_top_subs'],
    'heel-hook':            ['sys_far_guard', 'sys_guard_subs'],
    'straight-ankle-lock':  ['sys_far_guard', 'sys_guard_subs'],

    // ── Top submissions ──
    'kimura':               ['sys_side_control', 'sys_top_subs'],
    'americana':            ['sys_mount', 'sys_top_subs'],
    'darce-choke':          ['sys_side_control', 'sys_top_subs'],

    // ── Back submissions ──
    'rear-naked-choke':     ['sys_back_control', 'sys_back_subs'],
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

    // System nodes — explicit tree coordinates scaled by mode
    SYSTEM_NODES.forEach(function(sn) {
      var node = {
        id: sn.id, label: sn.label,
        x: sn.x * scale,
        y: sn.y * scale,
        z: sn.z * scale,
        radius: sn.tier === 0 ? 9 * scale : (sn.tier === 3 ? 5 * scale : 6 * scale),
        color: C.system, type: 'system',
        slug: null, summary: null, category: null,
        tier: sn.tier, pulse: Math.random() * Math.PI * 2,
        dimmed: false,
      };
      nodes.push(node); nodeMap[sn.id] = node;
    });

    // Filter out excluded categories
    var filtered = articles.filter(function(a) {
      var cat = (a.category || '').toLowerCase();
      return EXCLUDED_CATEGORIES.indexOf(cat) === -1;
    });

    // Article nodes
    filtered.forEach(function(a) {
      var connections = ARTICLE_CONNECTIONS[a.slug];
      var cx = 0, cy = 0, cz = 0, count = 0;
      if (connections && connections.length > 0) {
        connections.forEach(function(sid) {
          var sn = nodeMap[sid];
          if (sn) { cx += sn.x; cy += sn.y; cz += sn.z; count++; }
        });
        if (count > 0) { cx /= count; cy /= count; cz /= count; }
      } else {
        var ang = Math.random() * Math.PI * 2;
        var elev = (Math.random() - 0.5) * 0.8;
        var outerR = 500 * scale;
        cx = Math.cos(ang) * outerR; cy = elev * outerR * 0.5; cz = Math.sin(ang) * outerR;
      }
      // Jitter in 3D
      var jitter = (50 + Math.random() * 70) * scale;
      var ja = Math.random() * Math.PI * 2;
      var je = (Math.random() - 0.5) * Math.PI * 0.5;
      cx += Math.cos(ja) * Math.cos(je) * jitter;
      cy += Math.sin(je) * jitter * 0.6;
      cz += Math.sin(ja) * Math.cos(je) * jitter;

      var cat = (a.category || 'glossary').toLowerCase();
      var nodeColor = C[cat] || C.glossary;
      var node = {
        id: 'art_' + a.slug, label: a.title,
        x: cx, y: cy, z: cz,
        radius: 3.5 * scale,
        color: nodeColor, type: 'article',
        slug: a.slug, summary: a.summary, category: a.category,
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
      if (!n.dimmed && n !== focusNode) {
        if (n.type === 'system') n.radius = Math.max(n.radius, 7);
        else n.radius = Math.max(n.radius, 5);
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
        ttCategory.textContent = node.category || (node.type === 'system' ? 'System' : '');
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
      if (node && node.slug) opts.onNodeClick(node.slug);
    });

    if (opts.interactive) {
      canvas.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        var node = findNodeAt(e.clientX, e.clientY);
        if (node) return;
        dragging = true;
        dragStart.x = e.clientX; dragStart.y = e.clientY;
        canvas.style.cursor = 'grabbing';
        cam.autoRotate = false;
      });
      window.addEventListener('mousemove', function(e) {
        if (!dragging) return;
        var dx = e.clientX - dragStart.x;
        var dy = e.clientY - dragStart.y;
        cam.targetRotY += dx * 0.005;
        cam.targetRotX += dy * 0.003;
        // Clamp vertical rotation
        cam.targetRotX = Math.max(-1.2, Math.min(1.2, cam.targetRotX));
        dragStart.x = e.clientX; dragStart.y = e.clientY;
      });
      window.addEventListener('mouseup', function() {
        if (dragging) { dragging = false; canvas.style.cursor = 'grab'; }
      });
      canvas.addEventListener('wheel', function(e) {
        e.preventDefault();
        var factor = e.deltaY > 0 ? 0.92 : 1.08;
        cam.targetZoom = Math.max(0.3, Math.min(3.5, cam.targetZoom * factor));
      }, { passive: false });
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

      // ── 3D Grid (XZ plane) ──
      var gridSize = 80, gridExtent = 600;
      for (var gx = -gridExtent; gx <= gridExtent; gx += gridSize) {
        var p1 = project(gx, 0, -gridExtent);
        var p2 = project(gx, 0, gridExtent);
        var a = (gx === 0) ? 0.1 : 0.04;
        ctx.strokeStyle = rgba(C.grid, a);
        ctx.lineWidth = (gx === 0) ? 1 : 0.5;
        ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
      }
      for (var gz = -gridExtent; gz <= gridExtent; gz += gridSize) {
        var q1 = project(-gridExtent, 0, gz);
        var q2 = project(gridExtent, 0, gz);
        var ag = (gz === 0) ? 0.1 : 0.04;
        ctx.strokeStyle = rgba(C.grid, ag);
        ctx.lineWidth = (gz === 0) ? 1 : 0.5;
        ctx.beginPath(); ctx.moveTo(q1.x, q1.y); ctx.lineTo(q2.x, q2.y); ctx.stroke();
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
        var nodeAlpha = node.dimmed ? 0.12 : (node.type === 'system' ? 1 : 0.9);
        if (isHovered || isFocused) nodeAlpha = 1;
        nodeAlpha *= depthAlpha;

        var col = node.color;

        // Glow
        if (!node.dimmed && (node.type === 'system' || isHovered || isFocused || opts.focusSlug)) {
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
        if (!node.dimmed && (node.type === 'system' || isHovered || isFocused)) {
          var coreA = isFocused ? 0.9 : (isHovered ? 0.8 : 0.5);
          ctx.beginPath(); ctx.arc(ns.x, ns.y, drawR * 0.35, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(255,255,255,' + (coreA * depthAlpha) + ')'; ctx.fill();
        }

        // Labels
        var showLabel = !node.dimmed && (
          node.type === 'system' || isFocused || isHovered ||
          (opts.focusSlug && !node.dimmed) ||
          (r > 3)
        );
        if (showLabel && depthAlpha > 0.35) {
          var fs = node.type === 'system' ? Math.max(8, 10 * ns.scale) :
                   isFocused ? Math.max(9, 11 * ns.scale) :
                   Math.max(7, 8.5 * ns.scale);
          var weight = (node.type === 'system' || isFocused) ? '600 ' : '400 ';
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

    return {
      resetView: function() {
        cam.targetRotY = 0; cam.targetRotX = -0.15;
        cam.targetZoom = 1; cam.targetPanX = 0; cam.targetPanY = 0;
      },
      nodeCount: nodes.length,
      edgeCount: edges.length,
    };
  }

  return { init: init, COLORS: C };
})();

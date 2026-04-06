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

    // ── Force vector colors — submission finish mechanics ──
    fv_arterial:     { r: 190, g: 100, b: 100 },
    fv_extension:    { r: 210, g: 140, b: 110 },
    fv_torsion:      { r: 200, g: 175, b: 100 },
    fv_compression:  { r: 100, g: 180, b: 175 },
  };

  // ── Excluded categories (not mapped in the graph) ──
  var EXCLUDED_CATEGORIES = ['person', 'competition', 'style', 'concept'];

  // ══════════════════════════════════════════════════════════
  // ── TAXONOMY-DRIVEN RADIAL GRAPH ──
  // ══════════════════════════════════════════════════════════
  //
  // No hardcoded positions or connections. Every node's placement
  // and every edge derives from the article's taxonomy fields:
  //
  //   graph_tier  → radial depth (center = standing, outer = submissions)
  //   mechanism   → angular sector (chokes cluster, locks cluster, etc.)
  //   target      → phi offset (body part sub-clustering)
  //   spatial     → theta fine-tuning (inner/outer/cross shifts)
  //
  // Layout is a continuous inside-out gradient with jitter,
  // not rigid shells. Taxonomy similarity drives edges.
  // ──────────────────────────────────────────────────────────

  // Spherical coordinate helper
  function spherePos(R, theta, phi) {
    return {
      x: R * Math.sin(phi) * Math.cos(theta),
      y: -R * Math.cos(phi),
      z: R * Math.sin(phi) * Math.sin(theta)
    };
  }

  // ── Tier depth mapping ──
  // graph_tier sys_* IDs → radial depth (0 = innermost, 4 = outermost)
  var TIER_DEPTH = {
    'sys_standing': 0,
    'sys_upper_td': 1, 'sys_lower_td': 1,
    'sys_close_guard': 2, 'sys_mid_guard': 2, 'sys_leg_entangle': 2,
    'sys_far_guard': 2, 'sys_front_headlock': 2,
    'sys_side_control': 3, 'sys_mount': 3, 'sys_kob': 3, 'sys_back_control': 3,
  };

  // ── Radial bands ──
  // depth → [minRadius, maxRadius]. Jitter within each band for organic spread.
  var DEPTH_RADII = {
    0: [30, 80],      // Standing — tight core
    1: [100, 160],    // Takedowns
    2: [180, 260],    // Guards + Front Headlock
    3: [280, 340],    // Dominant Positions
    4: [360, 430],    // Submissions — outermost
  };

  // Wireframe ring radii (midpoints of each band for visual guides)
  var RING_RADII = [55, 130, 220, 310, 395];

  // ── Finishing mechanisms ──
  // These are submission mechanics — always placed on the outermost shell.
  var FINISHING_MECHS = ['choke', 'lock', 'entanglement', 'compression'];

  // ── Mechanism → force vector type (for submission coloring) ──
  var MECH_TO_FV = {
    'choke': 'arterial', 'lock': 'extension',
    'entanglement': 'torsion', 'compression': 'compression'
  };

  // ── Mechanism angular sectors ──
  // Each mechanism gets a slice of theta so related techniques cluster.
  var MECH_THETA = {
    'choke': 0,          'lock': 0.55,        'entanglement': 1.1,
    'compression': 1.65, 'pin': 2.2,          'hook': 2.75,
    'throw': 3.3,        'reap': 3.75,        'sweep': 4.2,
    'pass': 4.75,        'drop': 5.2,         'wheel': 5.6,
  };

  // ── Target body part → phi offset for sub-clustering ──
  var TARGET_PHI = {
    'neck': -0.35, 'shoulder': -0.22, 'arm': -0.1,
    'wrist': 0.02, 'body': 0.12, 'hip': 0.22,
    'leg': 0.32, 'knee': 0.4, 'ankle': 0.48,
  };

  // ── Spatial qualifier → theta offset ──
  var SPATIAL_THETA = {
    'inner': -0.2, 'outer': 0.2, 'cross': 0.12,
    'major': -0.15, 'minor': 0.15, 'forward': -0.06,
    'rear': 0.06, 'side': 0.12, 'triangle': -0.1,
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
  // ── BUILD GRAPH (taxonomy-driven) ──
  // ══════════════════════════════════════════════════════════
  function buildGraph(articles, opts) {
    var nodes = [], edges = [], nodeMap = {};
    var scale = opts.mode === 'article' ? 0.6 : 1;

    // Filter out excluded categories
    var filtered = articles.filter(function(a) {
      var cat = (a.category || '').toLowerCase();
      return EXCLUDED_CATEGORIES.indexOf(cat) === -1;
    });

    // ── Place each article on the radial gradient ──
    filtered.forEach(function(a) {
      var mech    = (a.mechanism || '').toLowerCase();
      var target  = (a.target  || '').toLowerCase();
      var spatial = (a.spatial || '').toLowerCase();
      var graphTier = (a.graphTier || '');

      // Deterministic hash from slug for spread/jitter
      var slugHash = 0;
      for (var si = 0; si < a.slug.length; si++) slugHash += a.slug.charCodeAt(si);

      // ── Radial depth from graph_tier ──
      var tiers = graphTier ? graphTier.split(',').map(function(t) { return t.trim(); }).filter(Boolean) : [];
      var isFinisher = FINISHING_MECHS.indexOf(mech) !== -1;

      var depth;
      if (isFinisher) {
        depth = 4;  // Submissions always outermost
      } else if (tiers.length > 0) {
        var depthSum = 0, depthCnt = 0;
        tiers.forEach(function(t) {
          if (TIER_DEPTH[t] !== undefined) { depthSum += TIER_DEPTH[t]; depthCnt++; }
        });
        depth = depthCnt > 0 ? depthSum / depthCnt : 2;
      } else {
        depth = 2;  // fallback: guard level
      }

      // Radius: jitter within the depth band for gradient feel
      var band = DEPTH_RADII[Math.round(depth)] || DEPTH_RADII[2];
      var bandT = (slugHash % 100) / 100;  // 0-1 within band
      var R = (band[0] + (band[1] - band[0]) * bandT) * scale;

      // ── Angular position from mechanism ──
      var theta = MECH_THETA[mech] !== undefined ? MECH_THETA[mech] : (slugHash % 628) / 100;
      theta += SPATIAL_THETA[spatial] || 0;
      theta += ((slugHash % 41) / 41 - 0.5) * 0.45;  // spread within sector

      // ── Phi from target body part ──
      var phi = 1.57;  // equator baseline
      phi += TARGET_PHI[target] || 0;
      phi += ((slugHash % 29) / 29 - 0.5) * 0.25;  // spread
      phi = Math.max(0.3, Math.min(2.8, phi));  // avoid poles

      var pos = spherePos(R, theta, phi);

      // ── Mechanism-driven color ──
      var cat = (a.category || 'glossary').toLowerCase();
      var nodeColor = C[cat] || C.glossary;
      var fv = null;

      if (mech && C['mech_' + mech]) {
        nodeColor = C['mech_' + mech];
      }
      if (isFinisher) {
        fv = MECH_TO_FV[mech] || null;
        if (fv && C['fv_' + fv]) nodeColor = C['fv_' + fv];
      }

      var node = {
        id: 'art_' + a.slug, label: a.title,
        x: pos.x, y: pos.y, z: pos.z,
        radius: (isFinisher ? 4.5 : 3.5) * scale,
        color: nodeColor, type: 'article',
        slug: a.slug, summary: a.summary, category: a.category,
        mechanism: mech || null, target: target || null, spatial: spatial || null,
        forceVector: fv, depth: depth,
        tags: a.tags, pulse: Math.random() * Math.PI * 2,
        dimmed: false,
      };
      nodes.push(node); nodeMap[node.id] = node;
    });

    // ── Taxonomy-driven edges ──
    // Edges form between articles that share taxonomy properties.
    // Stronger connections for shared mechanism, lighter for shared target.
    // Adjacent depth bands with shared properties get cross-tier edges.
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i + 1; j < nodes.length; j++) {
        var nA = nodes[i], nB = nodes[j];
        var strength = 0;

        // Same mechanism → strong connection
        if (nA.mechanism && nA.mechanism === nB.mechanism) strength += 0.25;

        // Same target body part → medium connection
        if (nA.target && nA.target === nB.target) strength += 0.15;

        // Same spatial qualifier → light connection
        if (nA.spatial && nA.spatial === nB.spatial) strength += 0.08;

        // Bonus for adjacent depth bands (shows flow between tiers)
        var depthDiff = Math.abs((nA.depth || 0) - (nB.depth || 0));
        if (depthDiff <= 1 && strength > 0) strength += 0.05;

        // Only draw edges above a threshold to avoid clutter
        if (strength >= 0.25) {
          edges.push({ from: nA, to: nB, type: 'peer', strength: Math.min(strength, 0.5) });
        }
      }
    }

    // Center the graph (all axes — it's a sphere, not a tree)
    if (nodes.length > 0) {
      var avgX = 0, avgY = 0, avgZ = 0;
      nodes.forEach(function(n) { avgX += n.x; avgY += n.y; avgZ += n.z; });
      avgX /= nodes.length; avgY /= nodes.length; avgZ /= nodes.length;
      nodes.forEach(function(n) { n.x -= avgX; n.y -= avgY; n.z -= avgZ; });
    }

    return { nodes: nodes, edges: edges, nodeMap: nodeMap, scale: scale };
  }

  // ── Focus mode ──
  function applyFocus(graph, focusSlug) {
    if (!focusSlug) return null;
    var focusNode = graph.nodeMap['art_' + focusSlug];
    if (!focusNode) return null;

    var connectedIds = {};
    connectedIds[focusNode.id] = true;
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
    var graphScale = graph.scale;  // mode-based scale for sphere radii in draw loop

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
    // ── LIGHTNING / ELECTRICITY SYSTEM (radial) ──
    // ══════════════════════════════════════════════════════════
    // Lightning emanates from the center (origin) and strikes
    // submission nodes on the outer shell. Path goes through
    // 2-3 intermediate waypoints at increasing radii, following
    // nearby nodes at each depth band for organic routing.

    // Collect submission (finisher) nodes sorted by depth
    var submissionNodes = nodes.filter(function(n) {
      return n.depth === 4 && n.type === 'article';
    });

    // Sort all article nodes by depth for waypoint selection
    var nodesByDepth = {};
    nodes.forEach(function(n) {
      if (n.type !== 'article') return;
      var d = Math.round(n.depth || 0);
      if (!nodesByDepth[d]) nodesByDepth[d] = [];
      nodesByDepth[d].push(n);
    });

    // Active lightning bolts
    var lightningBolts = [];
    var lightningFlashes = [];
    var lightningTimer = 0;
    var lightningInterval = 1.2;

    function spawnLightningBolt() {
      if (submissionNodes.length === 0) return;

      // Pick a random submission as the endpoint
      var endNode = submissionNodes[Math.floor(Math.random() * submissionNodes.length)];

      // Build path: origin → depth 1 node → depth 2 node → depth 3 node → submission
      // Pick the closest node at each intermediate depth to the line from center to endpoint
      var pathNodes = [];

      // Start at origin (virtual point)
      var origin = { x: 0, y: 0, z: 0 };
      pathNodes.push(origin);

      // Waypoints at each intermediate depth band
      var wayDepths = [1, 2, 3];
      for (var wi = 0; wi < wayDepths.length; wi++) {
        var dNodes = nodesByDepth[wayDepths[wi]];
        if (!dNodes || dNodes.length === 0) continue;
        // Find node closest to the line from origin to endNode
        var bestDist = Infinity, bestNode = null;
        for (var ni = 0; ni < dNodes.length; ni++) {
          var dn = dNodes[ni];
          // Project onto the line origin → endNode, measure perpendicular distance
          var dx = endNode.x, dy = endNode.y, dz = endNode.z;
          var len2 = dx*dx + dy*dy + dz*dz;
          if (len2 < 1) continue;
          var t = (dn.x*dx + dn.y*dy + dn.z*dz) / len2;
          t = Math.max(0, Math.min(1, t));
          var px = dx*t - dn.x, py = dy*t - dn.y, pz = dz*t - dn.z;
          var dist = Math.sqrt(px*px + py*py + pz*pz);
          if (dist < bestDist) { bestDist = dist; bestNode = dn; }
        }
        if (bestNode) pathNodes.push(bestNode);
      }

      pathNodes.push(endNode);
      if (pathNodes.length < 2) return;

      var totalLen = 0;
      for (var j = 1; j < pathNodes.length; j++) {
        var ddx = pathNodes[j].x - pathNodes[j-1].x;
        var ddy = pathNodes[j].y - pathNodes[j-1].y;
        var ddz = pathNodes[j].z - pathNodes[j-1].z;
        totalLen += Math.sqrt(ddx*ddx + ddy*ddy + ddz*ddz);
      }

      lightningBolts.push({
        path: pathNodes,
        t: 0,
        speed: 0.01 + 0.004 / Math.max(1, pathNodes.length - 1),
        totalLen: totalLen,
        forkSeed: Math.random() * 100,
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
      // Faint ring outlines at each depth band's midpoint for visual structure.
      var ringSegments = 64;
      for (var ti = 0; ti < RING_RADII.length; ti++) {
        var tR = RING_RADII[ti] * graphScale;
        var tAlpha = ti === 0 ? 0.08 : (ti === 4 ? 0.04 : 0.06);
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
      // Export graph state as JSON (taxonomy-driven — no legacy data)
      exportState: function() {
        var articleNodes = [];
        nodes.forEach(function(n) {
          if (n.type === 'article') {
            articleNodes.push({
              id: n.id, slug: n.slug, label: n.label,
              mechanism: n.mechanism, target: n.target, spatial: n.spatial,
              depth: n.depth, x: n.x, y: n.y, z: n.z,
            });
          }
        });
        return { articleNodes: articleNodes, tierDepth: TIER_DEPTH };
      },
    };

    // Editor overlay hook — called at end of each draw frame
    var editorOverlayFn = null;
    var editorMouseHandler = null;

    return api;
  }

  return { init: init, COLORS: C, TIER_DEPTH: TIER_DEPTH, FINISHING_MECHS: FINISHING_MECHS };
})();

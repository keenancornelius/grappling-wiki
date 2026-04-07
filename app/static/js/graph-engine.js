/**
 * GrapplingWiki Knowledge Graph — SVG visualization
 *
 * Tiered layout:
 *   0 Standing → 1 Takedowns → 2 Guards → 3 Sweeps → 4 Passes → 5 Dominant → 6 Submissions
 *
 * Edges animate with an electric pulse tracing the causal chain.
 * Nodes are colored by category; submissions by force vector.
 */

var GWGraph = (function () {
  'use strict';

  // ── Color palette (matches Design Manifesto) ──
  var COLORS = {
    // Category colors
    standing:  'rgb(74, 158, 255)',   // steel blue — anchor
    takedown:  'rgb(100, 180, 210)',  // cool cyan
    guard:     'rgb(160, 140, 220)',  // muted lavender — positional
    sweep:     'rgb(140, 180, 160)',  // sage
    pass:      'rgb(120, 210, 190)',  // seafoam — active
    dominant:  'rgb(200, 195, 150)',  // warm silver
    concept:   'rgb(170, 170, 180)',  // cool gray
    default:   'rgb(150, 150, 160)',

    // Force vector colors (submissions override category)
    arterial:    'rgb(190, 100, 100)', // crimson — chokes
    extension:   'rgb(210, 140, 110)', // coral — hyperextension
    torsion:     'rgb(200, 175, 100)', // amber — rotation
    compression: 'rgb(100, 180, 175)', // teal — crushing

    // UI
    edge:        'rgba(255,255,255,0.06)',
    edgeHover:   'rgba(74, 158, 255, 0.5)',
    pulse:       'rgb(74, 158, 255)',
    bg:          '#0a0a0a',
    text:        '#ffffff',
    textDim:     'rgba(255,255,255,0.5)',
    tierLabel:   'rgba(255,255,255,0.08)',
  };

  // ── Tier config ──
  var TIER_LABELS = {
    0: 'Standing',
    1: 'Takedowns',
    2: 'Guards',
    3: 'Sweeps',
    4: 'Passes',
    5: 'Dominant Positions',
    6: 'Submissions',
  };

  var TIER_COUNT = 7;

  // ── State ──
  var svg, container, nodesG, edgesG, labelsG, pulseG;
  var nodes = [], edges = [], nodeMap = {};
  var width, height;
  var hoveredNode = null;
  var tooltip;
  var transform = { x: 0, y: 0, k: 1 };
  var isDragging = false, dragStart = { x: 0, y: 0 };
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Layout ──
  function layoutNodes() {
    // Group nodes by tier
    var tiers = {};
    for (var i = 0; i < TIER_COUNT; i++) tiers[i] = [];
    var unplaced = [];

    nodes.forEach(function (n) {
      if (n.tier >= 0 && n.tier < TIER_COUNT) {
        tiers[n.tier].push(n);
      } else {
        unplaced.push(n);
      }
    });

    // Vertical spacing — place tiered nodes first
    var tierPadding = 60;
    var topPad = 80;
    var tierHeight = (height - topPad - tierPadding) / (TIER_COUNT - 1 || 1);

    // Assign positions for tiered nodes
    for (var t = 0; t < TIER_COUNT; t++) {
      var tierNodes = tiers[t];
      if (!tierNodes.length) continue;

      var y = topPad + t * tierHeight;
      var count = tierNodes.length;

      // Horizontal distribution: spread evenly with padding
      var xPad = 60;
      var availWidth = width - xPad * 2;
      var spacing = count > 1 ? availWidth / (count - 1) : 0;
      var startX = count > 1 ? xPad : width / 2;

      // Count connections per node for sorting
      tierNodes.forEach(function (n) {
        var c = 0;
        edges.forEach(function (e) {
          if (e.source === n.id || e.target === n.id) c++;
        });
        n._connCount = c;
      });

      // Sort: most connected nodes go to the center, fewest to the edges
      // First sort by connection count descending
      tierNodes.sort(function (a, b) { return b._connCount - a._connCount; });

      // Then distribute center-out: index 0→center, 1→left, 2→right, 3→left...
      var ordered = new Array(count);
      var mid = Math.floor(count / 2);
      var left = mid, right = mid + 1;
      for (var ci = 0; ci < count; ci++) {
        if (ci === 0) {
          ordered[mid] = tierNodes[ci];
        } else if (ci % 2 === 1 && left > 0) {
          left--;
          ordered[left] = tierNodes[ci];
        } else if (right < count) {
          ordered[right] = tierNodes[ci];
          right++;
        } else {
          left--;
          ordered[left] = tierNodes[ci];
        }
      }

      // For dense tiers (>12 nodes), stagger labels to avoid overlap
      var dense = count > 12;
      ordered.forEach(function (n, i) {
        if (!n) return;
        n.x = startX + i * spacing;
        n.y = y;
        n._labelStagger = dense ? (i % 2 === 0 ? 0 : 12) : 0;
      });
    }

    // Place unplaced nodes (concepts/principles) at centroid of connected nodes
    // These float freely — not snapped to any tier row
    unplaced.forEach(function (n) {
      var cx = 0, cy = 0, connCount = 0;
      edges.forEach(function (e) {
        var other = null;
        if (e.source === n.id) other = nodeMap[e.target];
        if (e.target === n.id) other = nodeMap[e.source];
        if (other && typeof other.x === 'number') {
          cx += other.x;
          cy += other.y;
          connCount++;
        }
      });
      if (connCount > 0) {
        n.x = cx / connCount;
        n.y = cy / connCount;
      } else {
        // No connections — park in a neutral spot
        n.x = width / 2 + (Math.random() - 0.5) * 200;
        n.y = height / 2;
      }
      n._labelStagger = 0;
      n._isFree = true; // mark as free-floating for rendering
    });
  }

  // ── Node color ──
  function nodeColor(n) {
    if (n.force_vector) return COLORS[n.force_vector] || COLORS.default;

    var cat = n.category || '';
    var parent = n.parent_category || '';

    if (cat === 'standing' || parent === 'standing') return COLORS.standing;
    if (cat === 'takedown') return COLORS.takedown;
    if (cat === 'guard' || cat === 'leg-entanglement') return COLORS.guard;
    if (cat === 'sweep') return COLORS.sweep;
    if (cat === 'pass') return COLORS.pass;
    if (cat === 'dominant-position') return COLORS.dominant;
    if (cat === 'submission') {
      return COLORS.arterial; // fallback if no force_vector
    }
    if (parent === 'concept' || cat === 'concept' || cat === 'principle') return COLORS.concept;
    return COLORS.default;
  }

  // ── Node radius ──
  function nodeRadius(n) {
    // Count connections
    var count = 0;
    edges.forEach(function (e) {
      if (e.source === n.id || e.target === n.id) count++;
    });
    return Math.max(4, Math.min(12, 4 + count * 0.6));
  }

  // ── SVG helpers ──
  function svgEl(tag, attrs) {
    var el = document.createElementNS('http://www.w3.org/2000/svg', tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        el.setAttribute(k, attrs[k]);
      });
    }
    return el;
  }

  // ── Edge path (curved) ──
  function edgePath(e) {
    var src = nodeMap[e.source];
    var tgt = nodeMap[e.target];
    if (!src || !tgt) return '';

    var dx = tgt.x - src.x;
    var dy = tgt.y - src.y;

    // Curve amount based on horizontal distance
    var cx = (src.x + tgt.x) / 2;
    var cy = (src.y + tgt.y) / 2;
    var curveOffset = Math.min(Math.abs(dx) * 0.15, 40);
    // Alternate curve direction based on source position
    var dir = (src.x < width / 2) ? -1 : 1;
    cx += curveOffset * dir;

    return 'M' + src.x + ',' + src.y + ' Q' + cx + ',' + cy + ' ' + tgt.x + ',' + tgt.y;
  }

  // ── Render ──
  function render() {
    // Clear groups
    while (edgesG.firstChild) edgesG.removeChild(edgesG.firstChild);
    while (nodesG.firstChild) nodesG.removeChild(nodesG.firstChild);
    while (labelsG.firstChild) labelsG.removeChild(labelsG.firstChild);
    while (pulseG.firstChild) pulseG.removeChild(pulseG.firstChild);

    // Tier background labels
    var tierPadding = 60;
    var topPad = 80;
    var tierHeight = (height - topPad - tierPadding) / (TIER_COUNT - 1 || 1);

    for (var t = 0; t < TIER_COUNT; t++) {
      var y = topPad + t * tierHeight;
      var label = svgEl('text', {
        x: 16, y: y + 4,
        fill: COLORS.tierLabel,
        'font-size': '11',
        'font-family': 'Inter, system-ui, sans-serif',
        'font-weight': '600',
        'text-transform': 'uppercase',
        'letter-spacing': '0.1em',
      });
      label.textContent = TIER_LABELS[t] || '';
      labelsG.appendChild(label);

      // Tier divider line
      var line = svgEl('line', {
        x1: 0, y1: y, x2: width, y2: y,
        stroke: 'rgba(255,255,255,0.03)',
        'stroke-width': 1,
      });
      labelsG.appendChild(line);
    }

    // Edges
    edges.forEach(function (e, i) {
      var d = edgePath(e);
      if (!d) return;

      var path = svgEl('path', {
        d: d,
        fill: 'none',
        stroke: COLORS.edge,
        'stroke-width': 1,
        class: 'graph-edge',
        'data-source': e.source,
        'data-target': e.target,
        'data-type': e.type,
      });
      edgesG.appendChild(path);
      e._path = path;

      // Pulse animation path (hidden until hover)
      if (!reducedMotion) {
        var pulse = svgEl('circle', {
          r: 2,
          fill: COLORS.pulse,
          opacity: 0,
          class: 'graph-pulse',
        });

        var anim = svgEl('animateMotion', {
          dur: (1.2 + Math.random() * 0.8) + 's',
          repeatCount: 'indefinite',
          path: d,
        });
        pulse.appendChild(anim);
        pulseG.appendChild(pulse);
        e._pulse = pulse;
      }
    });

    // Nodes
    nodes.forEach(function (n) {
      var r = nodeRadius(n);
      var color = nodeColor(n);
      n._radius = r;
      n._color = color;

      var g = svgEl('g', {
        class: 'graph-node',
        'data-id': n.id,
        transform: 'translate(' + n.x + ',' + n.y + ')',
        style: 'cursor:pointer',
      });

      // Glow (hidden until hover)
      var glow = svgEl('circle', {
        r: r + 6,
        fill: color,
        opacity: 0,
        class: 'node-glow',
      });
      g.appendChild(glow);

      // Main circle
      var circle = svgEl('circle', {
        r: r,
        fill: color,
        opacity: 0.85,
        class: 'node-circle',
      });
      g.appendChild(circle);

      // Label — stagger vertically in dense tiers to reduce overlap
      var labelOffset = r + 14;
      if (n._labelStagger) labelOffset += n._labelStagger;
      var text = svgEl('text', {
        x: 0, y: labelOffset,
        fill: COLORS.textDim,
        'font-size': r > 7 ? '10' : '8',
        'font-family': 'Inter, system-ui, sans-serif',
        'text-anchor': 'middle',
        class: 'node-label',
      });
      text.textContent = n.title;
      g.appendChild(text);

      // Submission terminal flash (bottom glow bar)
      if (n.tier === 6 && n.force_vector) {
        var flash = svgEl('line', {
          x1: -r, y1: r + 2, x2: r, y2: r + 2,
          stroke: color,
          'stroke-width': 2,
          opacity: 0.4,
          class: 'node-terminal',
        });
        g.appendChild(flash);
      }

      nodesG.appendChild(g);
      n._el = g;
      n._glow = glow;

      // Events
      g.addEventListener('mouseenter', function () { onNodeHover(n); });
      g.addEventListener('mouseleave', function () { onNodeLeave(n); });
      g.addEventListener('click', function (ev) {
        ev.stopPropagation();
        window.location.href = n.url;
      });
    });
  }

  // ── Hover interactions ──
  function onNodeHover(n) {
    hoveredNode = n;

    // Show tooltip
    tooltip.style.display = 'block';
    tooltip.innerHTML =
      '<strong>' + n.title + '</strong>' +
      (n.summary ? '<br><span style="color:rgba(255,255,255,0.5);font-size:11px">' + n.summary.substring(0, 100) + '</span>' : '') +
      (n.force_vector ? '<br><span style="color:' + (COLORS[n.force_vector] || '#fff') + ';font-size:10px;text-transform:uppercase;letter-spacing:0.05em">' + n.force_vector + '</span>' : '');

    // Position tooltip
    var svgRect = svg.getBoundingClientRect();
    tooltip.style.left = (svgRect.left + n.x * transform.k + transform.x + 15) + 'px';
    tooltip.style.top = (svgRect.top + n.y * transform.k + transform.y - 10) + 'px';

    // Highlight node
    n._glow.setAttribute('opacity', '0.3');
    n._el.querySelector('.node-label').setAttribute('fill', COLORS.text);

    // Find connected edges and light them up
    var connectedIds = new Set();
    connectedIds.add(n.id);

    edges.forEach(function (e) {
      var connected = (e.source === n.id || e.target === n.id);
      if (connected) {
        e._path.setAttribute('stroke', COLORS.edgeHover);
        e._path.setAttribute('stroke-width', '1.5');
        if (e._pulse) {
          e._pulse.setAttribute('opacity', '0.8');
        }
        connectedIds.add(e.source);
        connectedIds.add(e.target);
      }
    });

    // Dim unconnected nodes
    nodes.forEach(function (other) {
      if (!connectedIds.has(other.id)) {
        other._el.querySelector('.node-circle').setAttribute('opacity', '0.15');
        other._el.querySelector('.node-label').setAttribute('opacity', '0.15');
      }
    });
  }

  function onNodeLeave() {
    hoveredNode = null;
    tooltip.style.display = 'none';

    // Reset all edges
    edges.forEach(function (e) {
      e._path.setAttribute('stroke', COLORS.edge);
      e._path.setAttribute('stroke-width', '1');
      if (e._pulse) {
        e._pulse.setAttribute('opacity', '0');
      }
    });

    // Reset all nodes
    nodes.forEach(function (n) {
      n._glow.setAttribute('opacity', '0');
      n._el.querySelector('.node-circle').setAttribute('opacity', '0.85');
      n._el.querySelector('.node-label').setAttribute('fill', COLORS.textDim);
      n._el.querySelector('.node-label').setAttribute('opacity', '1');
    });
  }

  // ══════════════════════════════════════════════════════════════════════
  // ELECTRIC TRACE — lightning bolt from Standing → Submission
  // ══════════════════════════════════════════════════════════════════════
  var traceInterval;
  var traceG;
  var traceActive = false;

  // Generate jagged lightning segments between two points
  function lightningPath(x1, y1, x2, y2, jag, segments) {
    var pts = [{ x: x1, y: y1 }];
    for (var i = 1; i < segments; i++) {
      var t = i / segments;
      var mx = x1 + (x2 - x1) * t + (Math.random() - 0.5) * jag;
      var my = y1 + (y2 - y1) * t + (Math.random() - 0.5) * jag * 0.3;
      pts.push({ x: mx, y: my });
    }
    pts.push({ x: x2, y: y2 });
    var d = 'M ' + pts[0].x.toFixed(1) + ' ' + pts[0].y.toFixed(1);
    for (var j = 1; j < pts.length; j++) {
      d += ' L ' + pts[j].x.toFixed(1) + ' ' + pts[j].y.toFixed(1);
    }
    return { d: d, pts: pts };
  }

  // Create a forking branch bolt off a point
  function forkBolt(cx, cy, angle, len) {
    var ex = cx + Math.cos(angle) * len;
    var ey = cy + Math.sin(angle) * len;
    var segs = 3 + Math.floor(Math.random() * 3);
    var pts = [{ x: cx, y: cy }];
    for (var i = 1; i <= segs; i++) {
      var t = i / segs;
      pts.push({
        x: cx + (ex - cx) * t + (Math.random() - 0.5) * len * 0.3,
        y: cy + (ey - cy) * t + (Math.random() - 0.5) * len * 0.2,
      });
    }
    var d = 'M ' + pts[0].x.toFixed(1) + ' ' + pts[0].y.toFixed(1);
    for (var j = 1; j < pts.length; j++) {
      d += ' L ' + pts[j].x.toFixed(1) + ' ' + pts[j].y.toFixed(1);
    }
    return d;
  }

  // Build a chain of nodes from tier 0 → tier N
  function buildTracePath() {
    var path = [];
    for (var t = 0; t < TIER_COUNT; t++) {
      var candidates = nodes.filter(function (n) { return n.tier === t; });
      if (!candidates.length) continue;
      if (path.length === 0) {
        path.push(candidates[Math.floor(Math.random() * candidates.length)]);
      } else {
        var prev = path[path.length - 1];
        var connected = candidates.filter(function (c) {
          return edges.some(function (e) {
            return (e.source === prev.id && e.target === c.id) ||
                   (e.target === prev.id && e.source === c.id);
          });
        });
        if (connected.length > 0) {
          path.push(connected[Math.floor(Math.random() * connected.length)]);
        } else {
          candidates.sort(function (a, b) {
            return Math.abs(a.x - prev.x) - Math.abs(b.x - prev.x);
          });
          path.push(candidates[0]);
        }
      }
    }
    return path;
  }

  function animateTrace() {
    if (reducedMotion || hoveredNode || traceActive) return;
    traceActive = true;

    var chain = buildTracePath();
    if (chain.length < 2) { traceActive = false; return; }

    var allEls = []; // track all SVG elements for cleanup
    var segDur = 280; // ms per segment
    var totalDur = chain.length * segDur + 1200;

    // Animate segment by segment, top to bottom
    chain.forEach(function (node, idx) {
      if (idx === 0) return;
      var prev = chain[idx - 1];
      var delay = idx * segDur;

      setTimeout(function () {
        if (hoveredNode) return;

        // ── Main lightning bolt between nodes ──
        var dist = Math.sqrt(Math.pow(node.x - prev.x, 2) + Math.pow(node.y - prev.y, 2));
        var jag = Math.min(60, dist * 0.15);
        var segs = Math.max(5, Math.floor(dist / 15));
        var bolt = lightningPath(prev.x, prev.y, node.x, node.y, jag, segs);

        // Main bolt path — bright white core
        var mainPath = svgEl('path', {
          d: bolt.d, fill: 'none', stroke: '#fff',
          'stroke-width': '2', opacity: '0.9',
          'stroke-linecap': 'round', 'stroke-linejoin': 'round',
        });
        traceG.appendChild(mainPath);
        allEls.push(mainPath);

        // Glow layer — wider, colored, electric blur
        var glowPath = svgEl('path', {
          d: bolt.d, fill: 'none', stroke: COLORS.pulse,
          'stroke-width': '6', opacity: '0.5',
          filter: 'url(#electric)',
          'stroke-linecap': 'round',
        });
        traceG.appendChild(glowPath);
        allEls.push(glowPath);

        // Second glow — even wider, atmospheric
        var outerGlow = svgEl('path', {
          d: bolt.d, fill: 'none', stroke: COLORS.pulse,
          'stroke-width': '18', opacity: '0.12',
          filter: 'url(#electric)',
        });
        traceG.appendChild(outerGlow);
        allEls.push(outerGlow);

        // ── Fork bolts — small branches off the main bolt ──
        var forkCount = 1 + Math.floor(Math.random() * 3);
        for (var f = 0; f < forkCount; f++) {
          var forkPt = bolt.pts[Math.floor(Math.random() * (bolt.pts.length - 1)) + 1];
          var forkAngle = Math.random() * Math.PI * 2;
          var forkLen = 15 + Math.random() * 30;
          var forkD = forkBolt(forkPt.x, forkPt.y, forkAngle, forkLen);

          var forkEl = svgEl('path', {
            d: forkD, fill: 'none', stroke: '#fff',
            'stroke-width': '1', opacity: '0.6',
            'stroke-linecap': 'round',
          });
          traceG.appendChild(forkEl);
          allEls.push(forkEl);

          var forkGlow = svgEl('path', {
            d: forkD, fill: 'none', stroke: COLORS.pulse,
            'stroke-width': '4', opacity: '0.3',
            filter: 'url(#electric)',
          });
          traceG.appendChild(forkGlow);
          allEls.push(forkGlow);
        }

        // ── Spark particles at the target node ──
        var sparkCount = 4 + Math.floor(Math.random() * 5);
        for (var s = 0; s < sparkCount; s++) {
          var sa = Math.random() * Math.PI * 2;
          var sr = 8 + Math.random() * 20;
          var sx = node.x + Math.cos(sa) * sr;
          var sy = node.y + Math.sin(sa) * sr;
          var sparkSize = 1 + Math.random() * 2;

          var spark = svgEl('circle', {
            cx: node.x, cy: node.y, r: sparkSize,
            fill: Math.random() > 0.5 ? '#fff' : COLORS.pulse,
            opacity: '0.9',
          });
          traceG.appendChild(spark);
          allEls.push(spark);

          // Animate spark outward
          (function (el, tx, ty) {
            var start = performance.now();
            var dur = 200 + Math.random() * 300;
            var ox = parseFloat(el.getAttribute('cx'));
            var oy = parseFloat(el.getAttribute('cy'));
            function step(now) {
              var t = Math.min(1, (now - start) / dur);
              var ease = 1 - Math.pow(1 - t, 3); // ease-out cubic
              el.setAttribute('cx', (ox + (tx - ox) * ease).toFixed(1));
              el.setAttribute('cy', (oy + (ty - oy) * ease).toFixed(1));
              el.setAttribute('opacity', (0.9 * (1 - t)).toFixed(2));
              el.setAttribute('r', (sparkSize * (1 - t * 0.5)).toFixed(1));
              if (t < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
          })(spark, sx, sy);
        }

        // ── Node impact flash ──
        if (node._glow) {
          node._glow.setAttribute('fill', '#fff');
          node._glow.setAttribute('opacity', '0.6');
          node._el.querySelector('.node-circle').setAttribute('fill', '#fff');

          setTimeout(function () {
            node._glow.setAttribute('fill', node._color);
            node._glow.setAttribute('opacity', '0.3');
            node._el.querySelector('.node-circle').setAttribute('fill', node._color);
          }, 150);
          setTimeout(function () {
            if (!hoveredNode) {
              node._glow.setAttribute('opacity', '0');
              node._el.querySelector('.node-circle').setAttribute('fill', node._color);
            }
          }, 800);
        }

        // Previous node glow lingers
        if (prev._glow && !hoveredNode) {
          prev._glow.setAttribute('opacity', '0.15');
        }

        // ── Flicker effect — redraw bolt 2x rapidly for crackle ──
        setTimeout(function () {
          if (hoveredNode) return;
          var flicker = lightningPath(prev.x, prev.y, node.x, node.y, jag * 1.2, segs);
          mainPath.setAttribute('d', flicker.d);
          glowPath.setAttribute('d', flicker.d);
          mainPath.setAttribute('opacity', '0.7');
        }, 60);
        setTimeout(function () {
          if (hoveredNode) return;
          var flicker2 = lightningPath(prev.x, prev.y, node.x, node.y, jag * 0.8, segs);
          mainPath.setAttribute('d', flicker2.d);
          glowPath.setAttribute('d', flicker2.d);
          mainPath.setAttribute('opacity', '0.5');
        }, 120);

        // Fade this segment
        setTimeout(function () {
          mainPath.setAttribute('opacity', '0.15');
          glowPath.setAttribute('opacity', '0.1');
          outerGlow.setAttribute('opacity', '0.03');
        }, segDur + 200);

      }, delay);
    });

    // Full cleanup after all segments done
    setTimeout(function () {
      // Fade everything out
      allEls.forEach(function (el) {
        el.setAttribute('opacity', '0');
      });
      // Reset node glows
      chain.forEach(function (n) {
        if (n._glow && !hoveredNode) n._glow.setAttribute('opacity', '0');
      });
      // Remove from DOM
      setTimeout(function () {
        allEls.forEach(function (el) {
          if (el.parentNode) el.parentNode.removeChild(el);
        });
        traceActive = false;
      }, 400);
    }, totalDur);
  }

  function startAmbientPulse() {
    if (reducedMotion || !edges.length) return;
    setTimeout(animateTrace, 1200);
    traceInterval = setInterval(function () {
      if (!hoveredNode) animateTrace();
    }, 6000);
  }

  // ── Pan and zoom ──
  function applyTransform() {
    container.setAttribute('transform',
      'translate(' + transform.x + ',' + transform.y + ') scale(' + transform.k + ')');
  }

  function setupInteraction() {
    svg.addEventListener('wheel', function (ev) {
      ev.preventDefault();
      var delta = ev.deltaY > 0 ? 0.9 : 1.1;
      var newK = Math.max(0.3, Math.min(3, transform.k * delta));

      // Zoom toward cursor
      var rect = svg.getBoundingClientRect();
      var mx = ev.clientX - rect.left;
      var my = ev.clientY - rect.top;

      transform.x = mx - (mx - transform.x) * (newK / transform.k);
      transform.y = my - (my - transform.y) * (newK / transform.k);
      transform.k = newK;
      applyTransform();
    }, { passive: false });

    svg.addEventListener('mousedown', function (ev) {
      if (ev.target.closest('.graph-node')) return;
      isDragging = true;
      dragStart.x = ev.clientX - transform.x;
      dragStart.y = ev.clientY - transform.y;
      svg.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', function (ev) {
      if (!isDragging) return;
      transform.x = ev.clientX - dragStart.x;
      transform.y = ev.clientY - dragStart.y;
      applyTransform();
    });

    window.addEventListener('mouseup', function () {
      isDragging = false;
      svg.style.cursor = 'grab';
    });
  }

  // ── Init ──
  function init(containerId) {
    var el = document.getElementById(containerId);
    if (!el) return;

    // Create tooltip
    tooltip = document.createElement('div');
    tooltip.className = 'graph-tooltip';
    tooltip.style.cssText = 'display:none;position:fixed;z-index:1000;background:rgba(15,15,15,0.95);border:1px solid rgba(255,255,255,0.1);padding:10px 14px;border-radius:2px;font-size:12px;color:#fff;pointer-events:none;max-width:250px;line-height:1.5;font-family:Inter,system-ui,sans-serif;';
    document.body.appendChild(tooltip);

    // Size
    var rect = el.getBoundingClientRect();
    width = rect.width || 1200;
    height = rect.height || 700;

    // Create SVG
    svg = svgEl('svg', {
      width: '100%',
      height: '100%',
      viewBox: '0 0 ' + width + ' ' + height,
      style: 'cursor:grab;background:' + COLORS.bg,
    });
    el.appendChild(svg);

    // Defs for glow filters
    var defs = svgEl('defs');

    // Soft glow (for nodes, hover)
    var filter = svgEl('filter', { id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%' });
    var blur = svgEl('feGaussianBlur', { stdDeviation: '3', result: 'blur' });
    var merge = svgEl('feMerge');
    merge.appendChild(svgEl('feMergeNode', { in: 'blur' }));
    merge.appendChild(svgEl('feMergeNode', { in: 'SourceGraphic' }));
    filter.appendChild(blur);
    filter.appendChild(merge);
    defs.appendChild(filter);

    // Electric glow (sharper, brighter — for lightning)
    var eFilter = svgEl('filter', { id: 'electric', x: '-80%', y: '-80%', width: '260%', height: '260%' });
    // Inner sharp glow
    var eBlur1 = svgEl('feGaussianBlur', { stdDeviation: '2', result: 'inner', in: 'SourceGraphic' });
    // Outer diffuse glow
    var eBlur2 = svgEl('feGaussianBlur', { stdDeviation: '8', result: 'outer', in: 'SourceGraphic' });
    var eMerge = svgEl('feMerge');
    eMerge.appendChild(svgEl('feMergeNode', { in: 'outer' }));
    eMerge.appendChild(svgEl('feMergeNode', { in: 'inner' }));
    eMerge.appendChild(svgEl('feMergeNode', { in: 'SourceGraphic' }));
    eFilter.appendChild(eBlur1);
    eFilter.appendChild(eBlur2);
    eFilter.appendChild(eMerge);
    defs.appendChild(eFilter);

    svg.appendChild(defs);

    // Groups (order = z-index)
    container = svgEl('g', { class: 'graph-container' });
    labelsG = svgEl('g', { class: 'tier-labels' });
    edgesG = svgEl('g', { class: 'edges' });
    pulseG = svgEl('g', { class: 'pulses', filter: 'url(#glow)' });
    nodesG = svgEl('g', { class: 'nodes' });

    traceG = svgEl('g', { class: 'traces' });

    container.appendChild(labelsG);
    container.appendChild(edgesG);
    container.appendChild(pulseG);
    container.appendChild(traceG);
    container.appendChild(nodesG);
    svg.appendChild(container);

    // Fetch data
    fetch('/api/graph')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        nodes = data.nodes || [];
        edges = data.edges || [];

        // Build lookup
        nodeMap = {};
        nodes.forEach(function (n) { nodeMap[n.id] = n; });

        // Layout and render
        layoutNodes();
        render();
        setupInteraction();
        startAmbientPulse();

        // Show node count
        var counter = document.getElementById('graph-node-count');
        if (counter) counter.textContent = nodes.length + ' articles · ' + edges.length + ' connections';
      })
      .catch(function (err) {
        console.error('[GWGraph] Failed to load graph data:', err);
        el.innerHTML = '<p style="color:rgba(255,255,255,0.4);text-align:center;padding:60px;font-family:Inter,system-ui,sans-serif">Failed to load graph data.</p>';
      });
  }

  // ── Resize handler ──
  function handleResize(containerId) {
    var el = document.getElementById(containerId);
    if (!el || !svg) return;
    var rect = el.getBoundingClientRect();
    width = rect.width || 1200;
    height = rect.height || 700;
    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    layoutNodes();
    render();
  }

  return { init: init, resize: handleResize };
})();

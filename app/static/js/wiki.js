/**
 * GrapplingWiki - Main JavaScript
 * Handles interactive features, animations, and the wiki editor.
 */

// ============================================================
// Animation System — Scroll Reveals & Click Feedback
// ============================================================
(function() {
  // ── Scroll-triggered module reveals ──
  const REVEAL_SELECTOR = [
    '.stat-card',
    '.article-card',
    '.category-card',
    '.section-header',
    '.featured-section',
    '.categories-section',
    '.hero-section',
    '.recent-changes-section',
    '.auth-box',
    '.auth-info',
    '.search-results-section',
    '.article-header',
    '.article-content',
    '.article-sidebar',
    '.profile-header',
    '.empty-state',
    '.roadmap-hero',
    '.roadmap-cta',
  ].join(',');

  function initReveals() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var delay = parseInt(entry.target.dataset.gwDelay, 10) || 0;
          setTimeout(function() {
            entry.target.classList.add('gw-visible');
          }, delay);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.06, rootMargin: '0px 0px -30px 0px' });

    var elements = document.querySelectorAll(REVEAL_SELECTOR);
    var parentMap = new Map();

    elements.forEach(function(el) {
      // Skip elements already revealed (e.g. after page transition)
      if (el.classList.contains('gw-visible')) return;
      el.classList.add('gw-reveal');
      var parent = el.parentElement;
      if (!parentMap.has(parent)) parentMap.set(parent, 0);
      var index = parentMap.get(parent);
      el.dataset.gwDelay = index * 60;
      parentMap.set(parent, index + 1);
      observer.observe(el);
    });
  }

  // ── Click ripple feedback ──
  function initClickFeedback() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.addEventListener('mousedown', function(e) {
      var target = e.target.closest('.button, .button-primary, .button-secondary, .auth-button, .search-button, .search-button-lg');
      if (!target) return;
      target.classList.add('gw-pressing');
    });

    document.addEventListener('mouseup', function() {
      document.querySelectorAll('.gw-pressing').forEach(function(el) {
        el.classList.remove('gw-pressing');
      });
    });
  }

  // Expose initReveals globally so the page transition engine can re-run it
  window.__gw = window.__gw || {};
  window.__gw.initReveals = initReveals;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initReveals();
      initClickFeedback();
    });
  } else {
    initReveals();
    initClickFeedback();
  }
})();

// ============================================================
// Page Transition Engine — Fetch + DOM Swap with Crossfade
// ============================================================
(function() {
  var TRANSITION_MS = 250; // per manifesto: 250ms ease-in-out crossfade
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isTransitioning = false;

  // ── Progress bar ──
  var progressBar = document.createElement('div');
  progressBar.className = 'gw-progress-bar';
  document.body.appendChild(progressBar);

  function showProgress() {
    progressBar.classList.add('gw-progress-active');
  }

  function hideProgress() {
    progressBar.classList.add('gw-progress-done');
    setTimeout(function() {
      progressBar.classList.remove('gw-progress-active', 'gw-progress-done');
    }, 300);
  }

  // ── Skeleton loader ──
  function showSkeleton(main) {
    main.innerHTML =
      '<div class="gw-skeleton-page">' +
        '<div class="gw-skeleton-block gw-skeleton-title"></div>' +
        '<div class="gw-skeleton-block gw-skeleton-text"></div>' +
        '<div class="gw-skeleton-block gw-skeleton-text short"></div>' +
        '<div class="gw-skeleton-block gw-skeleton-text"></div>' +
        '<div class="gw-skeleton-grid">' +
          '<div class="gw-skeleton-block gw-skeleton-card"></div>' +
          '<div class="gw-skeleton-block gw-skeleton-card"></div>' +
          '<div class="gw-skeleton-block gw-skeleton-card"></div>' +
        '</div>' +
      '</div>';
  }

  // ── Should we intercept this click? ──
  function shouldIntercept(anchor) {
    // External links
    if (anchor.origin !== window.location.origin) return false;
    // New tab / download / special attrs
    if (anchor.target === '_blank' || anchor.hasAttribute('download')) return false;
    // Hash-only links on same page
    if (anchor.pathname === window.location.pathname && anchor.hash) return false;
    // Logout, admin actions, API calls, explore (needs full page load)
    if (/\/(logout|api\/|static\/|explore)/.test(anchor.pathname)) return false;
    // Don't intercept if there's an unsaved edit form
    if (document.querySelector('form[data-edit-form]')) {
      var formInputs = document.querySelectorAll('form[data-edit-form] input, form[data-edit-form] textarea');
      for (var i = 0; i < formInputs.length; i++) {
        if (formInputs[i].dataset.changed === 'true') return false;
      }
    }
    return true;
  }

  // ── Perform the transition ──
  function navigateTo(url, pushState) {
    if (isTransitioning) return;
    isTransitioning = true;

    var main = document.querySelector('main.main-content');
    if (!main) { window.location.href = url; return; }

    var duration = reducedMotion ? 0 : TRANSITION_MS;

    showProgress();

    // Fade out current content
    main.style.transition = duration ? ('opacity ' + duration + 'ms ease-in-out') : 'none';
    main.style.opacity = '0';

    // After fade-out, show skeleton & fetch
    setTimeout(function() {
      showSkeleton(main);
      main.style.opacity = '1';

      fetch(url, { headers: { 'X-Requested-With': 'GWTransition' } })
        .then(function(response) {
          if (!response.ok) throw new Error(response.status);
          return response.text();
        })
        .then(function(html) {
          var parser = new DOMParser();
          var doc = parser.parseFromString(html, 'text/html');
          var newMain = doc.querySelector('main.main-content');
          var newTitle = doc.querySelector('title');

          if (!newMain) {
            // Fallback: full page load
            window.location.href = url;
            return;
          }

          // Fade out skeleton
          main.style.opacity = '0';

          setTimeout(function() {
            // Swap content and execute inline scripts
            main.innerHTML = newMain.innerHTML;
            main.querySelectorAll('script').forEach(function(oldScript) {
              // Skip non-JS scripts (JSON-LD, etc.)
              var scriptType = (oldScript.type || '').toLowerCase();
              if (scriptType && scriptType !== 'text/javascript' && scriptType !== 'module') return;
              var newScript = document.createElement('script');
              if (oldScript.src) {
                newScript.src = oldScript.src;
              } else {
                newScript.textContent = oldScript.textContent;
              }
              oldScript.parentNode.replaceChild(newScript, oldScript);
            });

            // Update title
            if (newTitle) document.title = newTitle.textContent;

            // Update URL
            if (pushState !== false) {
              window.history.pushState({ gwTransition: true }, '', url);
            }

            // Update active nav link
            updateActiveNav(url);

            // Fade in new content
            main.style.opacity = '1';

            // Re-initialize dynamic features on new content
            setTimeout(function() {
              main.style.transition = '';
              main.style.opacity = '';
              reinitPage();
              hideProgress();
              isTransitioning = false;
              window.scrollTo({ top: 0, behavior: reducedMotion ? 'auto' : 'smooth' });
            }, duration);
          }, duration);
        })
        .catch(function() {
          hideProgress();
          isTransitioning = false;
          window.location.href = url;
        });
    }, duration);
  }

  // ── Highlight the current nav link ──
  function updateActiveNav(url) {
    var path = new URL(url, window.location.origin).pathname;
    document.querySelectorAll('.navbar-link').forEach(function(link) {
      link.classList.remove('active');
      if (link.getAttribute('href') === path) {
        link.classList.add('active');
      }
    });
  }

  // ── Re-init JS features after content swap ──
  function reinitPage() {
    // Re-run scroll reveals on new content
    if (window.__gw && window.__gw.initReveals) {
      window.__gw.initReveals();
    }
    // Re-init TOC if present
    var tocContainer = document.querySelector('.toc ul');
    var articleContent = document.querySelector('.article-body');
    if (tocContainer && articleContent) {
      generateTOC(tocContainer, articleContent);
    }
    // Re-init search autocomplete stagger
    initSearchAutocompleteAnimation();
    // Re-bind smooth scroll anchors
    bindSmoothScrollAnchors();
    // Fire a custom event so other scripts can hook in
    document.dispatchEvent(new CustomEvent('gw:pageload'));
  }

  // ── Click handler ──
  document.addEventListener('click', function(e) {
    // Ignore modified clicks (new tab, etc.)
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button !== 0) return;

    var anchor = e.target.closest('a[href]');
    if (!anchor) return;
    if (!shouldIntercept(anchor)) return;

    e.preventDefault();
    navigateTo(anchor.href, true);
  });

  // ── Back/Forward navigation ──
  window.addEventListener('popstate', function() {
    navigateTo(window.location.href, false);
  });

  // Mark initial page state
  window.history.replaceState({ gwTransition: true }, '');
})();

// ============================================================
// Search Autocomplete — Staggered Fade Animation
// ============================================================
function initSearchAutocompleteAnimation() {
  // Observe the autocomplete container for new children
  var container = document.querySelector('.search-autocomplete');
  if (!container) return;
  if (container._gwObserver) return; // already watching

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var mo = new MutationObserver(function(mutations) {
    mutations.forEach(function(m) {
      if (m.type !== 'childList' || !m.addedNodes.length) return;
      var items = container.querySelectorAll('.search-autocomplete-item');
      items.forEach(function(item, i) {
        if (reducedMotion) {
          item.style.opacity = '1';
          return;
        }
        item.classList.add('gw-ac-enter');
        item.style.animationDelay = (i * 50) + 'ms';
      });
    });
  });

  mo.observe(container, { childList: true });
  container._gwObserver = mo;
}

// Run on initial load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSearchAutocompleteAnimation);
} else {
  initSearchAutocompleteAnimation();
}

// ============================================================
// Collapsible Module Toggles
// ============================================================
function initCollapsibleModules() {
  document.querySelectorAll('.gw-module-toggle').forEach(function(btn) {
    if (btn._gwBound) return;
    btn._gwBound = true;

    btn.addEventListener('click', function() {
      var expanded = this.getAttribute('aria-expanded') === 'true';
      var targetId = this.getAttribute('aria-controls');
      var body = targetId ? document.getElementById(targetId) : this.nextElementSibling;

      if (!body) return;

      if (expanded) {
        body.classList.add('collapsed');
        this.setAttribute('aria-expanded', 'false');
      } else {
        body.classList.remove('collapsed');
        this.setAttribute('aria-expanded', 'true');
      }
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCollapsibleModules);
} else {
  initCollapsibleModules();
}

// Re-init collapsibles after page transitions
document.addEventListener('gw:pageload', initCollapsibleModules);

// ============================================================
// Mobile Hamburger Menu
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  var hamburger = document.querySelector('.navbar-toggle');
  var navMenu = document.querySelector('.navbar-menu');

  if (hamburger && navMenu) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      navMenu.classList.toggle('active');
    });

    // Close menu when a link is clicked
    navMenu.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.navbar-toggle') && !event.target.closest('.navbar-menu')) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
      }
    });
  }

  // ── User Menu Dropdown ──
  var userTrigger = document.querySelector('.user-menu-trigger');
  var userDropdown = document.querySelector('.user-menu-dropdown');

  if (userTrigger && userDropdown) {
    userTrigger.addEventListener('click', function(e) {
      e.stopPropagation();
      userDropdown.classList.toggle('active');
      userTrigger.setAttribute('aria-expanded', userDropdown.classList.contains('active'));
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.user-menu')) {
        userDropdown.classList.remove('active');
        userTrigger.setAttribute('aria-expanded', 'false');
      }
    });
  }
});

// ============================================================
// Simple Markdown to HTML Converter (Client-side Preview)
// ============================================================
const MarkdownPreview = {
  /**
   * Convert markdown to HTML
   */
  convert: function(markdown) {
    if (!markdown) return '';

    let html = markdown;

    // Code blocks (triple backticks)
    html = html.replace(/```([^`]*?)```/gs, function(match, code) {
      const language = code.split('\n')[0];
      const codeContent = code.replace(language + '\n', '').trim();
      return '<pre><code class="language-' + language + '">' +
             this.escapeHtml(codeContent) + '</code></pre>';
    }.bind(this));

    // Inline code
    html = html.replace(/`([^`]+?)`/g, '<code>$1</code>');

    // Headings
    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

    // Blockquotes
    html = html.replace(/^> (.*?)$/gm, '<blockquote>$1</blockquote>');

    // Unordered lists
    html = html.replace(/^\* (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/^\- (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*?<\/li>)/s, function(match) {
      if (!match.includes('<ul>')) {
        return '<ul>' + match + '</ul>';
      }
      return match;
    });

    // Ordered lists
    html = html.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr>');

    return html;
  },

  escapeHtml: function(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }
};

// ============================================================
// Markdown Editor with Live Preview
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const contentTextarea = document.querySelector('textarea[name="content"]');
  const previewSection = document.querySelector('.markdown-preview');

  if (contentTextarea && previewSection) {
    // Update preview on input
    contentTextarea.addEventListener('input', function() {
      const markdown = this.value;
      const html = MarkdownPreview.convert(markdown);
      previewSection.innerHTML = html;
    });

    // Initial preview
    const initialHtml = MarkdownPreview.convert(contentTextarea.value);
    previewSection.innerHTML = initialHtml;

    // Editor toolbar buttons
    const toolbarBtns = document.querySelectorAll('.toolbar-btn');
    toolbarBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        insertMarkdown(this.dataset.format);
      });
    });
  }

  function insertMarkdown(format) {
    const textarea = contentTextarea;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    let insertText = '';

    switch(format) {
      case 'bold':
        insertText = `**${selectedText || 'bold text'}**`;
        break;
      case 'italic':
        insertText = `*${selectedText || 'italic text'}*`;
        break;
      case 'code':
        insertText = `\`${selectedText || 'code'}\``;
        break;
      case 'codeblock':
        insertText = `\`\`\`\n${selectedText || 'code'}\n\`\`\``;
        break;
      case 'heading':
        insertText = `## ${selectedText || 'Heading'}`;
        break;
      case 'quote':
        insertText = `> ${selectedText || 'Quote'}`;
        break;
      case 'link':
        insertText = `[${selectedText || 'Link text'}](URL)`;
        break;
      case 'list':
        insertText = `* Item 1\n* Item 2\n* Item 3`;
        break;
      default:
        return;
    }

    textarea.value = textarea.value.substring(0, start) + insertText +
                     textarea.value.substring(end);

    // Update preview
    const html = MarkdownPreview.convert(textarea.value);
    previewSection.innerHTML = html;
  }
});

// ============================================================
// Auto-generate Table of Contents from Article Headings
// ============================================================
function generateTOC(tocContainer, articleContent) {
  var headings = articleContent.querySelectorAll('h2, h3, h4');
  var toc = [];
  var currentH2 = null;
  var currentH3 = null;

  headings.forEach(function(heading, index) {
    if (!heading.id) heading.id = 'heading-' + index;
    var level = parseInt(heading.tagName[1]);
    var text = heading.textContent;

    if (level === 2) {
      currentH2 = { text: text, id: heading.id, children: [] };
      toc.push(currentH2);
    } else if (level === 3 && currentH2) {
      currentH3 = { text: text, id: heading.id, children: [] };
      currentH2.children.push(currentH3);
    } else if (level === 4 && currentH3) {
      currentH3.children.push({ text: text, id: heading.id });
    }
  });

  var html = '';
  toc.forEach(function(item) {
    html += '<li><a href="#' + item.id + '">' + item.text + '</a>';
    if (item.children.length > 0) {
      html += '<ul>';
      item.children.forEach(function(child) {
        html += '<li><a href="#' + child.id + '">' + child.text + '</a>';
        if (child.children && child.children.length > 0) {
          html += '<ul>';
          child.children.forEach(function(sub) {
            html += '<li><a href="#' + sub.id + '">' + sub.text + '</a></li>';
          });
          html += '</ul>';
        }
        html += '</li>';
      });
      html += '</ul>';
    }
    html += '</li>';
  });
  tocContainer.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
  var tocContainer = document.querySelector('.toc ul');
  var articleContent = document.querySelector('.article-body');
  if (tocContainer && articleContent) generateTOC(tocContainer, articleContent);
});

// ============================================================
// Search Autocomplete
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('nav .search-bar input');

  if (searchInput) {
    let autocompleteTimeout;
    const autocompleteContainer = document.querySelector('.search-autocomplete');

    searchInput.addEventListener('input', function() {
      clearTimeout(autocompleteTimeout);
      const query = this.value.trim();

      if (query.length < 2) {
        if (autocompleteContainer) {
          autocompleteContainer.innerHTML = '';
        }
        return;
      }

      autocompleteTimeout = setTimeout(() => {
        fetchSearchSuggestions(query);
      }, 300);
    });

    // Close autocomplete when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.search-bar')) {
        if (autocompleteContainer) {
          autocompleteContainer.innerHTML = '';
        }
      }
    });
  }

  function fetchSearchSuggestions(query) {
    const autocompleteContainer = document.querySelector('.search-autocomplete');
    if (!autocompleteContainer) return;

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        if (!data.results || data.results.length === 0) {
          autocompleteContainer.innerHTML = '<div class="search-autocomplete-item">No results found</div>';
          return;
        }

        let html = '';
        data.results.slice(0, 8).forEach(result => {
          html += `<a href="${result.url}" class="search-autocomplete-item">${result.title}</a>`;
        });

        autocompleteContainer.innerHTML = html;
      })
      .catch(error => {
        console.error('Search error:', error);
      });
  }
});

// ============================================================
// Slug Auto-generation from Title
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const titleInput = document.querySelector('input[name="title"]');
  const slugDisplay = document.querySelector('[data-slug-display]');

  if (titleInput) {
    titleInput.addEventListener('input', function() {
      const slug = generateSlug(this.value);
      if (slugDisplay) {
        slugDisplay.textContent = slug;
      }
    });
  }

  function generateSlug(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-+|-+$/g, '');
  }
});

// ============================================================
// Confirm Before Leaving Edit Page with Unsaved Changes
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const editForm = document.querySelector('form[data-edit-form]');

  if (editForm) {
    let formChanged = false;
    const formInputs = editForm.querySelectorAll('input, textarea, select');

    formInputs.forEach(input => {
      input.addEventListener('change', function() {
        formChanged = true;
      });
    });

    // Save form initial state
    const formData = new FormData(editForm);
    const initialData = Object.fromEntries(formData);

    // Listen for form submission
    editForm.addEventListener('submit', function() {
      formChanged = false;
    });

    // Warn before leaving
    window.addEventListener('beforeunload', function(e) {
      if (formChanged) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    });
  }
});

// ============================================================
// Smooth Scroll to Anchors
// ============================================================
function bindSmoothScrollAnchors() {
  var main = document.querySelector('main.main-content');
  if (!main) return;
  var links = main.querySelectorAll('a[href^="#"]');

  links.forEach(function(link) {
    // Avoid double-binding
    if (link._gwSmooth) return;
    link._gwSmooth = true;

    link.addEventListener('click', function(e) {
      var href = this.getAttribute('href');
      if (href === '#') return;
      var target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      var nav = document.querySelector('.navbar');
      var headerH = nav ? nav.offsetHeight : 0;
      var pos = target.getBoundingClientRect().top + window.pageYOffset - headerH - 20;
      window.scrollTo({ top: pos, behavior: 'smooth' });
      window.history.pushState(null, null, href);
    });
  });
}

document.addEventListener('DOMContentLoaded', bindSmoothScrollAnchors);

// ============================================================
// Revision Checkbox Selection for Diff Comparison
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const revisionCheckboxes = document.querySelectorAll('input[name="revisions"]');
  const compareBtn = document.querySelector('button[data-compare-revisions]');

  if (revisionCheckboxes.length > 0 && compareBtn) {
    revisionCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        const checkedCount = document.querySelectorAll('input[name="revisions"]:checked').length;

        // Disable checkboxes if 2 are already selected
        if (checkedCount === 2) {
          revisionCheckboxes.forEach(cb => {
            if (!cb.checked) {
              cb.disabled = true;
            }
          });
          compareBtn.disabled = false;
        } else {
          revisionCheckboxes.forEach(cb => {
            cb.disabled = false;
          });
        }

        // Disable compare button if not exactly 2 selected
        compareBtn.disabled = checkedCount !== 2;
      });
    });

    compareBtn.addEventListener('click', function() {
      const selected = Array.from(revisionCheckboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

      if (selected.length === 2) {
        const [rev1, rev2] = selected;
        const articleId = document.querySelector('[data-article-id]').dataset.articleId;
        window.location.href = `/article/${articleId}/diff?rev1=${rev1}&rev2=${rev2}`;
      }
    });
  }
});

// ============================================================
// Flash Message Auto-dismiss
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const alerts = document.querySelectorAll('.alert');

  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');

    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        alert.style.animation = 'slideDown 0.3s ease reverse';
        setTimeout(() => {
          alert.remove();
        }, 300);
      });
    }

    // Auto-dismiss success messages after 5 seconds
    if (alert.classList.contains('alert-success')) {
      setTimeout(() => {
        if (alert.parentElement) {
          alert.style.animation = 'slideDown 0.3s ease reverse';
          setTimeout(() => {
            alert.remove();
          }, 300);
        }
      }, 5000);
    }
  });
});

// Init taxonomy scroll reveals on categories page
document.addEventListener('DOMContentLoaded', function() {
  if (typeof GWWiki !== 'undefined' && GWWiki.initTaxonomyReveals) {
    GWWiki.initTaxonomyReveals();
  }
});

// ============================================================
// Form Validation Helpers
// ============================================================
const FormValidator = {
  validateEmail: function(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  validatePassword: function(password) {
    return password.length >= 8;
  },

  validateUsername: function(username) {
    const re = /^[a-zA-Z0-9_-]{3,20}$/;
    return re.test(username);
  },

  validateUrl: function(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
};

// ============================================================
// Utility Functions
// ============================================================
const WikiUtils = {
  /**
   * Copy text to clipboard
   */
  copyToClipboard: function(text) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        this.showNotification('Copied to clipboard', 'success');
      });
    }
  },

  /**
   * Show temporary notification
   */
  showNotification: function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    document.body.insertBefore(notification, document.body.firstChild);

    setTimeout(() => {
      notification.style.animation = 'slideDown 0.3s ease reverse';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  },

  /**
   * Debounce function
   */
  debounce: function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Format date
   */
  formatDate: function(date) {
    if (typeof date === 'string') {
      date = new Date(date);
    }
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  },

  /**
   * Taxonomy page: staggered scroll-reveal for tier sections.
   * Only activates when .tax-page is present and user allows motion.
   */
  initTaxonomyReveals: function() {
    if (!document.querySelector('.tax-page')) return;
    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var tiers = document.querySelectorAll('.tax-tier');
    if (prefersReduced) {
      tiers.forEach(function(t) { t.classList.add('tax-visible'); });
      return;
    }
    if (!('IntersectionObserver' in window)) {
      tiers.forEach(function(t) { t.classList.add('tax-visible'); });
      return;
    }
    var stagger = 0;
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var delay = stagger * 60;
          stagger++;
          setTimeout(function() {
            entry.target.classList.add('tax-visible');
          }, delay);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    tiers.forEach(function(t) { observer.observe(t); });
  }
};

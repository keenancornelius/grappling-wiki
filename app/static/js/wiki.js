/**
 * GrapplingWiki - Main JavaScript
 * Handles interactive features, animations, and the wiki editor.
 */

// ============================================================
// Animation System — Scroll Reveals & Click Feedback
// ============================================================
(function() {
  // ── Scroll-triggered module reveals ──
  // Elements with .gw-reveal fade/slide in when they enter the viewport.
  // Stagger delay is set via data-gw-delay or auto-calculated for siblings.
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

    const observer = new IntersectionObserver(function(entries) {
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
      el.classList.add('gw-reveal');
      // Auto-stagger siblings
      var parent = el.parentElement;
      if (!parentMap.has(parent)) parentMap.set(parent, 0);
      var index = parentMap.get(parent);
      el.dataset.gwDelay = index * 60;
      parentMap.set(parent, index + 1);
      observer.observe(el);
    });
  }

  // ── Click ripple feedback ──
  // A subtle scale pulse on click for buttons and interactive elements.
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
// Mobile Hamburger Menu
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('nav ul');

  if (hamburger) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      navMenu.classList.toggle('active');
    });

    // Close menu when a link is clicked
    const navLinks = navMenu.querySelectorAll('a');
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('nav')) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
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
document.addEventListener('DOMContentLoaded', function() {
  const tocContainer = document.querySelector('.toc ul');
  const articleContent = document.querySelector('.article-content');

  if (tocContainer && articleContent) {
    generateTableOfContents();
  }

  function generateTableOfContents() {
    const headings = articleContent.querySelectorAll('h2, h3, h4');
    const toc = [];
    let currentH2 = null;
    let currentH3 = null;

    headings.forEach((heading, index) => {
      if (!heading.id) {
        heading.id = 'heading-' + index;
      }

      const level = parseInt(heading.tagName[1]);
      const text = heading.textContent;

      if (level === 2) {
        currentH2 = { text, id: heading.id, children: [] };
        toc.push(currentH2);
      } else if (level === 3 && currentH2) {
        currentH3 = { text, id: heading.id, children: [] };
        currentH2.children.push(currentH3);
      } else if (level === 4 && currentH3) {
        currentH3.children.push({ text, id: heading.id });
      }
    });

    // Build HTML
    let tocHtml = '';
    toc.forEach(item => {
      tocHtml += `<li><a href="#${item.id}">${item.text}</a>`;
      if (item.children.length > 0) {
        tocHtml += '<ul>';
        item.children.forEach(child => {
          tocHtml += `<li><a href="#${child.id}">${child.text}</a>`;
          if (child.children && child.children.length > 0) {
            tocHtml += '<ul>';
            child.children.forEach(subchild => {
              tocHtml += `<li><a href="#${subchild.id}">${subchild.text}</a></li>`;
            });
            tocHtml += '</ul>';
          }
          tocHtml += '</li>';
        });
        tocHtml += '</ul>';
      }
      tocHtml += '</li>';
    });

    tocContainer.innerHTML = tocHtml;
  }
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
document.addEventListener('DOMContentLoaded', function() {
  const links = document.querySelectorAll('a[href^="#"]');

  links.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      const target = document.querySelector(href);
      if (!target) return;

      e.preventDefault();

      const headerHeight = document.querySelector('header').offsetHeight;
      const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });

      // Update URL without page reload
      window.history.pushState(null, null, href);
    });
  });
});

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
  }
};

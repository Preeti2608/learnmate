/**
 * LearnMate – Main JavaScript
 * Dark mode toggle, scroll animations, navbar, global utilities
 */

// ── Dark Mode ────────────────────────────────────────────────────────────────

(function initTheme() {
  const stored = localStorage.getItem('lm-theme') || 'light';
  applyTheme(stored);
})();

function applyTheme(theme) {
  document.documentElement.setAttribute('data-bs-theme', theme);
  const icon = document.getElementById('themeIcon');
  if (icon) {
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
  }
  localStorage.setItem('lm-theme', theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

document.addEventListener('DOMContentLoaded', () => {
  const switcher = document.getElementById('themeSwitcher');
  if (switcher) switcher.addEventListener('click', toggleTheme);
});

// ── Scroll animations (Intersection Observer) ────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const targets = document.querySelectorAll('.animate-on-scroll');
  if (!targets.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          const delay = entry.target.style.getPropertyValue('--delay') || (i * 80) + 'ms';
          setTimeout(() => entry.target.classList.add('visible'), parseInt(delay));
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  targets.forEach(el => observer.observe(el));
});

// ── Navbar shrink on scroll ──────────────────────────────────────────────────

window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.lm-navbar');
  if (!navbar) return;
  navbar.classList.toggle('lm-navbar-scrolled', window.scrollY > 30);
});

// ── Auto-dismiss alerts ──────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.lm-alert').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});

// ── Global utility: format timestamp ────────────────────────────────────────

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

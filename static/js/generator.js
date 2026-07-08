/**
 * LearnMate – AI Content Generator JavaScript
 * Shared by: roadmap, skill_gap, courses, weekly_plan, projects, career pages
 *
 * Expects `const SECTION = "..."` to be defined in the embedding page's <script> tag.
 */

const generateBtn    = document.getElementById('generateBtn');
const loadingState   = document.getElementById('loadingState');
const resultContainer = document.getElementById('resultContainer');
const aiContent      = document.getElementById('aiContent');

// Loading step elements (optional – only present on generation pages)
const steps = [
  document.getElementById('step1'),
  document.getElementById('step2'),
  document.getElementById('step3'),
  document.getElementById('step4'),
];

// ── Markdown-lite renderer (reused from chat.js concept) ─────────────────────

function renderMarkdown(text) {
  return text
    .replace(/^### (.+)$/gm, '<h5 class="mt-3 mb-1 fw-bold lm-heading-h5">$1</h5>')
    .replace(/^## (.+)$/gm,  '<h4 class="mt-4 mb-2 fw-bold lm-heading-h4">$1</h4>')
    .replace(/^# (.+)$/gm,   '<h3 class="mt-4 mb-2 fw-bold">$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,     '<em>$1</em>')
    .replace(/`([^`]+)`/g,     '<code>$1</code>')
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm,'<li>$2</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, m => `<ul class="mb-2">${m}</ul>`)
    .replace(/^---+$/gm,       '<hr class="my-3"/>')
    .replace(/\n{2,}/g, '</p><p class="mb-2">')
    .replace(/\n/g, '<br/>');
}

// ── Loading step animation ────────────────────────────────────────────────────

let stepTimers = [];

function startLoadingSteps() {
  steps.forEach(s => { if (s) { s.classList.remove('active', 'done'); } });
  if (steps[0]) steps[0].classList.add('active');

  const delays = [0, 1200, 2400, 3600];
  stepTimers = delays.map((delay, i) => {
    return setTimeout(() => {
      if (steps[i - 1]) { steps[i - 1].classList.remove('active'); steps[i - 1].classList.add('done'); }
      if (steps[i])     { steps[i].classList.add('active'); }
    }, delay);
  });
}

function clearLoadingSteps() {
  stepTimers.forEach(t => clearTimeout(t));
  steps.forEach(s => { if (s) s.classList.remove('active', 'done'); });
}

// ── Main generate function ────────────────────────────────────────────────────

async function generateContent() {
  // Show loading
  generateBtn.disabled = true;
  generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
  resultContainer.classList.add('d-none');
  loadingState.classList.remove('d-none');
  startLoadingSteps();

  try {
    const response = await fetch(`/api/generate/${SECTION}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await response.json();

    clearLoadingSteps();
    loadingState.classList.add('d-none');

    if (data.error) {
      showError(data.error);
    } else {
      // Render the AI response
      const parsed = renderMarkdown(data.content);
      aiContent.innerHTML = `<p class="mb-2">${parsed}</p>`;
      resultContainer.classList.remove('d-none');
      // Smooth scroll to result
      resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } catch (err) {
    clearLoadingSteps();
    loadingState.classList.add('d-none');
    showError('Network error. Please check your connection and try again.');
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Regenerate';
  }
}

// ── Error display ─────────────────────────────────────────────────────────────

function showError(message) {
  aiContent.innerHTML = `
    <div class="alert alert-danger border-0 rounded-3 d-flex align-items-center gap-2">
      <i class="bi bi-exclamation-triangle-fill flex-shrink-0"></i>
      <div>
        <strong>Error:</strong> ${message}
        <br/><small class="text-muted">Make sure your IBM API credentials are correctly set in <code>.env</code>.</small>
      </div>
    </div>`;
  resultContainer.classList.remove('d-none');
}

// ── Copy to clipboard ─────────────────────────────────────────────────────────

function copyResult() {
  const text = aiContent.innerText || aiContent.textContent;
  navigator.clipboard.writeText(text).then(() => {
    // Brief visual feedback
    const btn = document.querySelector('[onclick="copyResult()"]');
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Copied!';
      btn.classList.add('btn-success');
      setTimeout(() => { btn.innerHTML = orig; btn.classList.remove('btn-success'); }, 2000);
    }
  }).catch(() => {
    alert('Copy failed. Please select and copy manually.');
  });
}

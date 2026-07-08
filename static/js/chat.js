/**
 * LearnMate – Chat Assistant JavaScript
 * Handles: sending messages, rendering responses, suggestion chips, auto-resize textarea
 */

const chatWindow  = document.getElementById('chatWindow');
const chatInput   = document.getElementById('chatInput');
const sendBtn     = document.getElementById('sendBtn');
const typingEl    = document.getElementById('typingIndicator');
const messagesEl  = document.getElementById('chatMessages');

// ── Markdown-lite renderer ───────────────────────────────────────────────────

function renderMarkdown(text) {
  return text
    // Headings
    .replace(/^### (.+)$/gm, '<h5 class="mt-3 mb-2 fw-bold">$1</h5>')
    .replace(/^## (.+)$/gm,  '<h4 class="mt-3 mb-2 fw-bold">$1</h4>')
    .replace(/^# (.+)$/gm,   '<h3 class="mt-3 mb-2 fw-bold">$1</h3>')
    // Bold and italic
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,     '<em>$1</em>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Unordered lists
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    // Ordered lists – wrap consecutive <li> elements
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    // Wrap naked li runs in <ul>
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    // Horizontal rule
    .replace(/^---+$/gm, '<hr/>')
    // Line breaks
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/\n/g, '<br/>');
}

// ── Append a message bubble ──────────────────────────────────────────────────

function appendMessage(role, text) {
  const isUser = role === 'user';
  const wrapper = document.createElement('div');
  wrapper.className = `lm-msg ${isUser ? 'lm-msg-user' : 'lm-msg-ai'} animate-fade-up`;

  const avatar = document.createElement('div');
  avatar.className = 'lm-msg-avatar';
  avatar.innerHTML = isUser
    ? '<i class="bi bi-person-fill"></i>'
    : '<i class="bi bi-robot"></i>';

  const body = document.createElement('div');
  body.className = 'lm-msg-body';

  const bubble = document.createElement('div');
  bubble.className = 'lm-msg-bubble';

  if (isUser) {
    bubble.textContent = text;
  } else {
    // Render AI response as formatted HTML
    const parsed = renderMarkdown(text);
    bubble.innerHTML = `<div class="lm-ai-content"><p>${parsed}</p></div>`;
  }

  const timeEl = document.createElement('span');
  timeEl.className = 'lm-msg-time';
  timeEl.textContent = formatTime(new Date());

  body.appendChild(bubble);
  body.appendChild(timeEl);
  wrapper.appendChild(avatar);
  wrapper.appendChild(body);

  messagesEl.appendChild(wrapper);
  scrollToBottom();
}

// ── Scroll helpers ───────────────────────────────────────────────────────────

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Typing indicator ─────────────────────────────────────────────────────────

function showTyping() {
  typingEl.classList.remove('d-none');
  scrollToBottom();
}

function hideTyping() {
  typingEl.classList.add('d-none');
}

// ── Send message ─────────────────────────────────────────────────────────────

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  // Render user bubble immediately
  appendMessage('user', text);

  // Clear input, disable controls
  chatInput.value = '';
  autoResizeTextarea();
  sendBtn.disabled = true;
  showTyping();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    const data = await response.json();
    hideTyping();

    if (data.error) {
      appendMessage('assistant', `⚠️ Error: ${data.error}`);
    } else {
      appendMessage('assistant', data.reply);
    }
  } catch (err) {
    hideTyping();
    appendMessage('assistant', '⚠️ Network error. Please check your connection and try again.');
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

// ── Suggestion chip handler ──────────────────────────────────────────────────

function sendSuggestion(btn) {
  chatInput.value = btn.textContent.trim();
  sendMessage();
}

// ── Keyboard handler ─────────────────────────────────────────────────────────

function handleChatKey(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// ── Auto-resize textarea ──────────────────────────────────────────────────────

function autoResizeTextarea() {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + 'px';
}

// ── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  if (chatInput) {
    chatInput.addEventListener('input', autoResizeTextarea);
    chatInput.focus();
  }
  scrollToBottom();
});

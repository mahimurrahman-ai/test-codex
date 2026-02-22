const root = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const resetButton = document.getElementById('resetProgress');
const filter = document.getElementById('focusFilter');
const checks = [...document.querySelectorAll('.month-check')];
const cards = [...document.querySelectorAll('.month')];
const progressText = document.getElementById('progressText');
const progressFill = document.getElementById('progressFill');

const THEME_KEY = 'roadmap-theme';
const PROGRESS_KEY = 'roadmap-progress';

function loadTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === 'light') root.classList.add('light');
}

function saveTheme() {
  const isLight = root.classList.contains('light');
  localStorage.setItem(THEME_KEY, isLight ? 'light' : 'dark');
}

function loadProgress() {
  const saved = JSON.parse(localStorage.getItem(PROGRESS_KEY) || '{}');
  checks.forEach((check) => {
    check.checked = Boolean(saved[check.dataset.month]);
  });
  updateProgress();
}

function saveProgress() {
  const payload = {};
  checks.forEach((check) => {
    payload[check.dataset.month] = check.checked;
  });
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(payload));
}

function updateProgress() {
  const complete = checks.filter((c) => c.checked).length;
  const total = checks.length;
  const percent = Math.round((complete / total) * 100);
  progressText.textContent = `${complete} / ${total} complete (${percent}%)`;
  progressFill.style.width = `${percent}%`;
}

function applyFilter() {
  const value = filter.value;
  cards.forEach((card) => {
    if (value === 'all') {
      card.classList.remove('hidden');
      return;
    }

    const focus = (card.dataset.focus || '').split(' ');
    if (focus.includes(value)) {
      card.classList.remove('hidden');
    } else {
      card.classList.add('hidden');
    }
  });
}

checks.forEach((check) => {
  check.addEventListener('change', () => {
    saveProgress();
    updateProgress();
  });
});

filter.addEventListener('change', applyFilter);

resetButton.addEventListener('click', () => {
  checks.forEach((check) => { check.checked = false; });
  saveProgress();
  updateProgress();
});

themeToggle.addEventListener('click', () => {
  root.classList.toggle('light');
  saveTheme();
});

loadTheme();
loadProgress();
applyFilter();

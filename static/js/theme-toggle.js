// ===== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ =====

function initTheme() {
  const savedTheme = localStorage.getItem('mindflow-theme') || 'dark';
  applyTheme(savedTheme);
  updateThemeButton();
}

function applyTheme(theme) {
  if (theme === 'light') {
    document.body.classList.add('light-theme');
    localStorage.setItem('mindflow-theme', 'light');
  } else {
    document.body.classList.remove('light-theme');
    localStorage.setItem('mindflow-theme', 'dark');
  }
  updateThemeButton();
}

function toggleTheme() {
  const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  applyTheme(newTheme);
}

function updateThemeButton() {
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) {
    const isDarkMode = !document.body.classList.contains('light-theme');
    btn.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    btn.title = isDarkMode ? 'Светлая тема' : 'Тёмная тема';
  }
}

// Инициализация при загрузке страницы
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTheme);
} else {
  initTheme();
}

// ===== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ =====

function initTheme() {
  const savedTheme = localStorage.getItem('mindflow-theme') || 'light';
  applyTheme(savedTheme);
  updateThemeRadios();
}

function applyTheme(theme) {
  if (theme === 'light') {
    document.body.classList.add('light-theme');
    localStorage.setItem('mindflow-theme', 'light');
  } else {
    document.body.classList.remove('light-theme');
    localStorage.setItem('mindflow-theme', 'dark');
  }
  updateThemeRadios();
}

function updateThemeRadios() {
  const isDarkMode = !document.body.classList.contains('light-theme');
  const lightRadio = document.getElementById('themeLight');
  const darkRadio = document.getElementById('themeDark');
  
  if (lightRadio && darkRadio) {
    lightRadio.checked = !isDarkMode;
    darkRadio.checked = isDarkMode;
  }
}

function openThemeDialog(event) {
  event.preventDefault();
  event.stopPropagation();
  const dialog = document.getElementById('themeDialog');
  if (dialog) {
    updateThemeRadios();
    dialog.style.display = 'flex';
    document.getElementById('profileOverlay').classList.remove('active');
  }
}

function closeThemeDialog() {
  const dialog = document.getElementById('themeDialog');
  if (dialog) {
    dialog.style.display = 'none';
  }
}

// Закрытие диалога при клике вне его
document.addEventListener('click', function(event) {
  const dialog = document.getElementById('themeDialog');
  const dialogContent = document.querySelector('.theme-dialog-content');
  
  if (dialog && dialog.style.display === 'flex' && !dialogContent.contains(event.target)) {
    closeThemeDialog();
  }
});

// Инициализация при загрузке страницы
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTheme);
} else {
  initTheme();
}

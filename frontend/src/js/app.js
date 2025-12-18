// ============================================
// ГЛАВНЫЙ ФАЙЛ ПРИЛОЖЕНИЯ (app.js)
// ============================================
// Инициализация и связующая логика
// Модули: utils.js -> data.js -> ui.js -> app.js

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
  // Загрузка данных
  loadData();
  initSettings(); // Инициализация настроек для старых данных
  initDefaultTasks(); // Инициализация задач по умолчанию (до checkDailyReset)
  checkDailyReset(); // Проверка ежедневного сброса (после initDefaultTasks)
  
  // Первоначальный рендеринг
  renderChecklist();
  renderKanban();
  renderPiggy();
  renderMoney();
  renderRules();
  updateStars();
  updateProfileAvatar();
  
  // Применяем сохранённые цвета пола
  const gender = appData.profile?.gender || 'none';
  applyGenderColors(gender);
  
  // Обновляем имя в шапке при загрузке
  const headerNameEl = document.getElementById('header-name');
  if (headerNameEl) {
    const name = appData.profile?.name || 'Ребёнок';
    headerNameEl.textContent = name;
  }
  
  checkWeeklyReset();
  
  // Обработчики событий для модальных окон (закрытие по клику вне)
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  });
  
  // Enter для добавления задач
  document.getElementById('new-task-text')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      addTask();
    }
  });
  
  document.getElementById('goal-name-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      setGoal();
    }
  });
  
  document.getElementById('new-rule-text')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      addRule();
    }
  });
  
  document.getElementById('piggy-amount-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      savePiggyAmount();
    }
  });
});

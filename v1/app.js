// Данные приложения
let appData = {
  checklist: [],
  kanban: {
    todo: [],
    doing: [],
    done: []
  },
  piggy: {
    amount: 0,
    goal: {
      name: '',
      amount: 0
    },
    history: []
  },
  stars: {
    today: 0,
    total: 0,
    history: [],
    streak: {
      current: 0,
      lastDate: null,
      history: []
    },
    claimedRewards: []
  },
  money: {
    total: 0,
    history: []
  },
  wallet: {
    amount: 0,
    history: []
  },
  rules: [
    '📱 Телефон до 21:00',
    '🛏 Сон важнее экрана',
    '🌸 Ошибаться можно',
    '❤️ Родители всегда рядом'
  ],
  settings: {
    starsToMoney: 15,
    moneyPerStars: 200
  },
  weeklyStats: {
    days: [],
    lastWeek: []
  },
  diary: [],
  wishlist: [],
  profile: {
    avatar: null,
    name: 'Ребёнок',
    gender: 'none' // 'girl', 'boy', 'none'
  },
  lastResetDate: null
};

// Функции для получения настроек (обратная совместимость)
function getStarsToMoney() {
  return appData.settings?.starsToMoney || 15;
}

function getMoneyPerStars() {
  return appData.settings?.moneyPerStars || 200;
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  loadData();
  initSettings(); // Инициализация настроек для старых данных
  checkDailyReset();
  initDefaultTasks();
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
});

// Работа с данными
function loadData() {
  const saved = localStorage.getItem('responsibilityAppData');
  if (saved) {
    // Безопасный парсинг JSON согласно rules.md
    const parsed = safeJsonParse(saved, null);
    if (!parsed) {
      console.error('Ошибка загрузки данных: неверный формат JSON');
      return;
    }
    
    try {
      // Объединяем с дефолтными значениями для обратной совместимости
      appData = {
        ...appData,
        ...parsed,
        stars: {
          ...appData.stars,
          ...(parsed.stars || {}),
          streak: parsed.stars?.streak || appData.stars.streak,
          claimedRewards: parsed.stars?.claimedRewards || []
        },
        settings: parsed.settings || appData.settings,
        weeklyStats: parsed.weeklyStats || appData.weeklyStats,
        wallet: parsed.wallet || appData.wallet,
        profile: {
          ...appData.profile,
          ...(parsed.profile || {}),
          gender: parsed.profile?.gender || 'none'
        }
      };
    } catch (e) {
      console.error('Ошибка загрузки данных:', e);
      // Восстанавливаем дефолтные данные при критической ошибке
      appData = { ...appData };
    }
  }
}

function initSettings() {
  // Инициализация настроек для старых данных
  if (!appData.settings) {
    appData.settings = {
      starsToMoney: 15,
      moneyPerStars: 200
    };
    saveData();
  }
}

function saveData() {
  try {
    // Валидация данных перед сохранением
    if (!appData || typeof appData !== 'object') {
      console.error('Ошибка сохранения: неверная структура данных');
      return false;
    }
    
    // Проверка размера данных перед сохранением
    const sizeCheck = checkStorageSize(appData);
    if (!sizeCheck.valid) {
      console.error('Ошибка сохранения:', sizeCheck.error);
      alert('Ошибка сохранения данных: ' + sizeCheck.error);
      return false;
    }
    
    // Безопасная сериализация
    const jsonString = JSON.stringify(appData);
    if (!jsonString || jsonString === 'null' || jsonString === 'undefined') {
      console.error('Ошибка сохранения: неверная сериализация данных');
      return false;
    }
    
    localStorage.setItem('responsibilityAppData', jsonString);
    return true;
  } catch (error) {
    console.error('Ошибка сохранения данных:', error);
    // Обработка ошибки переполнения localStorage
    if (error.name === 'QuotaExceededError' || error.code === 22) {
      alert('Недостаточно места в хранилище. Попробуйте удалить старые данные.');
    } else if (error.name === 'SecurityError' || error.code === 18) {
      alert('Ошибка доступа к хранилищу. Проверьте настройки браузера.');
    } else {
      alert('Ошибка сохранения данных. Попробуйте позже.');
    }
    return false;
  }
}

// Ежедневный сброс
function checkDailyReset() {
  const today = new Date().toDateString();
  if (appData.lastResetDate !== today) {
    // Проверяем streak перед сбросом
    checkStreak();
    resetDailyTasks();
    appData.lastResetDate = today;
    saveData();
  }
}

function resetDailyTasks() {
  // Сохраняем статистику дня перед сбросом
  saveDailyStats();
  
  // Сбрасываем чек-лист (но сохраняем задачи)
  appData.checklist.forEach(task => {
    task.completed = false;
  });
  appData.stars.today = 0;
  saveData();
  renderChecklist();
  updateStars();
}

// Сохранение статистики дня
function saveDailyStats() {
  const today = new Date();
  const completedTasks = appData.checklist.filter(t => t.completed).length;
  const starsEarned = appData.stars.today;
  
  const dayStat = {
    date: today.toISOString().split('T')[0],
    tasksCompleted: completedTasks,
    starsEarned: starsEarned
  };
  
  // Удаляем старую запись за этот день, если есть
  appData.weeklyStats.days = appData.weeklyStats.days.filter(
    d => d.date !== dayStat.date
  );
  appData.weeklyStats.days.push(dayStat);
  
  // Храним только последние 14 дней
  appData.weeklyStats.days.sort((a, b) => new Date(b.date) - new Date(a.date));
  appData.weeklyStats.days = appData.weeklyStats.days.slice(0, 14);
  
  saveData();
}

// Проверка и обновление streak
function checkStreak() {
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().split('T')[0];
  
  // Подсчитываем выполненные задачи за вчера
  const yesterdayStats = appData.weeklyStats.days.find(d => d.date === yesterdayStr);
  const completedTasks = yesterdayStats?.tasksCompleted || 0;
  
  // Инициализация streak
  if (!appData.stars.streak) {
    appData.stars.streak = {
      current: 0,
      lastDate: null,
      history: []
    };
  }
  
  const streak = appData.stars.streak;
  
  // Если выполнено 4+ задач вчера
  if (completedTasks >= 4) {
    // Проверяем, был ли вчерашний день уже засчитан
    if (streak.lastDate !== yesterdayStr) {
      streak.current += 1;
      streak.lastDate = todayStr;
      
      // Проверяем бонусы за серии
      checkStreakBonus();
      
      saveData();
    }
  } else {
    // Если не выполнено 4+ задач, сбрасываем streak
    if (streak.current > 0) {
      streak.history.push({
        days: streak.current,
        date: yesterdayStr
      });
    }
    streak.current = 0;
    streak.lastDate = null;
    saveData();
  }
}

// Бонусы за серии дней
function checkStreakBonus() {
  const streak = appData.stars.streak.current;
  let bonus = 0;
  let description = '';
  
  if (streak === 3) {
    bonus = 10;
    description = 'Бонус за 3 дня подряд! 🔥';
  } else if (streak === 7) {
    bonus = 50;
    description = 'Бонус за неделю подряд! 🔥🔥';
  } else if (streak === 14) {
    bonus = 150;
    description = 'Бонус за 2 недели подряд! 🔥🔥🔥';
  } else if (streak === 30) {
    bonus = 500;
    description = 'Бонус за месяц подряд! 🔥🔥🔥🔥';
  }
  
  if (bonus > 0) {
    addMoneyToPiggyDirect(bonus, description);
    addMoneyHistory('streak', bonus, description);
    appData.piggy.history.push({
      date: new Date().toISOString(),
      type: 'add',
      amount: bonus,
      description: description
    });
    saveData();
    renderPiggy();
    
    // Показываем уведомление
    showStreakNotification(streak, bonus);
  }
}

function showStreakNotification(days, bonus) {
  // Создаем временное уведомление
  const notification = document.createElement('div');
  notification.className = 'streak-notification';
  notification.innerHTML = `
    <div class="streak-notification-content">
      <h3>🔥 Серия ${days} дней! 🔥</h3>
      <p>Бонус: +${bonus} ₽</p>
    </div>
  `;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.classList.add('show');
  }, 100);
  
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Еженедельный сброс статистики
function checkWeeklyReset() {
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0 = воскресенье
  
  // Если понедельник (1) и есть данные за прошлую неделю
  if (dayOfWeek === 1) {
    const lastWeekData = appData.weeklyStats.days.filter(d => {
      const date = new Date(d.date);
      const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
      return daysAgo >= 7 && daysAgo < 14;
    });
    
    if (lastWeekData.length > 0 && appData.weeklyStats.lastWeek.length === 0) {
      appData.weeklyStats.lastWeek = [...lastWeekData];
      saveData();
    }
  }
}

// Инициализация задач по умолчанию
function initDefaultTasks() {
  if (appData.checklist.length === 0) {
    appData.checklist = [
      { id: Date.now(), text: 'Встала и проснулась', completed: false, stars: 1 },
      { id: Date.now() + 1, text: 'Заправила кровать', completed: false, stars: 1 },
      { id: Date.now() + 2, text: 'Собралась в школу', completed: false, stars: 1 },
      { id: Date.now() + 3, text: 'Сделала учи.ру', completed: false, stars: 2 },
      { id: Date.now() + 4, text: 'Убрала комнату (5 мин)', completed: false, stars: 1 }
    ];
    saveData();
  }
  
  if (appData.kanban.todo.length === 0 && appData.kanban.doing.length === 0 && appData.kanban.done.length === 0) {
    appData.kanban.todo = [
      { id: Date.now(), text: 'Учи.ру' }
    ];
    saveData();
  }
}

// Навигация
function openPage(id, btn) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.menu button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  // Обновить данные при открытии страницы
  if (id === 'checklist') {
    renderChecklist();
    updateStars();
  } else if (id === 'kanban') {
    renderKanban();
  } else if (id === 'piggy') {
    renderPiggy();
    renderMoney();
    renderWishlist();
  } else if (id === 'diary') {
    renderDiary();
  } else if (id === 'stats') {
    renderWeeklyStats();
  }
}

// Чек-лист
function renderChecklist() {
  const container = document.getElementById('checklist-items');
  container.innerHTML = '';
  
  if (appData.checklist.length === 0) {
    container.innerHTML = '<li class="empty-state">Нет задач</li>';
    return;
  }
  
  appData.checklist.forEach((task, index) => {
    const li = document.createElement('li');
    li.className = task.completed ? 'completed' : '';
    
    // Безопасное создание элементов вместо innerHTML (защита от XSS)
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = task.completed || false;
    checkbox.addEventListener('change', () => toggleChecklistTask(task.id));
    
    const taskText = createTextElement('span', task.text || '', 'task-text');
    
    li.appendChild(checkbox);
    li.appendChild(taskText);
    
    if (task.stars) {
      const starsSpan = createTextElement('span', `⭐${task.stars}`, 'task-stars');
      li.appendChild(starsSpan);
    }
    
    container.appendChild(li);
  });
}

function toggleChecklistTask(id) {
  try {
    if (!id || (typeof id !== 'number' && typeof id !== 'string')) {
      console.error('Ошибка: неверный ID задачи');
      return;
    }
    
    if (!appData.checklist || !Array.isArray(appData.checklist)) {
      console.error('Ошибка: структура данных checklist неверна');
      return;
    }
    
    const task = appData.checklist.find(t => t && t.id === id);
    if (!task) {
      console.error('Ошибка: задача не найдена');
      return;
    }
    
    task.completed = !task.completed;
    
    // Инициализация stars если отсутствует
    if (!appData.stars) {
      appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
    }
    
    // Добавить/убрать звёзды
    if (task.completed && task.stars) {
      const stars = parseInt(task.stars) || 0;
      if (stars > 0) {
        appData.stars.today = (appData.stars.today || 0) + stars;
        appData.stars.total = (appData.stars.total || 0) + stars;
        addStarHistory(`Выполнено: ${task.text || ''}`, stars);
      }
    } else if (!task.completed && task.stars) {
      const stars = parseInt(task.stars) || 0;
      if (stars > 0) {
        appData.stars.today = Math.max(0, (appData.stars.today || 0) - stars);
        appData.stars.total = Math.max(0, (appData.stars.total || 0) - stars);
      }
    }
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      task.completed = !task.completed;
      return;
    }
    
    renderChecklist();
    updateStars();
    checkMoneyReward();
    checkMiniRewards();
  } catch (error) {
    console.error('Ошибка при переключении задачи:', error);
    alert('Ошибка при обновлении задачи. Попробуйте позже.');
  }
}

function deleteChecklistTask(id) {
  if (confirm('Удалить задачу?')) {
    appData.checklist = appData.checklist.filter(t => t.id !== id);
    saveData();
    renderChecklist();
  }
}

function openAddTaskModal(type) {
  document.getElementById('add-task-modal').classList.add('active');
  document.getElementById('add-task-modal').dataset.type = type;
  document.getElementById('new-task-text').value = '';
  document.getElementById('new-task-text').focus();
}

function closeAddTaskModal() {
  document.getElementById('add-task-modal').classList.remove('active');
}

function addTask() {
  try {
    const textInput = document.getElementById('new-task-text');
    const modal = document.getElementById('add-task-modal');
    
    if (!textInput || !modal) {
      console.error('Ошибка: элементы формы не найдены');
      return;
    }
    
    const type = modal.dataset.type;
    if (!type || (type !== 'checklist' && type !== 'kanban')) {
      console.error('Ошибка: неверный тип задачи');
      return;
    }
    
    // Валидация текста задачи согласно rules.md
    const validation = validateTaskText(textInput.value);
    if (!validation.valid) {
      alert(validation.error);
      textInput.focus();
      return;
    }
    
    if (type === 'checklist') {
      if (!appData.checklist || !Array.isArray(appData.checklist)) {
        appData.checklist = [];
      }
      
      const task = {
        id: Date.now(),
        text: validation.value,
        completed: false,
        stars: 1
      };
      appData.checklist.push(task);
      
      if (!saveData()) {
        // Откатываем добавление при ошибке сохранения
        appData.checklist.pop();
        return;
      }
      
      renderChecklist();
    } else if (type === 'kanban') {
      if (!appData.kanban || !appData.kanban.todo || !Array.isArray(appData.kanban.todo)) {
        if (!appData.kanban) appData.kanban = { todo: [], doing: [], done: [] };
        if (!appData.kanban.todo) appData.kanban.todo = [];
      }
      
      const task = {
        id: Date.now(),
        text: validation.value
      };
      appData.kanban.todo.push(task);
      
      if (!saveData()) {
        // Откатываем добавление при ошибке сохранения
        appData.kanban.todo.pop();
        return;
      }
      
      renderKanban();
    }
    
    closeAddTaskModal();
    textInput.value = '';
  } catch (error) {
    console.error('Ошибка при добавлении задачи:', error);
    alert('Ошибка при добавлении задачи. Попробуйте позже.');
  }
}

// Канбан
function renderKanban() {
  renderKanbanColumn('todo', appData.kanban.todo);
  renderKanbanColumn('doing', appData.kanban.doing);
  renderKanbanColumn('done', appData.kanban.done);
}

function renderKanbanColumn(column, tasks) {
  const container = document.getElementById(`${column}-tasks`);
  container.innerHTML = '';
  
  tasks.forEach(task => {
    const taskEl = document.createElement('div');
    taskEl.className = 'task';
    taskEl.draggable = true;
    taskEl.dataset.id = task.id;
    taskEl.innerHTML = `
      <span class="task-text">${task.text}</span>
      <div class="task-actions">
        ${column !== 'todo' ? `<button class="task-move" onclick="moveTask(${task.id}, '${column}', 'prev')" title="Назад">←</button>` : ''}
        ${column !== 'done' ? `<button class="task-move" onclick="moveTask(${task.id}, '${column}', 'next')" title="Вперёд">→</button>` : ''}
      </div>
    `;
    
    // Drag and drop
    taskEl.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', task.id);
      e.dataTransfer.setData('column', column);
      taskEl.classList.add('dragging');
    });
    
    taskEl.addEventListener('dragend', () => {
      taskEl.classList.remove('dragging');
    });
    
    container.appendChild(taskEl);
  });
  
  // Drop zone
  container.addEventListener('dragover', (e) => {
    e.preventDefault();
  });
  
  container.addEventListener('drop', (e) => {
    e.preventDefault();
    const taskId = parseInt(e.dataTransfer.getData('text/plain'));
    const fromColumn = e.dataTransfer.getData('column');
    moveTaskToColumn(taskId, fromColumn, column);
  });
}

function moveTask(id, currentColumn, direction) {
  const columnOrder = ['todo', 'doing', 'done'];
  const currentIndex = columnOrder.indexOf(currentColumn);
  let newIndex;
  
  if (direction === 'next') {
    newIndex = Math.min(currentIndex + 1, columnOrder.length - 1);
  } else {
    newIndex = Math.max(currentIndex - 1, 0);
  }
  
  const newColumn = columnOrder[newIndex];
  moveTaskToColumn(id, currentColumn, newColumn);
}

function moveTaskToColumn(taskId, fromColumn, toColumn) {
  try {
    if (!taskId || !fromColumn || !toColumn) {
      console.error('Ошибка: неверные параметры для перемещения задачи');
      return;
    }
    
    if (fromColumn === toColumn) return;
    
    if (!appData.kanban || !appData.kanban[fromColumn] || !appData.kanban[toColumn]) {
      console.error('Ошибка: структура данных kanban неверна');
      if (!appData.kanban) appData.kanban = { todo: [], doing: [], done: [] };
      if (!appData.kanban[fromColumn]) appData.kanban[fromColumn] = [];
      if (!appData.kanban[toColumn]) appData.kanban[toColumn] = [];
    }
    
    const task = appData.kanban[fromColumn].find(t => t && t.id === taskId);
    if (!task) {
      console.error('Ошибка: задача не найдена');
      return;
    }
    
    // Сохраняем исходное состояние для отката
    const originalFromColumn = [...appData.kanban[fromColumn]];
    const originalToColumn = [...appData.kanban[toColumn]];
    
    appData.kanban[fromColumn] = appData.kanban[fromColumn].filter(t => t && t.id !== taskId);
    appData.kanban[toColumn].push(task);
    
    // Если задача перешла в "Готово", добавить звёзды
    if (toColumn === 'done' && fromColumn !== 'done') {
      if (!appData.stars) {
        appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
      }
      
      appData.stars.today = (appData.stars.today || 0) + 2;
      appData.stars.total = (appData.stars.total || 0) + 2;
      addStarHistory(`Завершено: ${task.text || ''}`, 2);
      updateStars();
      checkMoneyReward();
      checkMiniRewards();
    }
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      appData.kanban[fromColumn] = originalFromColumn;
      appData.kanban[toColumn] = originalToColumn;
      return;
    }
    
    renderKanban();
  } catch (error) {
    console.error('Ошибка при перемещении задачи:', error);
    alert('Ошибка при перемещении задачи. Попробуйте позже.');
  }
}

function deleteKanbanTask(id, column) {
  if (confirm('Удалить задачу?')) {
    appData.kanban[column] = appData.kanban[column].filter(t => t.id !== id);
    saveData();
    renderKanban();
  }
}

// Копилка
function renderPiggy() {
  const amount = appData.piggy.amount;
  const goal = appData.piggy.goal.amount;
  
  document.getElementById('piggy-amount').textContent = `${amount} ₽`;
  document.getElementById('piggy-goal').textContent = goal > 0 ? `/ ${goal} ₽` : '';
  
  const progress = goal > 0 ? Math.min((amount / goal) * 100, 100) : 0;
  document.getElementById('piggy-progress').style.width = `${progress}%`;
  
  const goalText = goal > 0 
    ? `${appData.piggy.goal.name || 'Цель'} - ${goal} ₽`
    : 'Цель не установлена';
  document.getElementById('goal-text').textContent = goalText;
  
  renderPiggyHistory();
}

// Открытие модального окна для изменения суммы
function openPiggyModal(type) {
  const modal = document.getElementById('piggy-modal');
  const title = document.getElementById('piggy-modal-title');
  const input = document.getElementById('piggy-amount-input');
  
  if (type === 'plus') {
    title.textContent = '➕ Добавить в копилку';
    input.placeholder = 'Введите сумму для добавления (₽)';
  } else {
    title.textContent = '➖ Убрать из копилки';
    input.placeholder = 'Введите сумму для удаления (₽)';
  }
  
  input.value = '';
  input.dataset.type = type;
  modal.classList.add('active');
  setTimeout(() => input.focus(), 100);
}

function closePiggyModal() {
  document.getElementById('piggy-modal').classList.remove('active');
  document.getElementById('piggy-amount-input').value = '';
}

function savePiggyAmount() {
  try {
    const input = document.getElementById('piggy-amount-input');
    if (!input) {
      console.error('Ошибка: поле ввода не найдено');
      return;
    }
    
    const type = input.dataset.type;
    if (!type || (type !== 'plus' && type !== 'minus')) {
      console.error('Ошибка: неверный тип операции');
      return;
    }
    
    // Валидация суммы согласно rules.md
    const validation = validateNumber(input.value, { min: 1, max: 1000000 });
    if (!validation.valid) {
      alert(validation.error);
      input.focus();
      return;
    }
    
    const amount = validation.value;
    
    // Инициализация piggy если отсутствует
    if (!appData.piggy) {
      appData.piggy = { amount: 0, goal: { name: '', amount: 0 }, history: [] };
    }
    if (!appData.piggy.history || !Array.isArray(appData.piggy.history)) {
      appData.piggy.history = [];
    }
    
    // Сохраняем исходное состояние для отката
    const originalAmount = appData.piggy.amount;
    const originalHistoryLength = appData.piggy.history.length;
    
    if (type === 'minus') {
      const newAmount = Math.max(0, (appData.piggy.amount || 0) - amount);
      const actualDelta = (appData.piggy.amount || 0) - newAmount;
      
      if (actualDelta > 0) {
        appData.piggy.amount = newAmount;
        appData.piggy.history.push({
          date: new Date().toISOString(),
          type: 'withdraw',
          amount: actualDelta,
          description: `Убрано ${actualDelta} ₽`
        });
      } else {
        alert('Недостаточно средств в копилке');
        return;
      }
    } else {
      appData.piggy.amount = (appData.piggy.amount || 0) + amount;
      appData.piggy.history.push({
        date: new Date().toISOString(),
        type: 'add',
        amount: amount,
        description: `Добавлено ${amount} ₽`
      });
    }
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      appData.piggy.amount = originalAmount;
      appData.piggy.history = appData.piggy.history.slice(0, originalHistoryLength);
      return;
    }
    
    renderPiggy();
    closePiggyModal();
    
    // Анимация изменения суммы
    const amountEl = document.getElementById('piggy-amount');
    if (amountEl) {
      amountEl.style.transform = 'scale(1.1)';
      amountEl.style.color = type === 'plus' ? '#10b981' : '#ef4444';
      setTimeout(() => {
        amountEl.style.transform = 'scale(1)';
        amountEl.style.color = '#ff8ccf';
      }, 300);
    }
  } catch (error) {
    console.error('Ошибка при сохранении суммы в копилке:', error);
    alert('Ошибка при сохранении суммы. Попробуйте позже.');
  }
}

function renderPiggyHistory() {
  try {
    const container = document.getElementById('piggy-history');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!appData.piggy || !appData.piggy.history || !Array.isArray(appData.piggy.history) || appData.piggy.history.length === 0) {
      container.innerHTML = '<p class="empty-state">Нет истории</p>';
      return;
    }
    
    appData.piggy.history.slice(-10).reverse().forEach(item => {
      if (!item) return;
      
      const div = document.createElement('div');
      div.className = 'history-item';
      
      // Безопасное создание элементов
      const leftDiv = document.createElement('div');
      const amountDiv = createTextElement('div', `${item.type === 'add' ? '➕' : '➖'} ${item.amount || 0} ₽`, '');
      const dateDiv = createTextElement('div', formatDate(item.date || new Date().toISOString()), 'history-date');
      leftDiv.appendChild(amountDiv);
      leftDiv.appendChild(dateDiv);
      
      const descDiv = createTextElement('div', item.description || '', '');
      
      div.appendChild(leftDiv);
      div.appendChild(descDiv);
      container.appendChild(div);
    });
  } catch (error) {
    console.error('Ошибка при отображении истории копилки:', error);
  }
}

function openGoalModal() {
  document.getElementById('goal-modal').classList.add('active');
  document.getElementById('goal-name-input').value = appData.piggy.goal.name || '';
  document.getElementById('goal-amount-input').value = appData.piggy.goal.amount || '';
}

function closeGoalModal() {
  document.getElementById('goal-modal').classList.remove('active');
}

function setGoal() {
  try {
    const nameInput = document.getElementById('goal-name-input');
    const amountInput = document.getElementById('goal-amount-input');
    
    if (!nameInput || !amountInput) {
      console.error('Ошибка: поля формы не найдены');
      return;
    }
    
    const name = nameInput.value.trim();
    const amountValidation = validateNumber(amountInput.value, { min: 1, max: 10000000 });
    
    if (!amountValidation.valid) {
      alert(amountValidation.error || 'Введите сумму больше 0');
      amountInput.focus();
      return;
    }
    
    const amount = amountValidation.value;
    
    // Инициализация piggy если отсутствует
    if (!appData.piggy) {
      appData.piggy = { amount: 0, goal: { name: '', amount: 0 }, history: [] };
    }
    if (!appData.piggy.goal) {
      appData.piggy.goal = { name: '', amount: 0 };
    }
    
    // Сохраняем исходное состояние для отката
    const originalGoal = { ...appData.piggy.goal };
    
    appData.piggy.goal = {
      name: name || 'Цель',
      amount: amount
    };
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      appData.piggy.goal = originalGoal;
      return;
    }
    
    renderPiggy();
    closeGoalModal();
  } catch (error) {
    console.error('Ошибка при установке цели:', error);
    alert('Ошибка при установке цели. Попробуйте позже.');
  }
}

// Звёзды и деньги
function updateStars() {
  try {
    // Инициализация stars если отсутствует
    if (!appData.stars) {
      appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
    }
    
    const todayStars = appData.stars.today || 0;
    const totalStars = appData.stars.total || 0;
    
    const todayStarsEl = document.getElementById('today-stars');
    if (todayStarsEl) {
      todayStarsEl.textContent = todayStars;
      // Анимация при изменении
      todayStarsEl.classList.add('animate');
      setTimeout(() => todayStarsEl.classList.remove('animate'), 500);
    }
    
    const totalStarsEl = document.getElementById('total-stars');
    if (totalStarsEl) {
      totalStarsEl.textContent = totalStars;
    }
    
    // Обновление звёзд в заголовке
    const headerStarsEl = document.getElementById('header-stars-count');
    if (headerStarsEl) {
      headerStarsEl.textContent = totalStars;
    }
    
    const starsToMoney = getStarsToMoney();
    if (starsToMoney > 0) {
      const progress = (totalStars % starsToMoney) / starsToMoney * 100;
      const progressEl = document.getElementById('stars-progress');
      if (progressEl) {
        progressEl.style.width = `${progress}%`;
      }
      
      const nextReward = starsToMoney - (totalStars % starsToMoney);
      const moneyPerStars = getMoneyPerStars();
      const nextRewardEl = document.getElementById('next-reward');
      if (nextRewardEl) {
        nextRewardEl.textContent = `Следующая выплата через: ${nextReward} ⭐ (${moneyPerStars} ₽)`;
      }
    }
    
    // Обновляем отображение курса
    const starsInfo = document.querySelector('.stars-info p');
    if (starsInfo) {
      const moneyPerStars = getMoneyPerStars();
      starsInfo.textContent = `${starsToMoney} ⭐ = ${moneyPerStars} ₽`;
    }
    
    // Обновляем streak
    renderStreak();
  } catch (error) {
    console.error('Ошибка при обновлении звёзд:', error);
    // Не показываем alert, чтобы не мешать пользователю
  }
}

// Отображение streak
function renderStreak() {
  const streakContainer = document.getElementById('streak-display');
  if (!streakContainer) return;
  
  const streak = appData.stars.streak?.current || 0;
  if (streak > 0) {
    streakContainer.innerHTML = `
      <div class="streak-info">
        <span class="streak-emoji">🔥</span>
        <span class="streak-text">Серия: ${streak} дней</span>
      </div>
    `;
    streakContainer.style.display = 'block';
  } else {
    streakContainer.style.display = 'none';
  }
}

function checkMoneyReward() {
  try {
    // Инициализация данных если отсутствуют
    if (!appData.stars) {
      appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
    }
    if (!appData.money) {
      appData.money = { total: 0, history: [] };
    }
    if (!appData.money.history || !Array.isArray(appData.money.history)) {
      appData.money.history = [];
    }
    
    const starsToMoney = getStarsToMoney();
    const moneyPerStars = getMoneyPerStars();
    
    if (starsToMoney <= 0 || moneyPerStars <= 0) {
      console.error('Ошибка: неверные настройки курса обмена');
      return;
    }
    
    const totalStars = appData.stars.total || 0;
    const fullRewards = Math.floor(totalStars / starsToMoney);
    const alreadyPaid = appData.money.history.filter(h => h && h.type === 'stars').length;
    
    if (fullRewards > alreadyPaid) {
      const toPay = (fullRewards - alreadyPaid) * moneyPerStars;
      
      if (toPay > 0) {
        // Добавляем деньги в кошелек, а не в копилку
        addMoneyToWallet(toPay, `Награда за ${starsToMoney} звёзд`);
        addMoneyHistory('stars', toPay, `Награда за ${starsToMoney} звёзд`);
        appData.money.total = (appData.money.total || 0) + toPay;
        
        if (!saveData()) {
          // Откатываем при ошибке сохранения
          appData.money.total = (appData.money.total || 0) - toPay;
          if (appData.wallet && appData.wallet.history) {
            appData.wallet.history.pop();
            appData.wallet.amount = (appData.wallet.amount || 0) - toPay;
          }
          return;
        }
        
        renderMoney();
      }
    }
  } catch (error) {
    console.error('Ошибка при проверке денежной награды:', error);
    // Не показываем alert, чтобы не мешать пользователю
  }
}

// Мини-награды
function checkMiniRewards() {
  if (!appData.stars.claimedRewards) {
    appData.stars.claimedRewards = [];
  }
  
  const rewards = [
    { stars: 5, title: '🎬 Выбор мультика!', message: 'Ты можешь выбрать мультик для просмотра!' },
    { stars: 10, title: '🎁 Маленький сюрприз', message: 'Отличная работа! Заслужил маленький сюрприз!' },
    { stars: 25, title: '🌟 Отличная работа!', message: 'Ты просто супер! Продолжай в том же духе!' }
  ];
  
  rewards.forEach(reward => {
    if (appData.stars.total >= reward.stars && 
        !appData.stars.claimedRewards.includes(reward.stars)) {
      showRewardModal(reward);
      appData.stars.claimedRewards.push(reward.stars);
      saveData();
    }
  });
}

function showRewardModal(reward) {
  const modal = document.getElementById('reward-modal');
  if (!modal) return;
  
  document.getElementById('reward-title').textContent = reward.title;
  document.getElementById('reward-message').textContent = reward.message;
  modal.classList.add('active');
}

function closeRewardModal() {
  document.getElementById('reward-modal').classList.remove('active');
}

function addStarHistory(description, amount) {
  try {
    // Инициализация stars если отсутствует
    if (!appData.stars) {
      appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
    }
    if (!appData.stars.history || !Array.isArray(appData.stars.history)) {
      appData.stars.history = [];
    }
    
    const amountNum = parseInt(amount) || 0;
    if (amountNum <= 0) {
      console.error('Ошибка: неверное количество звёзд для истории');
      return;
    }
    
    appData.stars.history.push({
      date: new Date().toISOString(),
      description: description || 'Начисление звёзд',
      amount: amountNum
    });
    
    // Ограничиваем размер истории (последние 100 записей)
    if (appData.stars.history.length > 100) {
      appData.stars.history = appData.stars.history.slice(-100);
    }
    
    saveData();
  } catch (error) {
    console.error('Ошибка при добавлении истории звёзд:', error);
  }
}

function renderMoney() {
  const totalStarsEl = document.getElementById('total-stars');
  const totalMoneyEl = document.getElementById('total-money');
  const walletAmountEl = document.getElementById('wallet-amount');
  const moneyProgressEl = document.getElementById('money-progress');
  const nextRewardEl = document.getElementById('next-reward');
  const conversionTextEl = document.getElementById('conversion-text');
  
  // Инициализация wallet если отсутствует
  if (!appData.wallet) {
    appData.wallet = { amount: 0, history: [] };
  }
  
  if (totalStarsEl) totalStarsEl.textContent = appData.stars?.total || 0;
  if (totalMoneyEl) totalMoneyEl.textContent = `${appData.money?.total || 0} ₽`;
  if (walletAmountEl) walletAmountEl.textContent = `${appData.wallet?.amount || 0} ₽`;
  
  const starsToMoney = getStarsToMoney();
  const progress = (appData.stars.total % starsToMoney) / starsToMoney * 100;
  if (moneyProgressEl) moneyProgressEl.style.width = `${progress}%`;
  
  const nextReward = starsToMoney - (appData.stars.total % starsToMoney);
  const moneyPerStars = getMoneyPerStars();
  if (nextRewardEl) {
    nextRewardEl.textContent = `Следующая выплата через: ${nextReward} ⭐ (${moneyPerStars} ₽)`;
  }
  if (conversionTextEl) {
    conversionTextEl.textContent = `${starsToMoney} ⭐ = ${moneyPerStars} ₽`;
  }
  
  renderMoneyHistory();
}

function renderMoneyHistory() {
  const container = document.getElementById('money-history');
  container.innerHTML = '';
  
  if (appData.money.history.length === 0) {
    container.innerHTML = '<p class="empty-state">Нет выплат</p>';
    return;
  }
  
  appData.money.history.slice(-10).reverse().forEach(item => {
    const div = document.createElement('div');
    div.className = 'history-item';
    div.innerHTML = `
      <div>
        <div>💰 ${item.amount} ₽</div>
        <div class="history-date">${formatDate(item.date)}</div>
      </div>
      <div>${item.description || ''}</div>
    `;
    container.appendChild(div);
  });
}

function addMoneyHistory(type, amount, description) {
  try {
    // Инициализация money если отсутствует
    if (!appData.money) {
      appData.money = { total: 0, history: [] };
    }
    if (!appData.money.history || !Array.isArray(appData.money.history)) {
      appData.money.history = [];
    }
    
    const amountNum = parseInt(amount) || 0;
    if (amountNum <= 0) {
      console.error('Ошибка: неверная сумма для истории');
      return;
    }
    
    if (!type || typeof type !== 'string') {
      console.error('Ошибка: неверный тип операции');
      return;
    }
    
    appData.money.history.push({
      date: new Date().toISOString(),
      type: type,
      amount: amountNum,
      description: description || 'Операция'
    });
    
    // Ограничиваем размер истории (последние 100 записей)
    if (appData.money.history.length > 100) {
      appData.money.history = appData.money.history.slice(-100);
    }
    
    saveData();
  } catch (error) {
    console.error('Ошибка при добавлении истории денег:', error);
  }
}

// Правила
function renderRules() {
  const container = document.getElementById('rules-list');
  container.innerHTML = '';
  
  appData.rules.forEach((rule, index) => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span>${rule}</span>
    `;
    container.appendChild(li);
  });
}

function openRuleModal() {
  document.getElementById('rule-modal').classList.add('active');
  document.getElementById('new-rule-text').value = '';
  document.getElementById('new-rule-text').focus();
}

function closeRuleModal() {
  document.getElementById('rule-modal').classList.remove('active');
}

function addRule() {
  const text = document.getElementById('new-rule-text').value.trim();
  if (!text) return;
  
  appData.rules.push(text);
  saveData();
  renderRules();
  closeRuleModal();
}

function deleteRule(index) {
  if (confirm('Удалить правило?')) {
    appData.rules.splice(index, 1);
    saveData();
    renderRules();
  }
}

// Переключение мобильного вида
function toggleMobileView() {
  const container = document.querySelector('.container');
  if (container.style.maxWidth === '420px') {
    container.style.maxWidth = '100%';
    container.style.width = '100%';
    document.body.style.paddingBottom = '0';
  } else {
    container.style.maxWidth = '420px';
    container.style.width = '420px';
    document.body.style.paddingBottom = '80px';
  }
}

// Админка
function toggleAdmin() {
  const panel = document.getElementById('admin-panel');
  const isActive = panel.classList.toggle('active');
  if (isActive) {
    loadSettingsToAdmin();
  }
}

function addTaskFromAdmin() {
  const text = document.getElementById('admin-task-input').value.trim();
  const type = document.getElementById('admin-task-type').value;
  
  if (!text) {
    alert('Введите текст задачи');
    return;
  }
  
  if (type === 'checklist') {
    const task = {
      id: Date.now(),
      text: text,
      completed: false,
      stars: 1
    };
    appData.checklist.push(task);
  } else {
    const task = {
      id: Date.now(),
      text: text
    };
    appData.kanban.todo.push(task);
  }
  
  saveData();
  renderChecklist();
  renderKanban();
  document.getElementById('admin-task-input').value = '';
}

function setGoalFromAdmin() {
  const name = document.getElementById('admin-goal-name').value.trim();
  const amount = parseInt(document.getElementById('admin-goal-amount').value) || 0;
  
  if (amount <= 0) {
    alert('Введите сумму больше 0');
    return;
  }
  
  appData.piggy.goal = {
    name: name || 'Цель',
    amount: amount
  };
  
  saveData();
  renderPiggy();
  document.getElementById('admin-goal-name').value = '';
  document.getElementById('admin-goal-amount').value = '';
}

// Настройка курса в админке
function saveSettings() {
  const starsToMoney = parseInt(document.getElementById('admin-stars-to-money').value) || 15;
  const moneyPerStars = parseInt(document.getElementById('admin-money-per-stars').value) || 200;
  
  if (starsToMoney <= 0 || moneyPerStars <= 0) {
    alert('Введите значения больше 0');
    return;
  }
  
  appData.settings.starsToMoney = starsToMoney;
  appData.settings.moneyPerStars = moneyPerStars;
  
  saveData();
  updateStars();
  renderMoney();
  alert('Настройки сохранены!');
}

function loadSettingsToAdmin() {
  document.getElementById('admin-stars-to-money').value = appData.settings.starsToMoney || 15;
  document.getElementById('admin-money-per-stars').value = appData.settings.moneyPerStars || 200;
}

// Статистика недели
function renderWeeklyStats() {
  const container = document.getElementById('weekly-stats-content');
  if (!container) return;
  
  const last7Days = appData.weeklyStats.days.slice(0, 7).reverse();
  const lastWeek = appData.weeklyStats.lastWeek || [];
  
  let html = '<div class="stats-summary">';
  
  // Текущая неделя
  const currentWeekTotal = last7Days.reduce((sum, d) => sum + (d.starsEarned || 0), 0);
  const currentWeekTasks = last7Days.reduce((sum, d) => sum + (d.tasksCompleted || 0), 0);
  
  html += `
    <div class="stat-card">
      <h3>Эта неделя</h3>
      <div class="stat-value">${currentWeekTotal} ⭐</div>
      <div class="stat-label">${currentWeekTasks} задач</div>
    </div>
  `;
  
  // Прошлая неделя
  if (lastWeek.length > 0) {
    const lastWeekTotal = lastWeek.reduce((sum, d) => sum + (d.starsEarned || 0), 0);
    const lastWeekTasks = lastWeek.reduce((sum, d) => sum + (d.tasksCompleted || 0), 0);
    const diff = currentWeekTotal - lastWeekTotal;
    
    html += `
      <div class="stat-card">
        <h3>Прошлая неделя</h3>
        <div class="stat-value">${lastWeekTotal} ⭐</div>
        <div class="stat-label">${lastWeekTasks} задач</div>
        ${diff !== 0 ? `<div class="stat-diff ${diff > 0 ? 'positive' : 'negative'}">${diff > 0 ? '+' : ''}${diff} ⭐</div>` : ''}
      </div>
    `;
  }
  
  html += '</div>';
  
  // График по дням
  html += '<div class="stats-chart"><h3>Звёзды по дням</h3><div class="chart-bars">';
  
  last7Days.forEach(day => {
    const date = new Date(day.date);
    const dayName = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][date.getDay()];
    const maxStars = Math.max(...last7Days.map(d => d.starsEarned || 0), 1);
    const height = ((day.starsEarned || 0) / maxStars) * 100;
    
    html += `
      <div class="chart-bar-item">
        <div class="chart-bar" style="height: ${height}%"></div>
        <div class="chart-label">${dayName}</div>
        <div class="chart-value">${day.starsEarned || 0}⭐</div>
      </div>
    `;
  });
  
  html += '</div></div>';
  
  container.innerHTML = html;
}

function addMoneyToPiggy() {
  const amount = parseInt(document.getElementById('admin-add-money').value) || 0;
  if (amount <= 0) {
    alert('Введите сумму больше 0');
    return;
  }
  
  addMoneyToPiggyDirect(amount, 'Пополнение');
  document.getElementById('admin-add-money').value = '';
}

function addMoneyToPiggyDirect(amount, description) {
  try {
    // Валидация параметров
    const amountNum = parseInt(amount) || 0;
    if (amountNum <= 0) {
      console.error('Ошибка: неверная сумма для добавления');
      return false;
    }
    
    // Инициализация piggy если отсутствует
    if (!appData.piggy) {
      appData.piggy = { amount: 0, goal: { name: '', amount: 0 }, history: [] };
    }
    if (!appData.piggy.history || !Array.isArray(appData.piggy.history)) {
      appData.piggy.history = [];
    }
    
    // Сохраняем исходное состояние для отката
    const originalAmount = appData.piggy.amount || 0;
    const originalHistoryLength = appData.piggy.history.length;
    
    appData.piggy.amount = (appData.piggy.amount || 0) + amountNum;
    appData.piggy.history.push({
      date: new Date().toISOString(),
      type: 'add',
      amount: amountNum,
      description: description || 'Пополнение'
    });
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      appData.piggy.amount = originalAmount;
      appData.piggy.history = appData.piggy.history.slice(0, originalHistoryLength);
      return false;
    }
    
    renderPiggy();
    return true;
  } catch (error) {
    console.error('Ошибка при добавлении денег в копилку:', error);
    return false;
  }
}

// Добавление денег в кошелек (из конвертации звезд)
function addMoneyToWallet(amount, description) {
  try {
    // Валидация параметров
    const amountNum = parseInt(amount) || 0;
    if (amountNum <= 0) {
      console.error('Ошибка: неверная сумма для добавления в кошелек');
      return false;
    }
    
    // Инициализация wallet если отсутствует
    if (!appData.wallet) {
      appData.wallet = { amount: 0, history: [] };
    }
    if (!appData.wallet.history || !Array.isArray(appData.wallet.history)) {
      appData.wallet.history = [];
    }
    
    // Сохраняем исходное состояние для отката
    const originalAmount = appData.wallet.amount || 0;
    const originalHistoryLength = appData.wallet.history.length;
    
    appData.wallet.amount = (appData.wallet.amount || 0) + amountNum;
    appData.wallet.history.push({
      date: new Date().toISOString(),
      type: 'add',
      amount: amountNum,
      description: description || 'Пополнение кошелька'
    });
    
    // Ограничиваем размер истории (последние 100 записей)
    if (appData.wallet.history.length > 100) {
      appData.wallet.history = appData.wallet.history.slice(-100);
    }
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      appData.wallet.amount = originalAmount;
      appData.wallet.history = appData.wallet.history.slice(0, originalHistoryLength);
      return false;
    }
    
    renderMoney();
    return true;
  } catch (error) {
    console.error('Ошибка при добавлении денег в кошелек:', error);
    return false;
  }
}

function addStars() {
  const amount = parseInt(document.getElementById('admin-add-stars').value) || 0;
  if (amount <= 0) {
    alert('Введите количество больше 0');
    return;
  }
  
  appData.stars.today += amount;
  appData.stars.total += amount;
  addStarHistory('Добавлено администратором', amount);
  saveData();
  updateStars();
  checkMoneyReward();
  document.getElementById('admin-add-stars').value = '';
}

function payOutMoney() {
  if (appData.piggy.amount <= 0) {
    alert('В копилке нет денег');
    return;
  }
  
  if (confirm(`Выплатить ${appData.piggy.amount} ₽ из копилки?`)) {
    const amount = appData.piggy.amount;
    appData.piggy.amount = 0;
    appData.piggy.history.push({
      date: new Date().toISOString(),
      type: 'withdraw',
      amount: amount,
      description: 'Выплата'
    });
    saveData();
    renderPiggy();
  }
}

function clearAllData() {
  if (confirm('Вы уверены? Все данные будут удалены!')) {
    localStorage.removeItem('responsibilityAppData');
    location.reload();
  }
}

// Экспорт/импорт
function exportData() {
  const dataStr = JSON.stringify(appData, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `responsibility-data-${new Date().toISOString().split('T')[0]}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function importData() {
  document.getElementById('import-file').click();
}

function handleFileImport(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Проверка типа файла
  if (!file.type.includes('json') && !file.name.endsWith('.json')) {
    alert('Выберите JSON файл');
    return;
  }
  
  // Проверка размера файла
  const maxSize = 5 * 1024 * 1024; // 5MB
  if (file.size > maxSize) {
    alert('Файл слишком большой (максимум 5MB)');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    // Безопасный парсинг JSON
    const imported = safeJsonParse(e.target.result, null);
    if (!imported) {
      alert('Ошибка при импорте данных: неверный формат JSON');
      return;
    }
    
    try {
      // Валидация структуры данных
      if (typeof imported !== 'object' || Array.isArray(imported)) {
        throw new Error('Неверная структура данных');
      }
      
      // Проверка размера перед импортом
      const sizeCheck = checkStorageSize(imported);
      if (!sizeCheck.valid) {
        alert('Ошибка импорта: ' + sizeCheck.error);
        return;
      }
      
      appData = imported;
      if (!saveData()) {
        return;
      }
      alert('Данные успешно импортированы!');
      location.reload();
    } catch (error) {
      console.error('Ошибка импорта:', error);
      alert('Ошибка при импорте данных: ' + error.message);
    }
  };
  
  reader.onerror = () => {
    alert('Ошибка чтения файла');
  };
  
  reader.readAsText(file);
  event.target.value = '';
}

// Утилиты
function formatDate(isoString) {
  const date = new Date(isoString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day}.${month}.${year} ${hours}:${minutes}`;
}

// Закрытие модальных окон по клику вне их
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

// Дневник
function renderDiary() {
  const container = document.getElementById('diary-entries');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!appData.diary || appData.diary.length === 0) {
    container.innerHTML = '<p class="empty-state">Пока нет записей. Нажми + чтобы начать!</p>';
    return;
  }
  
  const sortedEntries = [...appData.diary].sort((a, b) => 
    new Date(b.date) - new Date(a.date)
  );
  
  sortedEntries.forEach(entry => {
    const entryEl = document.createElement('div');
    entryEl.className = 'diary-entry';
    
    // Безопасное создание элементов
    const header = document.createElement('div');
    header.className = 'diary-entry-header';
    const dateEl = createTextElement('div', formatDiaryDate(entry.date), 'diary-entry-date');
    header.appendChild(dateEl);
    
    entryEl.appendChild(header);
    
    if (entry.title) {
      const titleEl = createTextElement('div', entry.title, 'diary-entry-title');
      entryEl.appendChild(titleEl);
    }
    
    const contentEl = createTextElement('div', entry.content || '', 'diary-entry-content');
    entryEl.appendChild(contentEl);
    
    container.appendChild(entryEl);
  });
}

function openDiaryEntryModal() {
  document.getElementById('diary-modal').classList.add('active');
  document.getElementById('diary-title-input').value = '';
  document.getElementById('diary-content-input').value = '';
  setTimeout(() => document.getElementById('diary-content-input').focus(), 100);
}

function closeDiaryEntryModal() {
  document.getElementById('diary-modal').classList.remove('active');
  document.getElementById('diary-title-input').value = '';
  document.getElementById('diary-content-input').value = '';
}

function saveDiaryEntry() {
  const title = document.getElementById('diary-title-input').value.trim();
  const content = document.getElementById('diary-content-input').value.trim();
  
  if (!content) {
    alert('Напиши что-нибудь!');
    return;
  }
  
  if (!appData.diary) {
    appData.diary = [];
  }
  
  const entry = {
    id: Date.now().toString(),
    title: title || null,
    content: content,
    date: new Date().toISOString()
  };
  
  appData.diary.push(entry);
  saveData();
  renderDiary();
  closeDiaryEntryModal();
}

function formatDiaryDate(isoString) {
  const date = new Date(isoString);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  const dateStr = date.toDateString();
  if (dateStr === today.toDateString()) {
    return `Сегодня, ${hours}:${minutes}`;
  } else if (dateStr === yesterday.toDateString()) {
    return `Вчера, ${hours}:${minutes}`;
  } else {
    const months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
    return `${day} ${months[date.getMonth()]} ${year}, ${hours}:${minutes}`;
  }
}

// Wishlist
function renderWishlist() {
  const container = document.getElementById('wishlist-items');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!appData.wishlist || appData.wishlist.length === 0) {
    container.innerHTML = '<p class="empty-state">Нет желаний</p>';
    return;
  }
  
  appData.wishlist.forEach(wish => {
    const wishEl = document.createElement('div');
    wishEl.className = 'wish-item';
    wishEl.innerHTML = `
      <div class="wish-content">
        <div class="wish-name">${wish.name}</div>
        ${wish.price ? `<div class="wish-price">${wish.price} ₽</div>` : ''}
        ${wish.description ? `<div class="wish-description">${wish.description}</div>` : ''}
      </div>
    `;
    container.appendChild(wishEl);
  });
}

function openWishModal() {
  document.getElementById('wish-modal').classList.add('active');
  document.getElementById('wish-name-input').value = '';
  document.getElementById('wish-price-input').value = '';
  document.getElementById('wish-description-input').value = '';
  setTimeout(() => document.getElementById('wish-name-input').focus(), 100);
}

function closeWishModal() {
  document.getElementById('wish-modal').classList.remove('active');
  document.getElementById('wish-name-input').value = '';
  document.getElementById('wish-price-input').value = '';
  document.getElementById('wish-description-input').value = '';
}

function saveWish() {
  const nameInput = document.getElementById('wish-name-input');
  const priceInput = document.getElementById('wish-price-input');
  const descriptionInput = document.getElementById('wish-description-input');
  
  // Валидация названия
  const nameValidation = validateTaskText(nameInput.value);
  if (!nameValidation.valid) {
    alert('Ошибка в названии: ' + nameValidation.error);
    nameInput.focus();
    return;
  }
  
  // Валидация цены
  let price = null;
  if (priceInput.value) {
    const priceValidation = validateNumber(priceInput.value, { min: 0, max: 10000000, required: false });
    if (!priceValidation.valid) {
      alert('Ошибка в цене: ' + priceValidation.error);
      priceInput.focus();
      return;
    }
    price = priceValidation.value;
  }
  
  // Валидация описания
  let description = null;
  if (descriptionInput.value.trim()) {
    const descValidation = validateTaskText(descriptionInput.value);
    if (!descValidation.valid) {
      alert('Ошибка в описании: ' + descValidation.error);
      descriptionInput.focus();
      return;
    }
    description = descValidation.value;
  }
  
  const name = nameValidation.value;
  
  if (!appData.wishlist) {
    appData.wishlist = [];
  }
  
  const wish = {
    id: Date.now().toString(),
    name: name,
    price: price || null,
    description: description || null,
    date: new Date().toISOString()
  };
  
  appData.wishlist.push(wish);
  saveData();
  renderWishlist();
  closeWishModal();
}

// Профиль
function openProfileModal() {
  updateProfileAvatar();
  loadProfileData();
  document.getElementById('profile-modal').classList.add('active');
}

function closeProfileModal() {
  document.getElementById('profile-modal').classList.remove('active');
}

function loadProfileData() {
  const nameInput = document.getElementById('profile-name-input');
  const gender = appData.profile?.gender || 'none';
  
  if (nameInput) {
    nameInput.value = appData.profile?.name || 'Ребёнок';
  }
  
  // Обновляем выбор пола
  document.querySelectorAll('.gender-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.gender === gender) {
      btn.classList.add('active');
    }
  });
  
  // Применяем цвета при загрузке
  applyGenderColors(gender);
}

function selectGender(gender) {
  // Обновляем визуальный выбор
  document.querySelectorAll('.gender-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.gender === gender) {
      btn.classList.add('active');
    }
  });
  
  // Сохраняем выбор
  if (!appData.profile) {
    appData.profile = { avatar: null, name: 'Ребёнок', gender: 'none' };
  }
  appData.profile.gender = gender;
  saveData();
  
  // Применяем цвета
  applyGenderColors(gender);
}

function applyGenderColors(gender) {
  const root = document.documentElement;
  
  switch(gender) {
    case 'girl':
      // Розовый для девочки
      root.style.setProperty('--primary-color', '#ff8ccf');
      root.style.setProperty('--accent-color', '#ff5fa2');
      root.style.setProperty('--header-bg', '#ff8ccf');
      root.style.setProperty('--body-gradient-start', '#fff0f6');
      root.style.setProperty('--body-gradient-end', '#f5f6ff');
      break;
    case 'boy':
      // Синий для мальчика
      root.style.setProperty('--primary-color', '#3b82f6');
      root.style.setProperty('--accent-color', '#60a5fa');
      root.style.setProperty('--header-bg', '#3b82f6');
      root.style.setProperty('--body-gradient-start', '#eff6ff');
      root.style.setProperty('--body-gradient-end', '#dbeafe');
      break;
    default:
      // Зелёный универсальный
      root.style.setProperty('--primary-color', '#10b981');
      root.style.setProperty('--accent-color', '#14b8a6');
      root.style.setProperty('--header-bg', '#10b981');
      root.style.setProperty('--body-gradient-start', '#f0fdf4');
      root.style.setProperty('--body-gradient-end', '#ecfdf5');
  }
  
  // Обновляем header
  const header = document.querySelector('header');
  if (header) {
    header.style.background = `var(--header-bg)`;
  }
  
  // Обновляем body gradient
  document.body.style.background = `linear-gradient(180deg, var(--body-gradient-start), var(--body-gradient-end))`;
  
  // Обновляем theme-color
  const themeColor = document.querySelector('meta[name="theme-color"]');
  if (themeColor) {
    themeColor.setAttribute('content', `var(--primary-color)`);
  }
}

function saveProfile() {
  const nameInput = document.getElementById('profile-name-input');
  
  // Валидация имени
  const nameValidation = validateTaskText(nameInput.value);
  if (!nameValidation.valid) {
    alert('Ошибка в имени: ' + nameValidation.error);
    nameInput.focus();
    return;
  }
  
  if (!appData.profile) {
    appData.profile = { avatar: null, name: 'Ребёнок', gender: 'none' };
  }
  
  appData.profile.name = nameValidation.value;
  
  if (!saveData()) {
    return;
  }
  
  // Применяем цвета сохранённого пола
  applyGenderColors(appData.profile.gender || 'none');
  
  // Обновляем имя в шапке
  updateProfileAvatar();
  
  closeProfileModal();
}

function updateProfileAvatar() {
  const avatarEl = document.getElementById('profile-avatar');
  const avatarLargeEl = document.getElementById('profile-avatar-large');
  const headerNameEl = document.getElementById('header-name');
  
  if (appData.profile?.avatar) {
    if (avatarEl) {
      avatarEl.style.backgroundImage = `url(${appData.profile.avatar})`;
      avatarEl.textContent = '';
    }
    if (avatarLargeEl) {
      avatarLargeEl.style.backgroundImage = `url(${appData.profile.avatar})`;
      avatarLargeEl.textContent = '';
    }
  } else {
    if (avatarEl) {
      avatarEl.style.backgroundImage = '';
      avatarEl.textContent = '👤';
    }
    if (avatarLargeEl) {
      avatarLargeEl.style.backgroundImage = '';
      avatarLargeEl.textContent = '👤';
    }
  }
  
  // Обновляем имя в шапке
  if (headerNameEl) {
    const name = appData.profile?.name || 'Ребёнок';
    headerNameEl.textContent = name;
  }
}

// Конвертация звёзд в деньги
function openStarsExchangeModal() {
  try {
    const modal = document.getElementById('stars-exchange-modal');
    if (!modal) return;
    
    // Инициализация stars если отсутствует
    if (!appData.stars) {
      appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
    }
    
    const totalStars = appData.stars.total || 0;
    const starsToMoney = getStarsToMoney();
    const moneyPerStars = getMoneyPerStars();
    
    // Обновляем данные в модальном окне
    const totalStarsEl = document.getElementById('exchange-total-stars');
    if (totalStarsEl) {
      totalStarsEl.textContent = totalStars;
    }
    
    const rateTextEl = document.getElementById('exchange-rate-text');
    if (rateTextEl) {
      rateTextEl.textContent = `${starsToMoney} ⭐ = ${moneyPerStars} ₽`;
    }
    
    const inputEl = document.getElementById('exchange-stars-input');
    if (inputEl) {
      inputEl.value = '';
      inputEl.max = totalStars;
      
      // Обработчик изменения количества звёзд
      inputEl.oninput = function() {
        updateExchangePreview();
      };
    }
    
    // Обновляем предпросмотр
    updateExchangePreview();
    
    modal.classList.add('active');
    
    // Фокус на поле ввода
    setTimeout(() => {
      if (inputEl) inputEl.focus();
    }, 100);
  } catch (error) {
    console.error('Ошибка при открытии модального окна конвертации:', error);
  }
}

function closeStarsExchangeModal() {
  const modal = document.getElementById('stars-exchange-modal');
  if (modal) {
    modal.classList.remove('active');
  }
  
  const inputEl = document.getElementById('exchange-stars-input');
  if (inputEl) {
    inputEl.value = '';
    inputEl.oninput = null;
  }
}

function updateExchangePreview() {
  try {
    const inputEl = document.getElementById('exchange-stars-input');
    if (!inputEl) return;
    
    const starsToExchange = parseInt(inputEl.value) || 0;
    const totalStars = appData.stars?.total || 0;
    const starsToMoney = getStarsToMoney();
    const moneyPerStars = getMoneyPerStars();
    
    if (starsToExchange <= 0 || starsToExchange > totalStars) {
      // Скрываем результаты если неверное значение
      const moneyResultEl = document.getElementById('exchange-money-result');
      const starsRemainingEl = document.getElementById('exchange-stars-remaining');
      const submitBtn = document.getElementById('exchange-submit-btn');
      
      if (moneyResultEl) moneyResultEl.textContent = '0 ₽';
      if (starsRemainingEl) starsRemainingEl.textContent = `${totalStars} ⭐`;
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
      }
      return;
    }
    
    // Вычисляем сколько полных наборов можно обменять
    const fullSets = Math.floor(starsToExchange / starsToMoney);
    const moneyToReceive = fullSets * moneyPerStars;
    const starsRemaining = totalStars - (fullSets * starsToMoney);
    
    // Обновляем результаты
    const moneyResultEl = document.getElementById('exchange-money-result');
    const starsRemainingEl = document.getElementById('exchange-stars-remaining');
    const submitBtn = document.getElementById('exchange-submit-btn');
    
    if (moneyResultEl) {
      moneyResultEl.textContent = `${moneyToReceive} ₽`;
    }
    
    if (starsRemainingEl) {
      starsRemainingEl.textContent = `${starsRemaining} ⭐`;
    }
    
    if (submitBtn) {
      submitBtn.disabled = (fullSets === 0);
      submitBtn.style.opacity = fullSets === 0 ? '0.5' : '1';
    }
  } catch (error) {
    console.error('Ошибка при обновлении предпросмотра конвертации:', error);
  }
}

function exchangeStarsToMoney() {
  try {
    const inputEl = document.getElementById('exchange-stars-input');
    if (!inputEl) return;
    
    const starsToExchange = parseInt(inputEl.value) || 0;
    const totalStars = appData.stars?.total || 0;
    const starsToMoney = getStarsToMoney();
    const moneyPerStars = getMoneyPerStars();
    
    // Валидация
    if (starsToExchange <= 0) {
      alert('Введите количество звёзд больше 0');
      inputEl.focus();
      return;
    }
    
    if (starsToExchange > totalStars) {
      alert('У вас недостаточно звёзд');
      inputEl.focus();
      return;
    }
    
    // Вычисляем сколько полных наборов можно обменять
    const fullSets = Math.floor(starsToExchange / starsToMoney);
    
    if (fullSets === 0) {
      alert(`Для обмена нужно минимум ${starsToMoney} звёзд`);
      inputEl.focus();
      return;
    }
    
    const moneyToReceive = fullSets * moneyPerStars;
    const starsToDeduct = fullSets * starsToMoney;
    
    // Инициализация данных если отсутствуют
    if (!appData.stars) {
      appData.stars = { today: 0, total: 0, history: [], streak: { current: 0, lastDate: null, history: [] }, claimedRewards: [] };
    }
    if (!appData.piggy) {
      appData.piggy = { amount: 0, goal: { name: '', amount: 0 }, history: [] };
    }
    if (!appData.piggy.history || !Array.isArray(appData.piggy.history)) {
      appData.piggy.history = [];
    }
    
    // Сохраняем исходное состояние для отката
    const originalStarsTotal = appData.stars.total;
    const originalPiggyAmount = appData.piggy.amount;
    const originalHistoryLength = appData.piggy.history.length;
    
    // Вычитаем звёзды
    appData.stars.total = Math.max(0, appData.stars.total - starsToDeduct);
    
    // Добавляем деньги в кошелек, а не в копилку
    if (!appData.wallet) {
      appData.wallet = { amount: 0, history: [] };
    }
    if (!appData.wallet.history || !Array.isArray(appData.wallet.history)) {
      appData.wallet.history = [];
    }
    
    const originalWalletAmount = appData.wallet.amount || 0;
    const originalWalletHistoryLength = appData.wallet.history.length;
    
    appData.wallet.amount = (appData.wallet.amount || 0) + moneyToReceive;
    appData.wallet.history.push({
      date: new Date().toISOString(),
      type: 'add',
      amount: moneyToReceive,
      description: `Обмен ${starsToDeduct} ⭐ на ${moneyToReceive} ₽`
    });
    
    // Добавляем в историю звёзд
    addStarHistory(`Обменено ${starsToDeduct} ⭐ на ${moneyToReceive} ₽`, -starsToDeduct);
    
    if (!saveData()) {
      // Откатываем изменение при ошибке сохранения
      appData.stars.total = originalStarsTotal;
      appData.wallet.amount = originalWalletAmount;
      appData.wallet.history = appData.wallet.history.slice(0, originalWalletHistoryLength);
      alert('Ошибка при сохранении. Попробуйте позже.');
      return;
    }
    
    // Обновляем интерфейс
    updateStars();
    renderMoney();
    
    // Показываем успешное сообщение
    alert(`Успешно обменено ${starsToDeduct} ⭐ на ${moneyToReceive} ₽!`);
    
    // Закрываем модальное окно
    closeStarsExchangeModal();
  } catch (error) {
    console.error('Ошибка при конвертации звёзд в деньги:', error);
    alert('Ошибка при конвертации. Попробуйте позже.');
  }
}

let cropImageData = null;
let cropState = {
  scale: 1,
  x: 0,
  y: 0,
  isDragging: false,
  startX: 0,
  startY: 0,
  startImageX: 0,
  startImageY: 0,
  imageWidth: 0,
  imageHeight: 0
};

function handleAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Валидация файла согласно rules.md
  const validation = validateImageFile(file);
  if (!validation.valid) {
    alert(validation.error);
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    cropImageData = e.target.result;
    openCropModal();
  };
  reader.readAsDataURL(file);
  
  // Сбрасываем input для возможности повторной загрузки того же файла
  event.target.value = '';
}

function openCropModal() {
  const cropImage = document.getElementById('crop-image');
  const cropModal = document.getElementById('crop-modal');
  const cropPreview = document.getElementById('crop-preview');
  
  if (!cropImage || !cropModal || !cropImageData || !cropPreview) return;
  
  cropImage.src = cropImageData;
  
  cropImage.onload = () => {
    // Инициализация состояния
    const previewSize = 300; // Размер круглой области
    const imgAspect = cropImage.naturalWidth / cropImage.naturalHeight;
    
    // Вычисляем начальный размер изображения
    if (imgAspect > 1) {
      cropState.imageWidth = previewSize * 1.2;
      cropState.imageHeight = cropState.imageWidth / imgAspect;
    } else {
      cropState.imageHeight = previewSize * 1.2;
      cropState.imageWidth = cropState.imageHeight * imgAspect;
    }
    
    cropState.scale = 1;
    cropState.x = 0;
    cropState.y = 0;
    
    updateCropImageTransform();
    setupCropInteractions();
    
    cropModal.classList.add('active');
  };
}

function setupCropInteractions() {
  const cropImage = document.getElementById('crop-image');
  const cropPreview = document.getElementById('crop-preview');
  if (!cropImage || !cropPreview) return;
  
  // Очистка предыдущих обработчиков
  const newImage = cropImage.cloneNode(true);
  cropImage.parentNode.replaceChild(newImage, cropImage);
  
  const image = document.getElementById('crop-image');
  
  // Перемещение мышью
  image.addEventListener('mousedown', (e) => {
    e.preventDefault();
    cropState.isDragging = true;
    cropState.startX = e.clientX;
    cropState.startY = e.clientY;
    cropState.startImageX = cropState.x;
    cropState.startImageY = cropState.y;
    image.style.cursor = 'grabbing';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (!cropState.isDragging) return;
    
    const deltaX = e.clientX - cropState.startX;
    const deltaY = e.clientY - cropState.startY;
    
    cropState.x = cropState.startImageX + deltaX;
    cropState.y = cropState.startImageY + deltaY;
    
    updateCropImageTransform();
  });
  
  document.addEventListener('mouseup', () => {
    if (cropState.isDragging) {
      cropState.isDragging = false;
      image.style.cursor = 'grab';
    }
  });
  
  // Масштабирование колесом мыши
  cropPreview.addEventListener('wheel', (e) => {
    e.preventDefault();
    
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.5, Math.min(3, cropState.scale * delta));
    
    // Масштабирование относительно центра превью
    const rect = cropPreview.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;
    
    cropState.x = mouseX - (mouseX - cropState.x) * (newScale / cropState.scale);
    cropState.y = mouseY - (mouseY - cropState.y) * (newScale / cropState.scale);
    cropState.scale = newScale;
    
    updateCropImageTransform();
  });
  
  // Touch события для мобильных
  let touchStartDistance = 0;
  let touchStartScale = 1;
  let touchStartX = 0;
  let touchStartY = 0;
  
  image.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      // Одно касание - перемещение
      cropState.isDragging = true;
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      cropState.startImageX = cropState.x;
      cropState.startImageY = cropState.y;
    } else if (e.touches.length === 2) {
      // Два касания - масштабирование
      cropState.isDragging = false;
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      touchStartDistance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      touchStartScale = cropState.scale;
    }
  });
  
  image.addEventListener('touchmove', (e) => {
    e.preventDefault();
    
    if (e.touches.length === 1 && cropState.isDragging) {
      // Перемещение
      const deltaX = e.touches[0].clientX - touchStartX;
      const deltaY = e.touches[0].clientY - touchStartY;
      
      cropState.x = cropState.startImageX + deltaX;
      cropState.y = cropState.startImageY + deltaY;
      
      updateCropImageTransform();
    } else if (e.touches.length === 2) {
      // Масштабирование
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      
      const scale = touchStartScale * (distance / touchStartDistance);
      cropState.scale = Math.max(0.5, Math.min(3, scale));
      
      updateCropImageTransform();
    }
  });
  
  image.addEventListener('touchend', () => {
    cropState.isDragging = false;
  });
  
  image.style.cursor = 'grab';
}

function updateCropImageTransform() {
  const cropImage = document.getElementById('crop-image');
  if (!cropImage) return;
  
  const scaledWidth = cropState.imageWidth * cropState.scale;
  const scaledHeight = cropState.imageHeight * cropState.scale;
  
  cropImage.style.width = `${scaledWidth}px`;
  cropImage.style.height = `${scaledHeight}px`;
  cropImage.style.transform = `translate(calc(-50% + ${cropState.x}px), calc(-50% + ${cropState.y}px))`;
}

function closeCropModal() {
  document.getElementById('crop-modal').classList.remove('active');
  cropImageData = null;
  cropState = {
    scale: 1,
    x: 0,
    y: 0,
    isDragging: false,
    startX: 0,
    startY: 0,
    startImageX: 0,
    startImageY: 0,
    imageWidth: 0,
    imageHeight: 0
  };
}

function applyCrop() {
  if (!cropImageData) return;
  
  const cropImage = document.getElementById('crop-image');
  if (!cropImage) return;
  
  // Создаём canvas для кадрирования
  const canvas = document.createElement('canvas');
  const size = 400; // Размер итогового аватара
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  
  // Создаём временное изображение для работы
  const img = new Image();
  img.onload = () => {
    const previewSize = 300; // Размер области превью
    const canvasScale = size / previewSize; // Масштаб для canvas
    
    // Вычисляем размеры изображения в превью (в пикселях превью)
    const previewImageWidth = cropState.imageWidth * cropState.scale;
    const previewImageHeight = cropState.imageHeight * cropState.scale;
    
    // Вычисляем размеры изображения в canvas (в пикселях canvas)
    const canvasImageWidth = previewImageWidth * canvasScale;
    const canvasImageHeight = previewImageHeight * canvasScale;
    
    // Центр canvas
    const canvasCenterX = size / 2;
    const canvasCenterY = size / 2;
    
    // Смещение изображения в canvas координатах
    // cropState.x и cropState.y - это смещение в пикселях превью
    const canvasOffsetX = cropState.x * canvasScale;
    const canvasOffsetY = cropState.y * canvasScale;
    
    // Позиция для рисования (верхний левый угол изображения)
    const drawX = canvasCenterX - (canvasImageWidth / 2) + canvasOffsetX;
    const drawY = canvasCenterY - (canvasImageHeight / 2) + canvasOffsetY;
    
    // Рисуем круглую маску
    ctx.save();
    ctx.beginPath();
    ctx.arc(canvasCenterX, canvasCenterY, size / 2, 0, Math.PI * 2);
    ctx.clip();
    
    // Рисуем изображение
    ctx.drawImage(img, drawX, drawY, canvasImageWidth, canvasImageHeight);
    
    ctx.restore();
    
    // Конвертируем в base64
    const croppedDataUrl = canvas.toDataURL('image/png', 0.9);
    
    // Сохраняем
    if (!appData.profile) {
      appData.profile = { avatar: null, name: 'Ребёнок', gender: 'none' };
    }
    appData.profile.avatar = croppedDataUrl;
    saveData();
    updateProfileAvatar();
    closeCropModal();
  };
  
  img.src = cropImageData;
}

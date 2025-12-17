// ============================================
// МОДУЛЬ РАБОТЫ С ДАННЫМИ (data.js)
// ============================================
// Управление состоянием приложения, загрузка/сохранение данных

// Данные приложения (глобальная переменная)
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

// Загрузка данных из localStorage
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

// Инициализация настроек
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

// Сохранение данных в localStorage
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

// Сброс ежедневных задач
function resetDailyTasks() {
  // Сохраняем статистику дня перед сбросом
  saveDailyStats();
  
  // Сбрасываем чек-лист (но сохраняем задачи)
  appData.checklist.forEach(task => {
    task.completed = false;
  });
  appData.stars.today = 0;
  saveData();
  
  // Обновляем UI (вызываем функции из ui.js)
  if (typeof renderChecklist === 'function') renderChecklist();
  if (typeof updateStars === 'function') updateStars();
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
    // Добавляем в кошелек, а не в копилку
    addMoneyToWallet(bonus, description);
    addMoneyHistory('streak', bonus, description);
    
    // Показываем уведомление (функция из ui.js)
    if (typeof showStreakNotification === 'function') {
      showStreakNotification(streak, bonus);
    }
    
    // Обновляем UI
    if (typeof renderPiggy === 'function') renderPiggy();
  }
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

// Добавление истории звёзд
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
    if (amountNum === 0) {
      // Разрешаем 0 для отрицательных значений (обмен)
      if (amountNum < 0) {
        appData.stars.history.push({
          date: new Date().toISOString(),
          description: description || 'Списание звёзд',
          amount: amountNum
        });
      } else {
        console.error('Ошибка: неверное количество звёзд для истории');
        return;
      }
    } else {
      appData.stars.history.push({
        date: new Date().toISOString(),
        description: description || 'Начисление звёзд',
        amount: amountNum
      });
    }
    
    // Ограничиваем размер истории (последние 100 записей)
    if (appData.stars.history.length > 100) {
      appData.stars.history = appData.stars.history.slice(-100);
    }
    
    saveData();
  } catch (error) {
    console.error('Ошибка при добавлении истории звёзд:', error);
  }
}

// Добавление истории денег
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

// Добавление денег в копилку напрямую
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
    
    // Обновляем UI
    if (typeof renderPiggy === 'function') renderPiggy();
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
    
    // Обновляем UI
    if (typeof renderMoney === 'function') renderMoney();
    return true;
  } catch (error) {
    console.error('Ошибка при добавлении денег в кошелек:', error);
    return false;
  }
}

// Форматирование даты
function formatDate(isoString) {
  const date = new Date(isoString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day}.${month}.${year} ${hours}:${minutes}`;
}

// Форматирование даты для дневника
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


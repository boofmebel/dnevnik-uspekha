/**
 * Система управления темами для "Дневник успеха"
 * Поддерживает автоматическое определение системной темы и ручное переключение
 */

(function() {
  'use strict';

  const THEME_STORAGE_KEY = 'dnevnik_theme';
  const THEME_ATTRIBUTE = 'data-theme';
  
  /**
   * Получить текущую тему из localStorage или системную
   */
  function getCurrentTheme() {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    
    // Определяем системную тему
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  }

  /**
   * Установить тему
   * @param {string} theme - 'light' или 'dark'
   * @param {boolean} save - сохранить в localStorage
   */
  function setTheme(theme, save = true) {
    if (theme !== 'light' && theme !== 'dark') {
      console.warn('Некорректная тема:', theme);
      return;
    }

    const root = document.documentElement;
    
    // Удаляем предыдущую тему
    root.removeAttribute(THEME_ATTRIBUTE);
    
    // Устанавливаем новую тему
    if (theme === 'dark') {
      root.setAttribute(THEME_ATTRIBUTE, 'dark');
    } else {
      root.setAttribute(THEME_ATTRIBUTE, 'light');
    }

    // Сохраняем в localStorage
    if (save) {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    }

    // Обновляем meta theme-color для мобильных браузеров
    updateThemeColor(theme);

    // Вызываем событие для других скриптов
    const event = new CustomEvent('themechange', { detail: { theme } });
    document.dispatchEvent(event);
  }

  /**
   * Обновить meta theme-color
   */
  function updateThemeColor(theme) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }
    
    // Цвета для разных тем
    metaThemeColor.content = theme === 'dark' ? '#1e293b' : '#667eea';
  }

  /**
   * Переключить тему (light <-> dark)
   */
  function toggleTheme() {
    const current = getCurrentTheme();
    const newTheme = current === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    return newTheme;
  }

  /**
   * Инициализация темы при загрузке страницы
   */
  function initTheme() {
    const theme = getCurrentTheme();
    setTheme(theme, false); // Не сохраняем при инициализации, т.к. уже есть в localStorage
    
    // Слушаем изменения системной темы (если пользователь не выбрал тему вручную)
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      // Обработчик изменения системной темы
      const handleSystemThemeChange = (e) => {
        // Применяем системную тему только если пользователь не выбрал тему вручную
        const stored = localStorage.getItem(THEME_STORAGE_KEY);
        if (!stored) {
          const systemTheme = e.matches ? 'dark' : 'light';
          setTheme(systemTheme, false);
        }
      };

      // Поддержка addEventListener для современных браузеров
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemThemeChange);
      } else {
        // Fallback для старых браузеров
        mediaQuery.addListener(handleSystemThemeChange);
      }
    }
  }

  /**
   * Создать кнопку переключения темы
   * @param {HTMLElement} container - контейнер для кнопки
   */
  function createThemeToggle(container) {
    if (!container) {
      console.warn('Контейнер для кнопки темы не найден');
      return;
    }

    const button = document.createElement('button');
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', 'Переключить тему');
    button.setAttribute('title', 'Переключить тему');
    
    // Иконки для светлой и темной темы
    const lightIcon = '☀️';
    const darkIcon = '🌙';
    
    function updateButtonIcon() {
      const currentTheme = getCurrentTheme();
      button.textContent = currentTheme === 'light' ? darkIcon : lightIcon;
    }

    button.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleTheme();
      updateButtonIcon();
    });

    // Обновляем иконку при изменении темы
    document.addEventListener('themechange', updateButtonIcon);
    
    updateButtonIcon();
    container.appendChild(button);
  }

  // Инициализация при загрузке DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }

  // Экспорт функций для использования в других скриптах
  window.themeManager = {
    setTheme,
    toggleTheme,
    getCurrentTheme,
    createThemeToggle
  };

})();



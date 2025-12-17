// Утилиты для безопасности и валидации
// Согласно rules.md: безопасность, валидация, обработка ошибок

/**
 * Санитизация текста для безопасного отображения
 * Защита от XSS атак
 */
function sanitizeText(text) {
  if (typeof text !== 'string') {
    return String(text || '');
  }
  
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Валидация и санитизация текста задачи
 */
function validateTaskText(text) {
  if (!text || typeof text !== 'string') {
    return { valid: false, error: 'Текст задачи не может быть пустым' };
  }
  
  const trimmed = text.trim();
  if (trimmed.length === 0) {
    return { valid: false, error: 'Текст задачи не может быть пустым' };
  }
  
  if (trimmed.length > 500) {
    return { valid: false, error: 'Текст задачи слишком длинный (максимум 500 символов)' };
  }
  
  return { valid: true, value: trimmed };
}

/**
 * Валидация числа (для денег, звёзд и т.д.)
 */
function validateNumber(value, options = {}) {
  const { min = 0, max = Number.MAX_SAFE_INTEGER, required = true } = options;
  
  if (value === null || value === undefined) {
    if (required) {
      return { valid: false, error: 'Значение обязательно' };
    }
    return { valid: true, value: 0 };
  }
  
  const num = Number(value);
  
  if (isNaN(num)) {
    return { valid: false, error: 'Неверное числовое значение' };
  }
  
  if (num < min) {
    return { valid: false, error: `Значение должно быть не меньше ${min}` };
  }
  
  if (num > max) {
    return { valid: false, error: `Значение должно быть не больше ${max}` };
  }
  
  return { valid: true, value: Math.floor(num) };
}

/**
 * Безопасное создание элемента с текстом
 * Альтернатива innerHTML для защиты от XSS
 */
function createTextElement(tag, text, className = '') {
  const el = document.createElement(tag);
  if (className) {
    el.className = className;
  }
  el.textContent = text || '';
  return el;
}

/**
 * Безопасная установка текста в элемент
 */
function setTextContent(element, text) {
  if (!element) return;
  element.textContent = text || '';
}

/**
 * Безопасный парсинг JSON с обработкой ошибок
 */
function safeJsonParse(jsonString, defaultValue = null) {
  if (!jsonString || typeof jsonString !== 'string') {
    return defaultValue;
  }
  
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    console.error('Ошибка парсинга JSON:', error);
    return defaultValue;
  }
}

/**
 * Проверка размера данных перед сохранением в localStorage
 */
function checkStorageSize(data) {
  try {
    const jsonString = JSON.stringify(data);
    const sizeInBytes = new Blob([jsonString]).size;
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    if (sizeInBytes > maxSize) {
      return { 
        valid: false, 
        error: `Данные слишком большие (${(sizeInBytes / 1024 / 1024).toFixed(2)}MB). Максимум 5MB.` 
      };
    }
    
    return { valid: true, size: sizeInBytes };
  } catch (error) {
    return { valid: false, error: 'Ошибка при проверке размера данных' };
  }
}

/**
 * Валидация даты
 */
function validateDate(dateString) {
  if (!dateString) {
    return { valid: false, error: 'Дата не указана' };
  }
  
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) {
    return { valid: false, error: 'Неверный формат даты' };
  }
  
  return { valid: true, value: date };
}

/**
 * Валидация файла изображения
 */
function validateImageFile(file) {
  if (!file) {
    return { valid: false, error: 'Файл не выбран' };
  }
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 5 * 1024 * 1024; // 5MB
  
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Разрешены только изображения (JPEG, PNG, GIF, WebP)' };
  }
  
  if (file.size > maxSize) {
    return { valid: false, error: 'Размер файла не должен превышать 5MB' };
  }
  
  return { valid: true };
}


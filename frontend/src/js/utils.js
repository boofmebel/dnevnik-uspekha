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

/**
 * Валидация email адреса
 */
function validateEmail(email) {
  if (!email || typeof email !== 'string') {
    return { valid: false, error: 'Email не указан' };
  }
  
  const trimmed = email.trim();
  if (trimmed.length === 0) {
    return { valid: false, error: 'Email не может быть пустым' };
  }
  
  // Простая проверка формата email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmed)) {
    return { valid: false, error: 'Неверный формат email адреса' };
  }
  
  if (trimmed.length > 254) {
    return { valid: false, error: 'Email слишком длинный (максимум 254 символа)' };
  }
  
  return { valid: true, value: trimmed.toLowerCase() };
}

/**
 * Валидация URL
 */
function validateUrl(url) {
  if (!url || typeof url !== 'string') {
    return { valid: false, error: 'URL не указан' };
  }
  
  const trimmed = url.trim();
  if (trimmed.length === 0) {
    return { valid: false, error: 'URL не может быть пустым' };
  }
  
  try {
    const urlObj = new URL(trimmed);
    // Проверяем протокол (только http/https)
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return { valid: false, error: 'URL должен использовать протокол http или https' };
    }
    return { valid: true, value: trimmed };
  } catch (error) {
    return { valid: false, error: 'Неверный формат URL' };
  }
}

/**
 * Валидация имени пользователя
 */
function validateUsername(username) {
  if (!username || typeof username !== 'string') {
    return { valid: false, error: 'Имя пользователя не указано' };
  }
  
  const trimmed = username.trim();
  if (trimmed.length === 0) {
    return { valid: false, error: 'Имя пользователя не может быть пустым' };
  }
  
  if (trimmed.length < 2) {
    return { valid: false, error: 'Имя пользователя должно содержать минимум 2 символа' };
  }
  
  if (trimmed.length > 50) {
    return { valid: false, error: 'Имя пользователя слишком длинное (максимум 50 символов)' };
  }
  
  // Разрешаем только буквы, цифры, пробелы, дефисы и подчёркивания
  const usernameRegex = /^[a-zA-Zа-яА-ЯёЁ0-9\s\-_]+$/u;
  if (!usernameRegex.test(trimmed)) {
    return { valid: false, error: 'Имя пользователя содержит недопустимые символы' };
  }
  
  return { valid: true, value: trimmed };
}

/**
 * Валидация ID (числового или строкового)
 */
function validateId(id, options = {}) {
  const { type = 'auto', required = true } = options;
  
  if (id === null || id === undefined) {
    if (required) {
      return { valid: false, error: 'ID обязателен' };
    }
    return { valid: true, value: null };
  }
  
  if (type === 'number' || (type === 'auto' && typeof id === 'number')) {
    const num = Number(id);
    if (isNaN(num) || num <= 0 || !Number.isInteger(num)) {
      return { valid: false, error: 'ID должен быть положительным целым числом' };
    }
    return { valid: true, value: num };
  }
  
  if (type === 'string' || (type === 'auto' && typeof id === 'string')) {
    const str = String(id).trim();
    if (str.length === 0) {
      return { valid: false, error: 'ID не может быть пустой строкой' };
    }
    if (str.length > 100) {
      return { valid: false, error: 'ID слишком длинный (максимум 100 символов)' };
    }
    return { valid: true, value: str };
  }
  
  return { valid: false, error: 'Неверный тип ID' };
}

/**
 * Валидация структуры объекта данных
 */
function validateDataStructure(data, schema) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return { valid: false, error: 'Данные должны быть объектом' };
  }
  
  if (!schema || typeof schema !== 'object') {
    return { valid: false, error: 'Схема валидации не указана' };
  }
  
  const errors = [];
  
  for (const [key, validator] of Object.entries(schema)) {
    if (validator.required && !(key in data)) {
      errors.push(`Поле "${key}" обязательно`);
      continue;
    }
    
    if (!(key in data)) {
      continue; // Пропускаем необязательные поля
    }
    
    const value = data[key];
    let result;
    
    if (typeof validator.validate === 'function') {
      result = validator.validate(value);
    } else if (validator.type === 'string') {
      result = validateTaskText(value);
    } else if (validator.type === 'number') {
      result = validateNumber(value, validator.options || {});
    } else if (validator.type === 'email') {
      result = validateEmail(value);
    } else if (validator.type === 'date') {
      result = validateDate(value);
    } else {
      result = { valid: true, value: value };
    }
    
    if (!result.valid) {
      errors.push(`Поле "${key}": ${result.error}`);
    }
  }
  
  if (errors.length > 0) {
    return { valid: false, error: errors.join('; ') };
  }
  
  return { valid: true };
}


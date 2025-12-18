// ============================================
// ГЛОБАЛЬНАЯ ОБРАБОТКА ОШИБОК (error-handler.js)
// ============================================
// Согласно rules.md: обработка ошибок, логирование, безопасность

/**
 * Уровни логирования
 */
const LogLevel = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR'
};

/**
 * Определение окружения (development/production)
 */
const isProduction = window.location.hostname !== 'localhost' && 
                     window.location.hostname !== '127.0.0.1' &&
                     !window.location.hostname.startsWith('192.168.');

/**
 * Структурированное логирование
 */
function log(level, message, context = {}) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    level,
    message,
    context,
    url: window.location.href,
    userAgent: navigator.userAgent
  };
  
  // В продакшене отправляем в консоль в формате JSON
  // В будущем можно отправлять на сервер
  if (isProduction) {
    console.log(JSON.stringify(logEntry));
  } else {
    // В разработке выводим читабельно
    console[level.toLowerCase()] || console.log(`[${level}] ${message}`, context);
  }
}

/**
 * Обработка глобальных ошибок JavaScript
 */
window.onerror = function(message, source, lineno, colno, error) {
  const errorContext = {
    message: String(message),
    source: String(source),
    lineno: Number(lineno),
    colno: Number(colno),
    stack: error ? error.stack : null,
    errorName: error ? error.name : null
  };
  
  log(LogLevel.ERROR, 'Uncaught JavaScript Error', errorContext);
  
  // В продакшене не показываем alert пользователю
  // В разработке показываем для отладки
  if (!isProduction) {
    console.error('Global error:', errorContext);
  }
  
  // Возвращаем false, чтобы браузер обработал ошибку стандартным способом
  return false;
};

/**
 * Обработка необработанных Promise rejections
 */
window.addEventListener('unhandledrejection', function(event) {
  const errorContext = {
    reason: event.reason,
    promise: event.promise,
    stack: event.reason && event.reason.stack ? event.reason.stack : null
  };
  
  log(LogLevel.ERROR, 'Unhandled Promise Rejection', errorContext);
  
  // Предотвращаем вывод ошибки в консоль браузера
  event.preventDefault();
  
  // В продакшене не показываем alert
  if (!isProduction) {
    console.error('Unhandled promise rejection:', errorContext);
  }
});

/**
 * Безопасная обёртка для выполнения функций с обработкой ошибок
 */
function safeExecute(fn, context = 'unknown') {
  try {
    return fn();
  } catch (error) {
    log(LogLevel.ERROR, `Error in ${context}`, {
      error: error.message,
      stack: error.stack,
      context: context
    });
    
    // В продакшене не показываем alert
    if (!isProduction) {
      console.error(`Error in ${context}:`, error);
    }
    
    return null;
  }
}

/**
 * Асинхронная безопасная обёртка
 */
async function safeExecuteAsync(fn, context = 'unknown') {
  try {
    return await fn();
  } catch (error) {
    log(LogLevel.ERROR, `Async error in ${context}`, {
      error: error.message,
      stack: error.stack,
      context: context
    });
    
    if (!isProduction) {
      console.error(`Async error in ${context}:`, error);
    }
    
    return null;
  }
}

/**
 * Обработка ошибок localStorage
 */
function handleStorageError(error, operation = 'storage') {
  const errorContext = {
    operation,
    errorName: error.name,
    errorMessage: error.message,
    errorCode: error.code
  };
  
  log(LogLevel.ERROR, `Storage error in ${operation}`, errorContext);
  
  // Специфичная обработка для разных типов ошибок
  if (error.name === 'QuotaExceededError' || error.code === 22) {
    log(LogLevel.WARN, 'Storage quota exceeded', errorContext);
    return {
      success: false,
      error: 'Недостаточно места в хранилище. Попробуйте удалить старые данные.'
    };
  } else if (error.name === 'SecurityError' || error.code === 18) {
    log(LogLevel.ERROR, 'Storage security error', errorContext);
    return {
      success: false,
      error: 'Ошибка доступа к хранилищу. Проверьте настройки браузера.'
    };
  } else {
    return {
      success: false,
      error: 'Ошибка при работе с хранилищем.'
    };
  }
}

/**
 * Инициализация обработки ошибок
 */
function initErrorHandling() {
  log(LogLevel.INFO, 'Error handling initialized', {
    isProduction,
    userAgent: navigator.userAgent,
    url: window.location.href
  });
  
  // Обработка ошибок загрузки ресурсов
  window.addEventListener('error', function(event) {
    // Игнорируем ошибки из других источников (CORS)
    if (event.target !== window && event.target.tagName) {
      const resourceContext = {
        tag: event.target.tagName,
        src: event.target.src || event.target.href,
        type: event.target.tagName === 'IMG' ? 'image' : 
              event.target.tagName === 'SCRIPT' ? 'script' : 
              event.target.tagName === 'LINK' ? 'stylesheet' : 'unknown'
      };
      
      log(LogLevel.WARN, 'Resource loading error', resourceContext);
    }
  }, true); // Используем capture phase
  
  log(LogLevel.INFO, 'Error handlers registered');
}

// Инициализация при загрузке модуля
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initErrorHandling);
} else {
  initErrorHandling();
}

// Экспорт функций для использования в других модулях
window.errorHandler = {
  log,
  safeExecute,
  safeExecuteAsync,
  handleStorageError,
  LogLevel,
  isProduction
};


/**
 * Авторизация для пользовательского сайта
 * Обработка входа и регистрации
 */

// Глобальный apiClient (должен быть определен в api.js)
if (typeof apiClient === 'undefined') {
  console.error('apiClient не определен! Убедитесь, что api.js загружен перед auth-user.js');
}

// Переключение между входом и регистрацией
function switchToRegister() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form-modal').style.display = 'block';
  document.getElementById('auth-subtitle').textContent = 'Регистрация родителя';
  hideLoginError();
  hideRegisterError();
}

function switchToLogin() {
  document.getElementById('register-form-modal').style.display = 'none';
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('auth-subtitle').textContent = 'Вход';
  hideLoginError();
  hideRegisterError();
}

// Показ/скрытие ошибок
function showLoginError(message) {
  const errorEl = document.getElementById('login-error-message');
  errorEl.textContent = message;
  errorEl.style.display = 'block';
  errorEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideLoginError() {
  document.getElementById('login-error-message').style.display = 'none';
}

function showRegisterError(message) {
  const errorEl = document.getElementById('register-error-message');
  errorEl.textContent = message;
  errorEl.style.display = 'block';
  errorEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideRegisterError() {
  document.getElementById('register-error-message').style.display = 'none';
}

// Форматирование номера телефона
function formatPhoneInput(input) {
  let value = input.value.replace(/\D/g, '');
  
  if (value.startsWith('7') || value.startsWith('8')) {
    value = value.substring(1);
  }
  
  if (value.length > 10) {
    value = value.substring(0, 10);
  }
  
  let formatted = '';
  if (value.length > 0) {
    formatted = '(' + value.substring(0, 3);
  }
  if (value.length > 3) {
    formatted += ') ' + value.substring(3, 6);
  }
  if (value.length > 6) {
    formatted += '-' + value.substring(6, 8);
  }
  if (value.length > 8) {
    formatted += '-' + value.substring(8, 10);
  }
  
  input.value = formatted;
}

// Нормализация номера телефона
function normalizePhone(phone) {
  const digits = phone.replace(/\D/g, '');
  
  if (digits.startsWith('8')) {
    return '+7' + digits.substring(1);
  }
  
  if (digits.startsWith('7')) {
    return '+' + digits;
  }
  
  return '+7' + digits;
}

// Валидация номера телефона
function validatePhone(phone) {
  const normalized = normalizePhone(phone);
  return /^\+7\d{10}$/.test(normalized);
}

// Переключение видимости пароля
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  const wrapper = input.closest('.password-input-wrapper');
  if (!wrapper) return;
  
  const button = wrapper.querySelector('.password-toggle');
  if (!button) return;
  
  if (input.type === 'password') {
    input.type = 'text';
    button.textContent = '🙈';
  } else {
    input.type = 'password';
    button.textContent = '👁️';
  }
}

// Проверка авторизации
function checkAuth() {
  // Согласно rules.md: токены не хранятся в localStorage
  // Проверяем только токен в памяти (apiClient)
  const token = apiClient.getAccessToken();
  if (token && token.trim()) {
    showApp();
    return true;
  }
  showAuthModal();
  return false;
}

// Показать модальное окно авторизации
function showAuthModal() {
  document.getElementById('auth-modal').style.display = 'flex';
  document.getElementById('app-content').style.display = 'none';
  // Сбрасываем формы
  document.getElementById('login-form').reset();
  document.getElementById('register-form-modal').reset();
  hideLoginError();
  hideRegisterError();
}

// Показать приложение
function showApp() {
  document.getElementById('auth-modal').style.display = 'none';
  document.getElementById('app-content').style.display = 'block';
}

// Вход
async function handleLogin(event) {
  if (event) event.preventDefault();
  
  const phoneInput = document.getElementById('login-phone-input');
  const passwordInput = document.getElementById('login-password-input');
  const loginButton = document.getElementById('login-button');
  
  const phone = phoneInput.value.trim();
  const password = passwordInput.value;
  
  if (!phone) {
    showLoginError('Введите номер телефона');
    phoneInput.focus();
    return;
  }
  
  if (!validatePhone(phone)) {
    showLoginError('Неверный формат номера телефона');
    phoneInput.focus();
    return;
  }
  
  if (!password) {
    showLoginError('Введите пароль');
    passwordInput.focus();
    return;
  }
  
  loginButton.disabled = true;
  loginButton.textContent = 'Вход...';
  hideLoginError();
  
  try {
    const normalizedPhone = normalizePhone(phone);
    
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: normalizedPhone,
        password: password
      }),
    });
    
    if (!response.ok) {
      let errorMessage = 'Ошибка входа';
      try {
        const data = await response.json();
        errorMessage = data.detail || errorMessage;
      } catch (e) {
        errorMessage = `Ошибка ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }
    
    const data = await response.json();
    
    if (!data.access_token) {
      throw new Error('Токен не получен');
    }
    
    // Согласно rules.md: access token хранится только в памяти
    apiClient.setAccessToken(data.access_token);
    // localStorage.setItem('user_token', data.access_token); // Удалено: токены не хранятся в localStorage
    // localStorage.setItem('user_role', data.user?.role || 'parent'); // Опционально, если нужно сохранить роль
    
    // Показываем приложение
    showApp();
    
    // Перезагружаем данные
    if (typeof loadData === 'function') {
      loadData();
    }
    
    // Обновляем имя в шапке если есть
    updateHeaderName(data.user?.name);
    
  } catch (error) {
    console.error('Ошибка входа:', error);
    showLoginError(error.message || 'Ошибка входа. Проверьте данные.');
    loginButton.disabled = false;
    loginButton.textContent = 'Войти';
  }
}

// Регистрация
async function handleRegister(event) {
  if (event) event.preventDefault();
  
  const phoneInput = document.getElementById('register-phone-input');
  const nameInput = document.getElementById('register-name-input');
  const passwordInput = document.getElementById('register-password-input');
  const registerButton = document.getElementById('register-button-modal');
  
  const phone = phoneInput.value.trim();
  const name = nameInput.value.trim();
  const password = passwordInput.value;
  
  if (!phone) {
    showRegisterError('Введите номер телефона');
    phoneInput.focus();
    return;
  }
  
  if (!validatePhone(phone)) {
    showRegisterError('Неверный формат номера телефона. Используйте формат +7 (XXX) XXX-XX-XX');
    phoneInput.focus();
    return;
  }
  
  if (!name || name.length < 2) {
    showRegisterError('Введите ваше имя (минимум 2 символа)');
    nameInput.focus();
    return;
  }
  
  if (!password || password.length < 8) {
    showRegisterError('Пароль должен содержать минимум 8 символов');
    passwordInput.focus();
    return;
  }
  
  registerButton.disabled = true;
  registerButton.textContent = 'Регистрация...';
  hideRegisterError();
  
  try {
    const normalizedPhone = normalizePhone(phone);
    
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: normalizedPhone,
        name: name,
        password: password,
        role: 'parent'
      }),
    });
    
    if (!response.ok) {
      let errorMessage = 'Ошибка регистрации';
      try {
        const data = await response.json();
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map(err => {
              const field = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : 'поле';
              return `${field}: ${err.msg || 'Ошибка валидации'}`;
            }).join(', ');
          } else {
            errorMessage = data.detail;
          }
        }
      } catch (e) {
        errorMessage = `Ошибка ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }
    
    const data = await response.json();
    
    if (!data.access_token) {
      throw new Error('Токен не получен после регистрации');
    }
    
    // Согласно rules.md: access token хранится только в памяти
    apiClient.setAccessToken(data.access_token);
    // localStorage.setItem('user_token', data.access_token); // Удалено: токены не хранятся в localStorage
    // localStorage.setItem('user_role', data.user?.role || 'parent'); // Опционально, если нужно сохранить роль
    
    // Показываем приложение
    showApp();
    
    // Перезагружаем данные
    if (typeof loadData === 'function') {
      loadData();
    }
    
    // Обновляем имя в шапке если есть
    updateHeaderName(data.user?.name);
    
  } catch (error) {
    console.error('Ошибка регистрации:', error);
    showRegisterError(error.message || 'Ошибка регистрации. Попробуйте еще раз.');
    registerButton.disabled = false;
    registerButton.textContent = 'Зарегистрироваться';
  }
}

// Выход
function handleLogout() {
  // Согласно rules.md: токены не хранятся в localStorage
  // localStorage.removeItem('user_token'); // Удалено
  // localStorage.removeItem('admin_token'); // Удалено
  apiClient.setAccessToken(null);
  showAuthModal();
  
  // Сбрасываем данные приложения
  if (typeof clearAllData === 'function') {
    clearAllData();
  }
}

// Обработка 401 ошибок в API
function setup401Handler() {
  const originalRequest = apiClient.request.bind(apiClient);
  
  apiClient.request = async function(endpoint, options = {}) {
    try {
      return await originalRequest(endpoint, options);
    } catch (error) {
      // Если получили 401, показываем окно входа
      if (error.message && (
        error.message.includes('401') || 
        error.message.includes('авторизац') || 
        error.message.includes('Требуется')
      )) {
        console.log('⚠️ Требуется авторизация, показываем окно входа');
        showAuthModal();
        throw error;
      }
      throw error;
    }
  };
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
  // Настройка обработчиков форм
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form-modal');
  
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }
  
  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
  }
  
  // Форматирование телефона при вводе
  const loginPhoneInput = document.getElementById('login-phone-input');
  const registerPhoneInput = document.getElementById('register-phone-input');
  
  if (loginPhoneInput) {
    loginPhoneInput.addEventListener('input', () => {
      formatPhoneInput(loginPhoneInput);
      hideLoginError();
    });
  }
  
  if (registerPhoneInput) {
    registerPhoneInput.addEventListener('input', () => {
      formatPhoneInput(registerPhoneInput);
      hideRegisterError();
    });
  }
  
  // Настройка обработчика 401 ошибок
  setup401Handler();
  
  // Проверка авторизации
  checkAuth();
});

// Обновление имени в шапке
function updateHeaderName(name) {
  if (name) {
    const headerNameEl = document.getElementById('header-name');
    if (headerNameEl) {
      headerNameEl.textContent = name;
    }
  }
}

// Экспорт функций для использования в других модулях
window.showAuthModal = showAuthModal;
window.handleLogout = handleLogout;
window.checkAuth = checkAuth;
window.switchToLogin = switchToLogin;
window.switchToRegister = switchToRegister;
window.togglePassword = togglePassword;
window.updateHeaderName = updateHeaderName;


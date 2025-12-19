/**
 * Страница регистрации
 * Регистрация родителя по номеру телефона
 */

// Форматирование номера телефона при вводе
function formatPhoneInput(input) {
  let value = input.value.replace(/\D/g, ''); // Удаляем все нецифровые символы
  
  // Если начинается с 7 или 8, убираем первую цифру (она будет заменена на +7)
  if (value.startsWith('7') || value.startsWith('8')) {
    value = value.substring(1);
  }
  
  // Ограничиваем до 10 цифр (после +7)
  if (value.length > 10) {
    value = value.substring(0, 10);
  }
  
  // Форматируем: (XXX) XXX-XX-XX
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

// Нормализация номера телефона для отправки на сервер
function normalizePhone(phone) {
  // Удаляем все символы кроме цифр
  const digits = phone.replace(/\D/g, '');
  
  // Если начинается с 8, заменяем на 7
  if (digits.startsWith('8')) {
    return '+7' + digits.substring(1);
  }
  
  // Если начинается с 7, добавляем +
  if (digits.startsWith('7')) {
    return '+' + digits;
  }
  
  // Иначе добавляем +7
  return '+7' + digits;
}

// Валидация номера телефона
function validatePhone(phone) {
  const normalized = normalizePhone(phone);
  // Проверяем формат +7XXXXXXXXXX (12 символов: +7 и 10 цифр)
  return /^\+7\d{10}$/.test(normalized);
}

// Переключение видимости пароля
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (!input) {
    console.error('Input not found:', inputId);
    return;
  }
  
  // Находим кнопку внутри password-input-wrapper
  const wrapper = input.closest('.password-input-wrapper');
  if (!wrapper) {
    console.error('Password wrapper not found for:', inputId);
    return;
  }
  
  const button = wrapper.querySelector('.password-toggle');
  if (!button) {
    console.error('Password toggle button not found');
    return;
  }
  
  if (input.type === 'password') {
    input.type = 'text';
    button.textContent = '🙈';
    button.setAttribute('aria-label', 'Скрыть пароль');
  } else {
    input.type = 'password';
    button.textContent = '👁️';
    button.setAttribute('aria-label', 'Показать пароль');
  }
}

// Показ ошибки
function showError(message) {
  const errorEl = document.getElementById('error-message');
  errorEl.textContent = message;
  errorEl.style.display = 'block';
  
  // Прокрутка к ошибке
  errorEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Скрытие ошибки
function hideError() {
  const errorEl = document.getElementById('error-message');
  errorEl.style.display = 'none';
}

// Обработка формы регистрации
document.addEventListener('DOMContentLoaded', () => {
  const phoneInput = document.getElementById('phone-input');
  const registerForm = document.getElementById('register-form');
  const registerButton = document.getElementById('register-button');
  
  // Форматирование телефона при вводе
  phoneInput.addEventListener('input', () => {
    formatPhoneInput(phoneInput);
    hideError();
  });
  
  // Обработка отправки формы
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();
    
    const phone = phoneInput.value.trim();
    const name = document.getElementById('name-input').value.trim();
    const password = document.getElementById('password-input').value;
    
    // Валидация
    if (!phone) {
      showError('Введите номер телефона');
      phoneInput.focus();
      return;
    }
    
    if (!validatePhone(phone)) {
      showError('Неверный формат номера телефона. Используйте формат +7 (XXX) XXX-XX-XX');
      phoneInput.focus();
      return;
    }
    
    if (!name || name.length < 2) {
      showError('Введите ваше имя (минимум 2 символа)');
      document.getElementById('name-input').focus();
      return;
    }
    
    if (!password || password.length < 8) {
      showError('Пароль должен содержать минимум 8 символов');
      document.getElementById('password-input').focus();
      return;
    }
    
    // Отправка запроса
    registerButton.disabled = true;
    registerButton.textContent = 'Регистрация...';
    
    try {
      const normalizedPhone = normalizePhone(phone);
      
      // Используем относительный путь - nginx проксирует на backend
      const apiBaseUrl = '/api';
      
      // Формируем тело запроса
      const requestBody = {
        phone: normalizedPhone,
        name: name.trim(),
        password: password,
        role: 'parent'
      };
      
      const response = await fetch(`${apiBaseUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        let errorMessage = 'Ошибка регистрации';
        try {
          const data = await response.json();
          console.error('Ошибка регистрации:', data);
          // Обрабатываем разные форматы ошибок
          if (data.detail) {
            if (Array.isArray(data.detail)) {
              // Pydantic validation errors
              errorMessage = data.detail.map(err => {
                const field = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : (err.loc ? err.loc.join('.') : 'поле');
                const msg = err.msg || 'Ошибка валидации';
                return `${field}: ${msg}`;
              }).join(', ');
            } else {
              errorMessage = data.detail;
            }
          } else if (data.details && Array.isArray(data.details)) {
            // Альтернативный формат
            errorMessage = data.details.map(err => {
              const field = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : (err.loc ? err.loc.join('.') : 'поле');
              const msg = err.msg || 'Ошибка валидации';
              return `${field}: ${msg}`;
            }).join(', ');
          } else if (data.message) {
            errorMessage = data.message;
          } else if (data.error) {
            errorMessage = data.error;
          }
        } catch (e) {
          // Если не удалось распарсить JSON, используем статус
          errorMessage = `Ошибка ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      
      // Проверяем успешность регистрации
      if (!data.access_token) {
        throw new Error('Токен не получен после регистрации');
      }
      
      // Согласно rules.md: access token хранится только в памяти
      apiClient.setAccessToken(data.access_token);
      // localStorage.setItem('admin_token', data.access_token); // Удалено: токены не хранятся в localStorage
      // localStorage.setItem('user_token', data.access_token); // Удалено: токены не хранятся в localStorage
      // localStorage.setItem('user_role', data.user?.role || 'parent'); // Опционально, если нужно сохранить роль
      
      // Показываем сообщение об успехе
      hideError();
      registerButton.textContent = '✅ Регистрация успешна!';
      registerButton.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
      registerButton.disabled = true;
      
      // Показываем уведомление
      const successMessage = document.createElement('div');
      successMessage.className = 'success-message';
      successMessage.style.cssText = `
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        animation: slideDown 0.5s ease-out;
      `;
      successMessage.textContent = '🎉 Регистрация прошла успешно! Перенаправление...';
      
      const form = document.getElementById('register-form');
      form.insertBefore(successMessage, form.firstChild);
      
      // Добавляем стиль для анимации
      if (!document.getElementById('register-animations')) {
        const style = document.createElement('style');
        style.id = 'register-animations';
        style.textContent = `
          @keyframes slideDown {
            from {
              opacity: 0;
              transform: translateY(-20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `;
        document.head.appendChild(style);
      }
      
      // Перенаправляем на главную страницу приложения для пользователя
      setTimeout(() => {
        window.location.href = '/';
      }, 1500);
      
    } catch (error) {
      console.error('Ошибка регистрации:', error);
      showError(error.message || 'Ошибка регистрации. Попробуйте еще раз.');
      registerButton.disabled = false;
      registerButton.textContent = 'Зарегистрироваться';
      registerButton.style.background = '';
    }
  });
});


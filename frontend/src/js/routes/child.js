/**
 * Маршрут /child
 * Интерфейс ребенка
 * 
 * Защита: проверяет роль через /api/auth/me перед показом UI
 * Поддержка входа по QR-коду через параметр qr_token в URL
 */
async function handleChildRoute() {
  console.log('👧 Загрузка интерфейса ребенка...');
  
  // Проверяем, есть ли qr_token в URL (вход по QR-коду)
  const urlParams = new URLSearchParams(window.location.search);
  const qrToken = urlParams.get('qr_token');
  
  if (qrToken) {
    console.log('📱 Обнаружен QR-токен в URL, выполняю вход...');
    try {
      // Выполняем вход по QR-коду
      const response = await apiClient.post('/auth/child-qr', {
        qr_token: qrToken
      });
      
      if (response && response.access_token) {
        // Сохраняем токен
        apiClient.setAccessToken(response.access_token);
        console.log('✅ Вход по QR-коду успешен');
        
        // Убираем qr_token из URL
        const newUrl = window.location.pathname;
        window.history.replaceState({}, '', newUrl);
        
        // Проверяем, требуется ли установка PIN
        if (response.user && response.user.pin_required) {
          console.log('🔐 Требуется установка PIN');
          // Показываем модальное окно для установки PIN
          await showPinSetupModal(response.user);
          return; // Не продолжаем загрузку интерфейса до установки PIN
        }
        
        // Продолжаем загрузку интерфейса ребенка
      } else {
        throw new Error('Токен не получен от сервера');
      }
    } catch (error) {
      console.error('❌ Ошибка входа по QR-коду:', error);
      alert('Ошибка входа по QR-коду. Возможно, код устарел или недействителен.');
      router.navigate('/', true);
      return;
    }
  }
  
  // Загружаем модуль аутентификации ребенка если нужно
  if (typeof window.checkChildAuth === 'undefined') {
    const script = document.createElement('script');
    script.src = '/src/js/child-auth.js';
    document.body.appendChild(script);
    await new Promise((resolve) => {
      script.onload = resolve;
    });
  }
  
  // Проверяем аутентификацию ребенка
  const isAuthenticated = await window.checkChildAuth();
  if (!isAuthenticated) {
    // Показывается экран входа в checkChildAuth
    return;
  }
  
  // ЗАЩИТА МАРШРУТА: проверяем роль через /api/auth/me
  const token = apiClient.getAccessToken();
  if (!token) {
    // Нет токена - показываем экран входа
    await window.showChildLoginScreen();
    return;
  }
  
  try {
    const me = await apiClient.get('/auth/me');
    
    // Проверка роли
    if (me.role !== 'child') {
      console.warn('⚠️ Доступ запрещён: роль не child');
      await window.showChildLoginScreen();
      return;
    }
    
    // Роль child подтверждена - показываем контент ребенка
    const childContent = document.getElementById('child-content');
    const mainContent = document.getElementById('app-content');
    const parentContent = document.getElementById('parent-content');
    const adminContent = document.getElementById('admin-content');
    const authModal = document.getElementById('auth-modal');
    
    // Скрываем форму входа и другие контенты
    if (authModal) {
      authModal.style.display = 'none';
      console.log('✅ handleChildRoute: форма входа скрыта');
    }
    if (childContent) {
      childContent.style.display = 'block';
      console.log('✅ handleChildRoute: контент ребенка показан');
    }
    if (mainContent) {
      mainContent.style.display = 'none';
    }
    if (parentContent) {
      parentContent.style.display = 'none';
    }
    if (adminContent) {
      adminContent.style.display = 'none';
    }
    
    // Загружаем скрипт ребенка если еще не загружен
    if (typeof initChildApp === 'undefined') {
      const script = document.createElement('script');
      script.src = '/src/js/child.js';
      document.body.appendChild(script);
      // Ждем загрузки скрипта
      await new Promise((resolve) => {
        script.onload = resolve;
      });
    }
    
    // Инициализируем приложение ребенка
    if (typeof initChildApp === 'function') {
      await initChildApp();
    }
  } catch (e) {
    // 401 или другая ошибка - пробуем обновить токен
    const refreshed = await apiClient.refreshToken();
    if (refreshed) {
      apiClient.setAccessToken(refreshed);
      // Повторяем проверку
      return handleChildRoute();
    }
    // Если не удалось обновить - редирект на главную
    console.error('❌ Ошибка проверки авторизации:', e);
    router.navigate('/', true);
  }
}

/**
 * Показ модального окна для установки PIN
 */
async function showPinSetupModal(user) {
  return new Promise((resolve) => {
    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.id = 'child-pin-setup-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 10002;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    
    modal.innerHTML = `
      <div style="
        background: white;
        border-radius: 24px;
        padding: 32px;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
      ">
        <h2 style="
          margin: 0 0 20px 0;
          text-align: center;
          font-size: 24px;
          font-weight: 700;
          color: #0f172a;
        ">🔐 Установите PIN-код</h2>
        <p style="
          margin: 0 0 24px 0;
          text-align: center;
          font-size: 14px;
          color: #64748b;
        ">Придумайте PIN-код для входа в приложение</p>
        <form id="pin-setup-form" onsubmit="return false;">
          <div style="margin-bottom: 20px;">
            <label style="
              display: block;
              margin-bottom: 8px;
              font-size: 14px;
              font-weight: 600;
              color: #0f172a;
            ">PIN-код (4-6 цифр)</label>
            <input 
              type="password" 
              id="pin-input" 
              pattern="[0-9]{4,6}" 
              maxlength="6"
              required
              autocomplete="off"
              style="
                width: 100%;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 18px;
                text-align: center;
                letter-spacing: 4px;
                font-family: monospace;
              "
              placeholder="0000"
            />
          </div>
          <div style="margin-bottom: 20px;">
            <label style="
              display: block;
              margin-bottom: 8px;
              font-size: 14px;
              font-weight: 600;
              color: #0f172a;
            ">Подтвердите PIN-код</label>
            <input 
              type="password" 
              id="pin-confirm-input" 
              pattern="[0-9]{4,6}" 
              maxlength="6"
              required
              autocomplete="off"
              style="
                width: 100%;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 18px;
                text-align: center;
                letter-spacing: 4px;
                font-family: monospace;
              "
              placeholder="0000"
            />
          </div>
          <div id="pin-error" style="
            color: #ef4444;
            font-size: 14px;
            margin-bottom: 20px;
            text-align: center;
            display: none;
          "></div>
          <button 
            type="submit"
            id="pin-setup-submit"
            style="
              width: 100%;
              padding: 16px;
              font-size: 16px;
              font-weight: 600;
              border-radius: 12px;
              background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
              color: white;
              border: none;
              cursor: pointer;
              transition: all 0.3s ease;
            "
            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(167, 139, 250, 0.4)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
          >
            Сохранить PIN-код
          </button>
        </form>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Обработчик отправки формы
    const form = document.getElementById('pin-setup-form');
    const pinInput = document.getElementById('pin-input');
    const pinConfirmInput = document.getElementById('pin-confirm-input');
    const errorDiv = document.getElementById('pin-error');
    const submitBtn = document.getElementById('pin-setup-submit');
    
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const pin = pinInput.value;
      const pinConfirm = pinConfirmInput.value;
      
      // Валидация
      if (pin.length < 4 || pin.length > 6) {
        errorDiv.textContent = 'PIN-код должен содержать от 4 до 6 цифр';
        errorDiv.style.display = 'block';
        return;
      }
      
      if (pin !== pinConfirm) {
        errorDiv.textContent = 'PIN-коды не совпадают';
        errorDiv.style.display = 'block';
        return;
      }
      
      // Отправляем PIN на сервер
      try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Сохранение...';
        
        await apiClient.post('/auth/child-set-pin', {
          pin: pin
        });
        
        console.log('✅ PIN-код установлен');
        
        // Закрываем модальное окно
        document.body.removeChild(modal);
        
        // Продолжаем загрузку интерфейса ребенка
        resolve();
        await handleChildRoute();
      } catch (error) {
        console.error('❌ Ошибка установки PIN:', error);
        errorDiv.textContent = error.message || 'Ошибка установки PIN-кода';
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Сохранить PIN-код';
      }
    });
    
    // Фокус на первом поле
    pinInput.focus();
  });
}

window.handleChildRoute = handleChildRoute;
window.showPinSetupModal = showPinSetupModal;




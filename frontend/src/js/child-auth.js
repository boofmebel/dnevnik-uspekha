/**
 * Модуль аутентификации ребенка
 * Поддерживает вход по PIN или биометрии (отпечаток/Face ID)
 */

let currentChildId = null;

/**
 * Проверка токена и показ экрана входа при необходимости
 */
async function checkChildAuth() {
  const token = apiClient.getAccessToken();
  
  if (!token) {
    // Нет токена - показываем экран входа
    await showChildLoginScreen();
    return false;
  }
  
  try {
    // Проверяем токен
    const me = await apiClient.get('/auth/me');
    
    if (me.role !== 'child') {
      // Не ребенок - показываем экран входа
      await showChildLoginScreen();
      return false;
    }
    
    // Сохраняем ID ребенка
    currentChildId = me.child_id || me.id;
    
    return true;
  } catch (error) {
    console.error('❌ Ошибка проверки токена:', error);
    // Токен недействителен - показываем экран входа
    await showChildLoginScreen();
    return false;
  }
}

/**
 * Показ экрана входа для ребенка
 * Показывает экран с камерой для автоматического сканирования QR-кода
 */
async function showChildLoginScreen() {
  // Скрываем все контенты
  const childContent = document.getElementById('child-content');
  const mainContent = document.getElementById('app-content');
  const parentContent = document.getElementById('parent-content');
  const authModal = document.getElementById('auth-modal');
  
  if (childContent) {
    childContent.style.display = 'none';
  }
  if (mainContent) {
    mainContent.style.display = 'none';
  }
  if (parentContent) {
    parentContent.style.display = 'none';
  }
  if (authModal) {
    authModal.style.display = 'none';
  }
  
  // Создаем или показываем экран с камерой
  let loginScreen = document.getElementById('child-login-screen');
  if (!loginScreen) {
    loginScreen = createChildQRScannerScreen();
    document.body.appendChild(loginScreen);
  }
  
  loginScreen.style.display = 'flex';
  
  // Запускаем сканирование QR-кода
  await startQRScanner();
}

/**
 * Создание экрана входа для ребенка
 */
function createChildLoginScreen() {
  const screen = document.createElement('div');
  screen.id = 'child-login-screen';
  screen.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  `;
  
  screen.innerHTML = `
    <div style="
      background: white;
      border-radius: 24px;
      padding: 40px;
      max-width: 400px;
      width: 100%;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
      text-align: center;
    ">
      <div style="
        font-size: 64px;
        margin-bottom: 24px;
      ">👧</div>
      <h2 style="
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
      ">Вход в приложение</h2>
      <p style="
        margin: 0 0 32px 0;
        font-size: 14px;
        color: #64748b;
      ">Введите PIN-код или используйте биометрию</p>
      
      <form id="child-login-form" onsubmit="return false;" style="margin-bottom: 20px;">
        <div style="margin-bottom: 20px;">
          <input 
            type="password" 
            id="child-pin-input" 
            pattern="[0-9]{4,6}" 
            maxlength="6"
            required
            autocomplete="off"
            placeholder="PIN-код"
            style="
              width: 100%;
              padding: 16px;
              border: 2px solid #e2e8f0;
              border-radius: 12px;
              font-size: 20px;
              text-align: center;
              letter-spacing: 4px;
              font-family: monospace;
              box-sizing: border-box;
            "
          />
        </div>
        <div id="child-login-error" style="
          color: #ef4444;
          font-size: 14px;
          margin-bottom: 20px;
          text-align: center;
          display: none;
          min-height: 20px;
        "></div>
        <button 
          type="submit"
          id="child-login-submit"
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
            margin-bottom: 16px;
          "
          onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(167, 139, 250, 0.4)'"
          onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
        >
          Войти
        </button>
      </form>
      
      <button 
        id="child-biometric-btn"
        onclick="handleChildBiometricLogin()"
        style="
          width: 100%;
          padding: 16px;
          font-size: 16px;
          font-weight: 600;
          border-radius: 12px;
          background: #f8f9fa;
          color: #64748b;
          border: 2px solid #e2e8f0;
          cursor: pointer;
          transition: all 0.3s ease;
          display: none;
        "
        onmouseover="this.style.background='#f1f3f5'; this.style.borderColor='#cbd5e1'"
        onmouseout="this.style.background='#f8f9fa'; this.style.borderColor='#e2e8f0'"
      >
        🔐 Войти с биометрией
      </button>
    </div>
  `;
  
  // Обработчик отправки формы
  const form = document.getElementById('child-login-form');
  const pinInput = document.getElementById('child-pin-input');
  const errorDiv = document.getElementById('child-login-error');
  const submitBtn = document.getElementById('child-login-submit');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleChildPinLogin();
  });
  
  // Фокус на поле ввода
  pinInput.focus();
  
  return screen;
}

/**
 * Обработка входа по PIN
 */
async function handleChildPinLogin() {
  const pinInput = document.getElementById('child-pin-input');
  const errorDiv = document.getElementById('child-login-error');
  const submitBtn = document.getElementById('child-login-submit');
  
  const pin = pinInput.value;
  
  if (!pin || pin.length < 4 || pin.length > 6) {
    errorDiv.textContent = 'PIN должен содержать от 4 до 6 цифр';
    errorDiv.style.display = 'block';
    return;
  }
  
  if (!currentChildId) {
    errorDiv.textContent = 'ID ребенка не найден';
    errorDiv.style.display = 'block';
    return;
  }
  
  try {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Вход...';
    errorDiv.style.display = 'none';
    
    const response = await apiClient.post('/auth/child-pin', {
      child_id: currentChildId,
      pin: pin
    });
    
    if (response && response.access_token) {
      // Сохраняем токен
      apiClient.setAccessToken(response.access_token);
      
      // Сохраняем child_id в localStorage
      localStorage.setItem('child_id', currentChildId.toString());
      
      console.log('✅ Вход по PIN успешен');
      
      // Скрываем экран входа
      const loginScreen = document.getElementById('child-login-screen');
      if (loginScreen) {
        loginScreen.style.display = 'none';
      }
      
      // Показываем контент ребенка
      const childContent = document.getElementById('child-content');
      if (childContent) {
        childContent.style.display = 'block';
      }
      
      // Перезагружаем маршрут
      if (typeof handleChildRoute === 'function') {
        await handleChildRoute();
      } else if (window.router) {
        window.router.navigate('/child', true);
      }
    } else {
      throw new Error('Токен не получен от сервера');
    }
  } catch (error) {
    console.error('❌ Ошибка входа по PIN:', error);
    const errorMessage = error.message || 'Неверный PIN-код';
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = 'block';
    pinInput.value = '';
    pinInput.focus();
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Войти';
  }
}

/**
 * Проверка поддержки биометрии
 */
async function checkBiometricSupport() {
  if (!window.PublicKeyCredential) {
    return false;
  }
  
  try {
    // Проверяем доступность биометрии
    const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    return available;
  } catch (error) {
    console.warn('⚠️ Ошибка проверки биометрии:', error);
    return false;
  }
}

/**
 * Обработка входа по биометрии
 */
async function handleChildBiometricLogin() {
  const errorDiv = document.getElementById('child-login-error');
  const biometricBtn = document.getElementById('child-biometric-btn');
  
  if (!currentChildId) {
    errorDiv.textContent = 'ID ребенка не найден';
    errorDiv.style.display = 'block';
    return;
  }
  
  try {
    biometricBtn.disabled = true;
    biometricBtn.textContent = 'Проверка...';
    errorDiv.style.display = 'none';
    
    // Проверяем поддержку биометрии
    const supported = await checkBiometricSupport();
    if (!supported) {
      throw new Error('Биометрия не поддерживается на этом устройстве');
    }
    
    // Создаем challenge для WebAuthn
    const challengeResponse = await apiClient.post('/auth/child-biometric-challenge', {
      child_id: currentChildId
    });
    
    if (!challengeResponse || !challengeResponse.challenge) {
      throw new Error('Не удалось получить challenge для биометрии');
    }
    
    // Запрашиваем биометрию
    const credential = await navigator.credentials.get({
      publicKey: {
        challenge: Uint8Array.from(challengeResponse.challenge, c => c.charCodeAt(0)),
        rpId: window.location.hostname,
        allowCredentials: challengeResponse.allowCredentials || [],
        userVerification: 'required',
        timeout: 60000
      }
    });
    
    // Отправляем credential на сервер
    const response = await apiClient.post('/auth/child-biometric-verify', {
      child_id: currentChildId,
      credential: {
        id: credential.id,
        rawId: Array.from(new Uint8Array(credential.rawId)),
        response: {
          authenticatorData: Array.from(new Uint8Array(credential.response.authenticatorData)),
          clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON)),
          signature: Array.from(new Uint8Array(credential.response.signature)),
          userHandle: credential.response.userHandle ? Array.from(new Uint8Array(credential.response.userHandle)) : null
        },
        type: credential.type
      }
    });
    
    if (response && response.access_token) {
      // Сохраняем токен
      apiClient.setAccessToken(response.access_token);
      
      // Сохраняем child_id в localStorage
      localStorage.setItem('child_id', currentChildId.toString());
      
      console.log('✅ Вход по биометрии успешен');
      
      // Скрываем экран входа
      const loginScreen = document.getElementById('child-login-screen');
      if (loginScreen) {
        loginScreen.style.display = 'none';
      }
      
      // Показываем контент ребенка
      const childContent = document.getElementById('child-content');
      if (childContent) {
        childContent.style.display = 'block';
      }
      
      // Перезагружаем маршрут
      if (typeof handleChildRoute === 'function') {
        await handleChildRoute();
      } else if (window.router) {
        window.router.navigate('/child', true);
      }
    } else {
      throw new Error('Токен не получен от сервера');
    }
  } catch (error) {
    console.error('❌ Ошибка входа по биометрии:', error);
    const errorMessage = error.message || 'Ошибка биометрической аутентификации';
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = 'block';
    
    // Если ошибка не связана с отменой пользователем
    if (!error.message.includes('NotAllowedError') && !error.message.includes('AbortError')) {
      // Можно показать более подробное сообщение
    }
  } finally {
    biometricBtn.disabled = false;
    biometricBtn.textContent = '🔐 Войти с биометрией';
  }
}

// Экспорт функций
window.checkChildAuth = checkChildAuth;
window.showChildLoginScreen = showChildLoginScreen;
window.handleChildPinLogin = handleChildPinLogin;
window.handleChildBiometricLogin = handleChildBiometricLogin;
window.checkBiometricSupport = checkBiometricSupport;
window.startQRScanner = startQRScanner;
window.stopQRScanner = stopQRScanner;


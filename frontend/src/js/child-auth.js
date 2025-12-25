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
  console.log('📱 showChildLoginScreen: начало');
  
  // Скрываем все контенты
  const childContent = document.getElementById('child-content');
  const mainContent = document.getElementById('app-content');
  const parentContent = document.getElementById('parent-content');
  const authModal = document.getElementById('auth-modal');
  
  if (childContent) {
    childContent.style.display = 'none';
    console.log('✅ child-content скрыт');
  }
  if (mainContent) {
    mainContent.style.display = 'none';
    console.log('✅ app-content скрыт');
  }
  if (parentContent) {
    parentContent.style.display = 'none';
    console.log('✅ parent-content скрыт');
  }
  if (authModal) {
    authModal.style.display = 'none';
    console.log('✅ auth-modal скрыт');
  }
  
  // Создаем или показываем экран с камерой
  let loginScreen = document.getElementById('child-login-screen');
  if (!loginScreen) {
    console.log('📱 Создаю новый экран с камерой');
    loginScreen = createChildQRScannerScreen();
    document.body.appendChild(loginScreen);
    console.log('✅ Экран с камерой добавлен в DOM');
  } else {
    console.log('📱 Использую существующий экран с камерой');
  }
  
  loginScreen.style.display = 'flex';
  console.log('✅ Экран с камерой показан (display: flex)');
  
  // Запускаем сканирование QR-кода
  console.log('📱 Запускаю сканирование QR-кода');
  try {
    await startQRScanner();
    console.log('✅ Сканирование QR-кода запущено');
  } catch (error) {
    console.error('❌ Ошибка запуска сканирования:', error);
  }
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
 * Создание экрана с камерой для сканирования QR-кода
 */
function createChildQRScannerScreen() {
  const screen = document.createElement('div');
  screen.id = 'child-login-screen';
  screen.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #000;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
  `;
  
  screen.innerHTML = `
    <div style="
      position: relative;
      width: 100%;
      max-width: 500px;
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    ">
      <!-- Видео с камеры -->
      <video 
        id="child-qr-video" 
        autoplay 
        playsinline
        style="
          width: 100%;
          max-width: 400px;
          height: auto;
          border-radius: 16px;
          background: #000;
        "
      ></video>
      
      <!-- Оверлей с рамкой для QR-кода -->
      <div style="
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 250px;
        height: 250px;
        border: 3px solid #a78bfa;
        border-radius: 16px;
        pointer-events: none;
        box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
      ">
        <div style="
          position: absolute;
          top: -2px;
          left: -2px;
          width: 30px;
          height: 30px;
          border-top: 4px solid #a78bfa;
          border-left: 4px solid #a78bfa;
          border-radius: 16px 0 0 0;
        "></div>
        <div style="
          position: absolute;
          top: -2px;
          right: -2px;
          width: 30px;
          height: 30px;
          border-top: 4px solid #a78bfa;
          border-right: 4px solid #a78bfa;
          border-radius: 0 16px 0 0;
        "></div>
        <div style="
          position: absolute;
          bottom: -2px;
          left: -2px;
          width: 30px;
          height: 30px;
          border-bottom: 4px solid #a78bfa;
          border-left: 4px solid #a78bfa;
          border-radius: 0 0 0 16px;
        "></div>
        <div style="
          position: absolute;
          bottom: -2px;
          right: -2px;
          width: 30px;
          height: 30px;
          border-bottom: 4px solid #a78bfa;
          border-right: 4px solid #a78bfa;
          border-radius: 0 0 16px 0;
        "></div>
      </div>
      
      <!-- Canvas для обработки кадров -->
      <canvas id="child-qr-canvas" style="display: none;"></canvas>
      
      <!-- Сообщение об ошибке -->
      <div id="child-qr-error" style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.9);
        color: #ef4444;
        font-size: 16px;
        text-align: center;
        display: none;
        padding: 20px;
        border-radius: 12px;
        max-width: 80%;
        z-index: 10001;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      ">
        <div style="margin-bottom: 16px;">⚠️</div>
        <div id="child-qr-error-text"></div>
        <button onclick="document.getElementById('child-qr-error').style.display='none'; startQRScanner();" style="
          margin-top: 16px;
          padding: 8px 16px;
          background: #a78bfa;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
        ">Закрыть</button>
      </div>
      
      <!-- Инструкция -->
      <p style="
        margin-top: 40px;
        color: white;
        font-size: 16px;
        text-align: center;
        padding: 0 20px;
        line-height: 1.5;
      ">
        Отсканируй QR-код у родителей<br>и пользуйся с удовольствием 😊
      </p>
    </div>
  `;
  
  return screen;
}

/**
 * Запуск сканирования QR-кода
 */
let qrScannerStream = null;
let qrScannerInterval = null;

async function startQRScanner() {
  console.log('📱 startQRScanner: начало');
  
  const video = document.getElementById('child-qr-video');
  const canvas = document.getElementById('child-qr-canvas');
  const errorDiv = document.getElementById('child-qr-error');
  
  if (!video) {
    console.error('❌ Элемент video не найден');
    return;
  }
  if (!canvas) {
    console.error('❌ Элемент canvas не найден');
    return;
  }
  
  console.log('✅ Элементы video и canvas найдены');
  
  // Загружаем библиотеку jsQR если еще не загружена
  if (typeof jsQR === 'undefined') {
    console.log('📚 Загружаю библиотеку jsQR');
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
    document.head.appendChild(script);
    await new Promise((resolve, reject) => {
      script.onload = () => {
        console.log('✅ Библиотека jsQR загружена');
        resolve();
      };
      script.onerror = (error) => {
        console.error('❌ Ошибка загрузки jsQR:', error);
        reject(error);
      };
    });
  } else {
    console.log('✅ Библиотека jsQR уже загружена');
  }
  
  try {
    console.log('📷 Запрашиваю доступ к камере');
    // Запрашиваем доступ к камере
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment', // Задняя камера
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    });
    
    console.log('✅ Доступ к камере получен');
    qrScannerStream = stream;
    video.srcObject = stream;
    if (errorDiv) {
      errorDiv.style.display = 'none';
    }
    
    // Настраиваем canvas
    const ctx = canvas.getContext('2d');
    
    // Обработка кадров для поиска QR-кода
    video.addEventListener('loadedmetadata', () => {
      console.log('✅ Метаданные видео загружены');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      console.log(`📐 Размер canvas: ${canvas.width}x${canvas.height}`);
      
      // Запускаем сканирование
      qrScannerInterval = setInterval(() => {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          
          // Ищем QR-код
          const code = jsQR(imageData.data, imageData.width, imageData.height);
          
          if (code) {
            console.log('✅ QR-код обнаружен:', code.data);
            handleQRCodeDetected(code.data);
          }
        }
      }, 100); // Проверяем каждые 100мс
      console.log('✅ Интервал сканирования запущен');
    });
    
    // Обработка ошибок видео
    video.addEventListener('error', (e) => {
      console.error('❌ Ошибка видео:', e);
    });
    
  } catch (error) {
    console.error('❌ Ошибка доступа к камере:', error);
    if (errorDiv) {
      const errorText = document.getElementById('child-qr-error-text');
      const errorMessage = 'Не удалось получить доступ к камере. Разрешите доступ к камере в настройках браузера.';
      if (errorText) {
        errorText.textContent = errorMessage;
      } else {
        errorDiv.textContent = errorMessage;
      }
      errorDiv.style.display = 'block';
    }
  }
}

/**
 * Обработка обнаруженного QR-кода
 */
async function handleQRCodeDetected(qrData) {
  // Останавливаем сканирование
  stopQRScanner();
  
  // Парсим QR-код (ожидаем URL вида /child?qr_token=... или полный URL)
  let qrToken = null;
  
  try {
    console.log('📱 Распознан QR-код:', qrData);
    
    // Пробуем извлечь токен разными способами
    if (qrData.includes('qr_token=')) {
      // Если это полный URL (http://...)
      if (qrData.startsWith('http://') || qrData.startsWith('https://')) {
        try {
          const url = new URL(qrData);
          qrToken = url.searchParams.get('qr_token');
        } catch (e) {
          // Если не удалось распарсить как URL, пробуем regex
          const match = qrData.match(/qr_token=([^&]+)/);
          if (match) {
            qrToken = decodeURIComponent(match[1]);
          }
        }
      } else {
        // Если это относительный URL (/child?qr_token=...)
        const match = qrData.match(/qr_token=([^&]+)/);
        if (match) {
          qrToken = decodeURIComponent(match[1]);
        }
      }
    } else {
      // Если это просто токен (без URL)
      qrToken = qrData.trim();
    }
    
    if (!qrToken || qrToken.length < 10) {
      throw new Error('QR-код не содержит валидный токен');
    }
    
    console.log('🔑 Извлеченный токен:', qrToken.substring(0, 20) + '...');
    
    // Выполняем вход по QR-коду
    const errorDiv = document.getElementById('child-qr-error');
    errorDiv.style.display = 'none';
    
    try {
      const response = await apiClient.post('/auth/child-qr', {
        qr_token: qrToken
      });
      
      if (response && response.access_token) {
        // Сохраняем токен
        apiClient.setAccessToken(response.access_token);
        console.log('✅ Вход по QR-коду успешен');
        
        // Устанавливаем флаг, что мы только что вошли по QR-коду
        window.justLoggedInViaQR = true;
        
        // Скрываем экран входа
        const loginScreen = document.getElementById('child-login-screen');
        if (loginScreen) {
          loginScreen.style.display = 'none';
        }
        
        // Проверяем, требуется ли установка PIN
        if (response.user && response.user.pin_required) {
          console.log('🔐 Требуется установка PIN');
          // Показываем модальное окно для установки PIN
          if (typeof showPinSetupModal === 'function') {
            await showPinSetupModal(response.user);
            return;
          }
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
      console.error('❌ Ошибка входа по QR-коду:', error);
      
      // Получаем детальное сообщение об ошибке
      let errorMessage = 'Ошибка входа по QR-коду. Возможно, код устарел или недействителен.';
      if (error.message) {
        errorMessage = error.message;
      } else if (error.detail) {
        errorMessage = error.detail;
      } else if (error.response && error.response.detail) {
        errorMessage = error.response.detail;
      }
      
      const errorText = document.getElementById('child-qr-error-text');
      if (errorText) {
        errorText.textContent = errorMessage;
      } else {
        errorDiv.textContent = errorMessage;
      }
      errorDiv.style.display = 'block';
      
      // Перезапускаем сканирование через 3 секунды (если пользователь не закрыл ошибку)
      setTimeout(() => {
        if (errorDiv.style.display !== 'none') {
          errorDiv.style.display = 'none';
          startQRScanner();
        }
      }, 3000);
    }
  } catch (error) {
    console.error('❌ Ошибка обработки QR-кода:', error);
    const errorDiv = document.getElementById('child-qr-error');
    const errorText = document.getElementById('child-qr-error-text');
    const errorMessage = 'Неверный QR-код. Отсканируй QR-код у родителей.';
    
    if (errorText) {
      errorText.textContent = errorMessage;
    } else {
      errorDiv.textContent = errorMessage;
    }
    errorDiv.style.display = 'block';
    
    // Перезапускаем сканирование через 3 секунды (если пользователь не закрыл ошибку)
    setTimeout(() => {
      if (errorDiv.style.display !== 'none') {
        errorDiv.style.display = 'none';
        startQRScanner();
      }
    }, 3000);
  }
}

/**
 * Остановка сканирования QR-кода
 */
function stopQRScanner() {
  if (qrScannerInterval) {
    clearInterval(qrScannerInterval);
    qrScannerInterval = null;
  }
  
  if (qrScannerStream) {
    qrScannerStream.getTracks().forEach(track => track.stop());
    qrScannerStream = null;
  }
  
  const video = document.getElementById('child-qr-video');
  if (video) {
    video.srcObject = null;
  }
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


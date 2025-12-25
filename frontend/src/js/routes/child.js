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
        
        // Устанавливаем флаг, что мы только что вошли по QR-коду
        // Это предотвратит редирект в bootstrapAuth
        window.justLoggedInViaQR = true;
        
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
        
        // Предотвращаем редирект bootstrapAuth - мы уже на правильной странице
        // Просто продолжаем загрузку интерфейса ребенка
        console.log('🔄 Продолжаем загрузку интерфейса ребенка после входа по QR-коду');
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
    
    // Сохраняем роль в window для использования в других модулях
    window.currentUserRole = 'child';
    
    // Инициализируем приложение ребенка
    if (typeof initChildApp === 'function') {
      await initChildApp();
    }
    
    // Ограничиваем права ребенка: скрываем кнопки добавления/редактирования/удаления
    restrictChildPermissions();
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

/**
 * Ограничение прав ребенка
 * Скрывает кнопки добавления/редактирования/удаления для дел и правил
 */
function restrictChildPermissions() {
  console.log('🔒 Ограничение прав ребенка...');
  
  // Скрываем кнопки добавления дел
  const addTaskBtnChecklist = document.querySelector('#checklist .add-btn-small');
  if (addTaskBtnChecklist) {
    addTaskBtnChecklist.style.display = 'none';
  }
  
  // Скрываем кнопки добавления заданий в канбан
  const addTaskBtnKanban = document.querySelector('#kanban .add-btn-small');
  if (addTaskBtnKanban) {
    addTaskBtnKanban.style.display = 'none';
  }
  
  // Скрываем кнопку добавления правил
  const addRuleBtn = document.querySelector('#rules .action-button');
  if (addRuleBtn) {
    addRuleBtn.style.display = 'none';
  }
  
  // Скрываем индикатор "+" на аватаре
  const addChildIndicator = document.querySelector('.add-child-indicator');
  if (addChildIndicator) {
    addChildIndicator.style.display = 'none';
  }
  
  // Изменяем обработчик клика на аватар для ребенка
  const avatarBtn = document.getElementById('parent-avatar-btn');
  if (avatarBtn) {
    avatarBtn.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      openChildAvatarModal();
    };
    avatarBtn.title = 'Изменить аватар';
  }
  
  // Отключаем функции добавления/удаления дел
  if (typeof window.openAddTaskModal === 'function') {
    window.openAddTaskModal = function() {
      console.log('⚠️ Ребенок не может добавлять дела');
    };
  }
  
  if (typeof window.deleteChecklistTask === 'function') {
    window.deleteChecklistTask = function() {
      console.log('⚠️ Ребенок не может удалять дела');
    };
  }
  
  // Отключаем функции добавления/удаления правил
  if (typeof window.openRuleModal === 'function') {
    window.openRuleModal = function() {
      console.log('⚠️ Ребенок не может добавлять правила');
    };
  }
  
  if (typeof window.addRule === 'function') {
    window.addRule = function() {
      console.log('⚠️ Ребенок не может добавлять правила');
    };
  }
  
  if (typeof window.deleteRule === 'function') {
    window.deleteRule = function() {
      console.log('⚠️ Ребенок не может удалять правила');
    };
  }
  
  console.log('✅ Права ребенка ограничены');
}

/**
 * Модальное окно редактирования аватара ребенка
 */
function openChildAvatarModal() {
  const modal = document.createElement('div');
  modal.id = 'child-avatar-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 10003;
    display: flex;
    align-items: center;
    justify-content: center;
  `;
  
  // Получаем текущий аватар
  const currentAvatar = appData.profile?.avatar || '';
  const hasAvatar = !!currentAvatar;
  
  modal.innerHTML = `
    <div style="
      background: white;
      border-radius: 24px;
      padding: 32px;
      max-width: 500px;
      width: 90%;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    ">
      <h2 style="
        margin: 0 0 24px 0;
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
      ">👤 Аватар</h2>
      
      <div style="
        display: flex;
        justify-content: center;
        margin-bottom: 32px;
      ">
        <div id="child-avatar-preview-large" style="
          width: 200px;
          height: 200px;
          border-radius: 50%;
          background: ${hasAvatar ? `url(${currentAvatar})` : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'};
          background-size: cover;
          background-position: center;
          border: 4px solid #e2e8f0;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 80px;
          overflow: hidden;
        ">${hasAvatar ? '' : '👤'}</div>
      </div>
      
      <div style="display: flex; gap: 12px; justify-content: center;">
        <button id="child-avatar-add-btn" style="
          flex: 1;
          padding: 14px;
          border: none;
          border-radius: 12px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        ">${hasAvatar ? 'Изменить' : 'Добавить'}</button>
        ${hasAvatar ? `
        <button id="child-avatar-remove-btn" style="
          flex: 1;
          padding: 14px;
          border: 2px solid #ef4444;
          border-radius: 12px;
          background: white;
          color: #ef4444;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        ">Удалить</button>
        ` : ''}
        <button id="child-avatar-cancel-btn" style="
          flex: 1;
          padding: 14px;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          background: white;
          color: #0f172a;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        ">Отмена</button>
      </div>
      
      <input type="file" id="child-avatar-file-input" accept="image/*" style="display: none;" />
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Обработчики событий
  const addBtn = document.getElementById('child-avatar-add-btn');
  const removeBtn = document.getElementById('child-avatar-remove-btn');
  const cancelBtn = document.getElementById('child-avatar-cancel-btn');
  const fileInput = document.getElementById('child-avatar-file-input');
  
  addBtn.addEventListener('click', () => {
    fileInput.click();
  });
  
  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      if (confirm('Удалить аватар?')) {
        if (!appData.profile) {
          appData.profile = {};
        }
        appData.profile.avatar = '';
        saveData();
        updateProfileAvatar();
        document.body.removeChild(modal);
      }
    });
  }
  
  cancelBtn.addEventListener('click', () => {
    document.body.removeChild(modal);
  });
  
  // Закрытие по клику вне модального окна
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  });
  
  // Обработчик выбора файла
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        openChildAvatarCropModal(event.target.result);
        document.body.removeChild(modal);
      };
      reader.readAsDataURL(file);
    }
  });
}

/**
 * Модальное окно кадрирования аватара ребенка
 */
function openChildAvatarCropModal(imageSrc) {
  const modal = document.createElement('div');
  modal.id = 'child-avatar-crop-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 10004;
    display: flex;
    align-items: center;
    justify-content: center;
  `;
  
  modal.innerHTML = `
    <div style="
      background: white;
      border-radius: 24px;
      padding: 24px;
      max-width: 90vw;
      max-height: 90vh;
      width: 500px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    ">
      <h3 style="
        margin: 0 0 20px 0;
        text-align: center;
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
      ">✂️ Подогнать фото</h3>
      
      <div style="
        position: relative;
        width: 300px;
        height: 300px;
        margin: 0 auto 20px;
        border-radius: 50%;
        overflow: hidden;
        border: 4px solid #e2e8f0;
        background: #f3f4f6;
      ">
        <div id="child-crop-image-wrapper" style="
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          cursor: move;
          user-select: none;
        ">
          <img id="child-crop-image" src="${imageSrc}" alt="Preview" style="
            display: block;
            max-width: none;
            user-select: none;
            pointer-events: none;
          " />
        </div>
      </div>
      
      <div style="
        text-align: center;
        margin-bottom: 20px;
        color: #64748b;
        font-size: 14px;
      ">
        💡 Перемещайте фото и увеличивайте/уменьшайте колесом мыши
      </div>
      
      <div style="display: flex; gap: 12px;">
        <button id="child-crop-cancel" style="
          flex: 1;
          padding: 14px;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          background: white;
          color: #0f172a;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        ">Отмена</button>
        <button id="child-crop-save" style="
          flex: 1;
          padding: 14px;
          border: none;
          border-radius: 12px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        ">Сохранить</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Инициализация кадрирования
  const imageWrapper = document.getElementById('child-crop-image-wrapper');
  const image = document.getElementById('child-crop-image');
  let scale = 1;
  let x = 0;
  let y = 0;
  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let startImageX = 0;
  let startImageY = 0;
  
  // Устанавливаем начальный размер изображения
  image.onload = () => {
    const containerSize = 300;
    const imgWidth = image.naturalWidth;
    const imgHeight = image.naturalHeight;
    const imgAspect = imgWidth / imgHeight;
    
    // Устанавливаем начальный размер так, чтобы изображение покрывало круг
    if (imgAspect > 1) {
      // Широкое изображение
      scale = containerSize / imgHeight * 1.5;
    } else {
      // Высокое изображение
      scale = containerSize / imgWidth * 1.5;
    }
    
    updateImageTransform();
  };
  
  function updateImageTransform() {
    imageWrapper.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px) scale(${scale})`;
  }
  
  // Перетаскивание
  imageWrapper.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    startImageX = x;
    startImageY = y;
    imageWrapper.style.cursor = 'grabbing';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (isDragging) {
      x = startImageX + (e.clientX - startX);
      y = startImageY + (e.clientY - startY);
      updateImageTransform();
    }
  });
  
  document.addEventListener('mouseup', () => {
    isDragging = false;
    imageWrapper.style.cursor = 'move';
  });
  
  // Масштабирование колесом мыши
  imageWrapper.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    scale = Math.max(0.5, Math.min(3, scale * delta));
    updateImageTransform();
  });
  
  // Касания для мобильных устройств
  let touchStartDistance = 0;
  let touchStartScale = 1;
  
  imageWrapper.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      // Одно касание - перемещение
      isDragging = true;
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      startImageX = x;
      startImageY = y;
    } else if (e.touches.length === 2) {
      // Два касания - масштабирование
      isDragging = false;
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      touchStartDistance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      touchStartScale = scale;
    }
  });
  
  imageWrapper.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (e.touches.length === 1 && isDragging) {
      x = startImageX + (e.touches[0].clientX - startX);
      y = startImageY + (e.touches[0].clientY - startY);
      updateImageTransform();
    } else if (e.touches.length === 2) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      scale = Math.max(0.5, Math.min(3, touchStartScale * (distance / touchStartDistance)));
      updateImageTransform();
    }
  });
  
  imageWrapper.addEventListener('touchend', () => {
    isDragging = false;
  });
  
  // Сохранение
  document.getElementById('child-crop-save').addEventListener('click', () => {
    // Создаем canvas для обрезки в круг
    const canvas = document.createElement('canvas');
    canvas.width = 300;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    
    // Рисуем круглую маску
    ctx.beginPath();
    ctx.arc(150, 150, 150, 0, 2 * Math.PI);
    ctx.clip();
    
    // Вычисляем позицию и размер изображения для отрисовки
    const imgWidth = image.naturalWidth;
    const imgHeight = image.naturalHeight;
    const imgAspect = imgWidth / imgHeight;
    const containerSize = 300;
    
    let drawWidth, drawHeight, drawX, drawY;
    
    if (imgAspect > 1) {
      // Широкое изображение
      drawHeight = containerSize / scale;
      drawWidth = drawHeight * imgAspect;
    } else {
      // Высокое изображение
      drawWidth = containerSize / scale;
      drawHeight = drawWidth / imgAspect;
    }
    
    drawX = 150 - (drawWidth / 2) - (x / scale);
    drawY = 150 - (drawHeight / 2) - (y / scale);
    
    // Рисуем изображение
    ctx.drawImage(image, drawX, drawY, drawWidth, drawHeight);
    
    // Получаем данные в base64
    const croppedImage = canvas.toDataURL('image/png');
    
    // Сохраняем
    if (!appData.profile) {
      appData.profile = {};
    }
    appData.profile.avatar = croppedImage;
    saveData();
    updateProfileAvatar();
    
    document.body.removeChild(modal);
  });
  
  // Отмена
  document.getElementById('child-crop-cancel').addEventListener('click', () => {
    document.body.removeChild(modal);
  });
  
  // Закрытие по клику вне модального окна
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  });
}

window.handleChildRoute = handleChildRoute;
window.showPinSetupModal = showPinSetupModal;
window.restrictChildPermissions = restrictChildPermissions;
window.openChildAvatarModal = openChildAvatarModal;




/**
 * Управление детьми
 * Создание, редактирование, генерация QR-кодов
 */

let childrenList = [];

/**
 * Инициализация управления детьми
 */
async function initChildren() {
  console.log('👶 Инициализация управления детьми...');
  await loadChildren();
  renderChildrenList();
}

/**
 * Загрузка списка детей
 */
async function loadChildren() {
  try {
    const children = await apiClient.getChildren();
    childrenList = children || [];
    console.log('✅ Дети загружены:', childrenList);
  } catch (error) {
    console.error('❌ Ошибка загрузки детей:', error);
    childrenList = [];
  }
}

/**
 * Отображение списка детей
 */
function renderChildrenList() {
  const container = document.getElementById('children-list');
  if (!container) {
    console.warn('⚠️ Контейнер детей не найден');
    return;
  }
  
  container.innerHTML = '';
  
  if (childrenList.length === 0) {
    container.innerHTML = `
      <div class="empty-children-state">
        <p style="color: #999; font-style: italic; text-align: center; padding: 20px;">
          Дети еще не добавлены
        </p>
        <button class="action-button" onclick="openAddChildModal()" style="margin: 0 auto; display: block;">
          + Добавить первого ребенка
        </button>
      </div>
    `;
    return;
  }
  
  childrenList.forEach(child => {
    const childCard = document.createElement('div');
    childCard.className = 'child-card';
    childCard.style.cssText = `
      display: flex;
      align-items: center;
      padding: 16px;
      margin-bottom: 12px;
      background: var(--surface);
      border-radius: 12px;
      box-shadow: var(--shadow-sm);
      gap: 16px;
    `;
    
    // Аватар
    const avatar = document.createElement('div');
    avatar.className = 'child-avatar';
    avatar.style.cssText = `
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: ${child.avatar || getDefaultAvatar(child.gender)};
      background-size: cover;
      background-position: center;
      border: 2px solid var(--border-color);
      flex-shrink: 0;
    `;
    
    // Информация о ребенке
    const info = document.createElement('div');
    info.style.cssText = 'flex: 1;';
    info.innerHTML = `
      <h3 style="margin: 0 0 4px 0; font-size: 18px; color: var(--text-primary);">${escapeHtml(child.name)}</h3>
      <p style="margin: 0; font-size: 14px; color: var(--text-secondary);">
        ${getGenderLabel(child.gender)}
      </p>
    `;
    
    // Кнопки действий
    const actions = document.createElement('div');
    actions.style.cssText = 'display: flex; gap: 8px;';
    
    const qrBtn = document.createElement('button');
    qrBtn.textContent = '📱 QR';
    qrBtn.className = 'btn-secondary';
    qrBtn.style.cssText = 'padding: 8px 16px; font-size: 14px;';
    qrBtn.onclick = () => generateChildQR(child.id);
    
    actions.appendChild(qrBtn);
    
    childCard.appendChild(avatar);
    childCard.appendChild(info);
    childCard.appendChild(actions);
    container.appendChild(childCard);
  });
  
  // Кнопка добавления
  const addBtn = document.createElement('button');
  addBtn.textContent = '+ Добавить ребенка';
  addBtn.className = 'action-button';
  addBtn.style.cssText = 'margin-top: 16px; width: 100%;';
  addBtn.onclick = openAddChildModal;
  container.appendChild(addBtn);
}

/**
 * Получение аватара по умолчанию по полу
 */
function getDefaultAvatar(gender) {
  if (gender === 'girl') {
    return 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)';
  } else if (gender === 'boy') {
    return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  }
  return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
}

/**
 * Получение текста для пола
 */
function getGenderLabel(gender) {
  if (gender === 'girl') return 'Девочка';
  if (gender === 'boy') return 'Мальчик';
  return 'Не указан';
}

/**
 * Экранирование HTML
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Открытие модального окна добавления ребенка
 */
function openAddChildModal() {
  const modal = document.getElementById('add-child-modal');
  if (modal) {
    modal.style.display = 'flex';
    // Сброс формы
    const form = document.getElementById('add-child-form');
    if (form) {
      form.reset();
      // Сброс аватара
      const avatarPreview = document.getElementById('child-avatar-preview');
      if (avatarPreview) {
        avatarPreview.style.background = getDefaultAvatar('none');
      }
    }
  }
}

/**
 * Закрытие модального окна добавления ребенка
 */
function closeAddChildModal() {
  const modal = document.getElementById('add-child-modal');
  if (modal) {
    modal.style.display = 'none';
  }
}

/**
 * Обработка выбора пола
 */
function onGenderChange() {
  const genderSelect = document.getElementById('child-gender');
  const avatarPreview = document.getElementById('child-avatar-preview');
  
  if (genderSelect && avatarPreview) {
    const gender = genderSelect.value;
    avatarPreview.style.background = getDefaultAvatar(gender);
  }
}

/**
 * Обработка загрузки аватара
 */
function onAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Проверка типа файла
  if (!file.type.startsWith('image/')) {
    alert('Пожалуйста, выберите изображение');
    return;
  }
  
  // Проверка размера (макс 2MB)
  if (file.size > 2 * 1024 * 1024) {
    alert('Размер изображения не должен превышать 2MB');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    const avatarPreview = document.getElementById('child-avatar-preview');
    if (avatarPreview) {
      avatarPreview.style.backgroundImage = `url(${e.target.result})`;
      avatarPreview.style.backgroundSize = 'cover';
      avatarPreview.style.backgroundPosition = 'center';
    }
  };
  reader.readAsDataURL(file);
}

/**
 * Создание ребенка
 */
async function createChild(event) {
  event.preventDefault();
  
  const form = event.target;
  const name = form.querySelector('#child-name').value.trim();
  const gender = form.querySelector('#child-gender').value;
  const age = form.querySelector('#child-age').value;
  
  if (!name) {
    alert('Пожалуйста, введите имя ребенка');
    return;
  }
  
  // Получаем аватар (если загружен)
  let avatar = null;
  const avatarInput = form.querySelector('#child-avatar-input');
  if (avatarInput && avatarInput.files[0]) {
    const file = avatarInput.files[0];
    const reader = new FileReader();
    avatar = await new Promise((resolve) => {
      reader.onload = (e) => resolve(e.target.result);
      reader.readAsDataURL(file);
    });
  }
  
  try {
    const childData = {
      name: name,
      gender: gender,
      avatar: avatar
    };
    
    console.log('📤 Создание ребенка:', childData);
    const child = await apiClient.createChild(childData);
    console.log('✅ Ребенок создан:', child);
    console.log('🔍 ID ребенка:', child?.id);
    
    if (!child) {
      throw new Error('Ребенок не был создан - сервер не вернул данные');
    }
    
    if (!child.id) {
      console.error('❌ Ребенок создан, но ID отсутствует:', child);
      throw new Error('Ребенок создан, но ID не получен. Попробуйте обновить страницу.');
    }
    
    // Обновляем список
    await loadChildren();
    renderChildrenList();
    
    // Закрываем модальное окно
    closeAddChildModal();
    
    // Показываем сообщение об успехе
    // Обновляем список детей в модальном окне
    if (typeof window.loadChildrenForModal === 'function') {
      await window.loadChildrenForModal();
    }
    
    // Переключаемся на нового ребенка
    if (typeof window.switchToChild === 'function' && child && child.id) {
      await window.switchToChild(child.id);
    }
    
    alert('Ребенок успешно добавлен! Теперь вы можете сгенерировать QR-код для входа, нажав кнопку "📱 QR" рядом с именем ребенка.');
    
  } catch (error) {
    console.error('❌ Ошибка создания ребенка:', error);
    const errorMessage = error.message || 'Неизвестная ошибка';
    alert(`Ошибка создания ребенка: ${errorMessage}`);
  }
}

/**
 * Генерация QR-кода для ребенка
 */
async function generateChildQR(childId) {
  try {
    console.log('📱 Генерация QR-кода для ребенка:', childId);
    
    if (!childId) {
      throw new Error('ID ребенка не указан');
    }
    
    const access = await apiClient.generateChildAccess(childId);
    console.log('✅ QR-код сгенерирован:', access);
    
    if (!access || !access.qr_code) {
      throw new Error('QR-код не был сгенерирован сервером');
    }
    
    // Показываем модальное окно с QR-кодом
    showQRModal(access);
  } catch (error) {
    console.error('❌ Ошибка генерации QR-кода:', error);
    const errorMessage = error.message || 'Неизвестная ошибка';
    alert(`Ошибка генерации QR-кода: ${errorMessage}`);
  }
}

/**
 * Показ модального окна с QR-кодом
 */
function showQRModal(access) {
  let modal = document.getElementById('child-qr-modal');
  if (!modal) {
    // Создаем модальное окно, если его нет
    createQRModal();
    modal = document.getElementById('child-qr-modal');
  }
  
  if (!modal) {
    console.error('❌ Не удалось создать модальное окно для QR-кода');
    return;
  }
  
  const qrImage = document.getElementById('child-qr-image');
  const qrPin = document.getElementById('child-qr-pin');
  const qrExpires = document.getElementById('child-qr-expires');
  
  if (qrImage && access.qr_code) {
    qrImage.src = access.qr_code;
    qrImage.style.display = 'block';
    qrImage.alt = 'QR-код для входа ребенка';
  } else if (qrImage) {
    qrImage.style.display = 'none';
  }
  
  if (qrPin) {
    if (access.pin) {
      qrPin.textContent = `PIN: ${access.pin}`;
      qrPin.style.display = 'block';
    } else {
      qrPin.style.display = 'none';
    }
  }
  
  if (qrExpires) {
    if (access.expires_at) {
      const expiresDate = new Date(access.expires_at);
      qrExpires.textContent = `Действителен до: ${expiresDate.toLocaleDateString('ru-RU')}`;
      qrExpires.style.display = 'block';
    } else {
      qrExpires.style.display = 'none';
    }
  }
  
  // Показываем модальное окно
  modal.style.display = 'flex';
  console.log('✅ Модальное окно с QR-кодом открыто');
}

/**
 * Создание модального окна для QR-кода
 */
function createQRModal() {
  const modal = document.createElement('div');
  modal.id = 'child-qr-modal';
  modal.className = 'modal';
  modal.style.cssText = `
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 10001;
    align-items: center;
    justify-content: center;
  `;
  
  modal.innerHTML = `
    <div class="modal-content" style="max-width: 400px; width: 90%; padding: 24px; background: white; border-radius: 16px;">
      <h2 style="margin: 0 0 20px 0; text-align: center;">📱 QR-код для входа</h2>
      <div style="text-align: center; margin-bottom: 20px;">
        <img id="child-qr-image" src="" alt="QR Code" style="max-width: 100%; border: 2px solid #e2e8f0; border-radius: 8px; display: none;" />
      </div>
      <p id="child-qr-pin" style="text-align: center; font-size: 18px; font-weight: bold; color: #667eea; margin: 16px 0; display: none;"></p>
      <p id="child-qr-expires" style="text-align: center; font-size: 14px; color: #64748b; margin: 8px 0; display: none;"></p>
      <button class="action-button" onclick="closeQRModal()" style="width: 100%; margin-top: 20px;">Закрыть</button>
    </div>
  `;
  
  document.body.appendChild(modal);
}

/**
 * Закрытие модального окна QR-кода
 */
function closeQRModal() {
  const modal = document.getElementById('child-qr-modal');
  if (modal) {
    modal.style.display = 'none';
  }
}

// Экспорт функций для глобального использования
window.openAddChildModal = openAddChildModal;
window.closeAddChildModal = closeAddChildModal;
window.onGenderChange = onGenderChange;
window.onAvatarUpload = onAvatarUpload;
window.createChild = createChild;
window.generateChildQR = generateChildQR;
window.closeQRModal = closeQRModal;
window.getDefaultAvatar = getDefaultAvatar;
window.getGenderLabel = getGenderLabel;
window.escapeHtml = escapeHtml;


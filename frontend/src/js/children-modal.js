/**
 * Модальное окно управления детьми
 * Отображается при нажатии на аватар родителя
 */

let currentChildren = [];
let currentChildId = null; // ID выбранного ребенка

/**
 * Инициализация модального окна управления детьми
 */
async function initChildrenModal() {
  console.log('👶 Инициализация модального окна управления детьми...');
  
  // Создаем модальное окно, если его нет
  if (!document.getElementById('children-management-modal')) {
    createChildrenModal();
  }
  
  // Загружаем список детей
  await loadChildrenForModal();
}

/**
 * Создание модального окна управления детьми
 */
function createChildrenModal() {
  const modal = document.createElement('div');
  modal.id = 'children-management-modal';
  modal.className = 'modal';
  modal.style.cssText = `
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 10002;
    align-items: center;
    justify-content: center;
  `;
  
  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: var(--surface);
    border-radius: 24px;
    padding: 32px;
    max-width: 600px;
    width: 92%;
    max-height: 85vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
    position: relative;
  `;
  
  modalContent.innerHTML = `
    <div style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 28px;
      padding-bottom: 20px;
      border-bottom: 2px solid var(--border-light);
    ">
      <h2 style="
        margin: 0;
        color: var(--text-primary);
        font-size: 24px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
      ">
        <span style="font-size: 28px;">👶</span>
        <span>Мои дети</span>
      </h2>
      <button onclick="closeChildrenModal()" style="
        background: var(--surface-hover);
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: var(--text-secondary);
        padding: 0;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
      " onmouseover="this.style.background='var(--border-color)'; this.style.color='var(--text-primary)'" onmouseout="this.style.background='var(--surface-hover)'; this.style.color='var(--text-secondary)'">×</button>
    </div>
    <div id="children-modal-list" style="margin-bottom: 24px; min-height: 200px;">
      <!-- Список детей будет загружен динамически -->
    </div>
    <button onclick="openAddChildModal(); closeChildrenModal();" class="action-button" style="
      width: 100%;
      padding: 16px;
      font-size: 16px;
      font-weight: 600;
      border-radius: 12px;
      background: linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #f0abfc 100%);
      color: white;
      border: none;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(167, 139, 250, 0.4)'; this.style.background='linear-gradient(135deg, #8b5cf6 0%, #a78bfa 50%, #c084fc 100%)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(167, 139, 250, 0.3)'; this.style.background='linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #f0abfc 100%)'">
      <span style="font-size: 20px;">+</span>
      <span>Добавить ребенка</span>
    </button>
  `;
  
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Сохраняем ссылку на modalContent для изменения содержимого
  window.childrenModalContent = modalContent;
  window.childrenModal = modal;
  
  // Закрытие по клику вне модального окна
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeChildrenModal();
    }
  });
  
  // Закрытие по Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display === 'flex') {
      closeChildrenModal();
    }
  });
}

/**
 * Загрузка списка детей для модального окна
 */
async function loadChildrenForModal() {
  try {
    console.log('📥 Загрузка детей для модального окна...');
    currentChildren = await apiClient.getChildren();
    console.log('✅ Дети загружены:', currentChildren);
    renderChildrenModalList();
    
    // Если детей нет, показываем сообщение
    if (currentChildren.length === 0) {
      const list = document.getElementById('children-modal-list');
      if (list) {
        list.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 20px;">Дети еще не добавлены</p>';
      }
    }
  } catch (error) {
    console.error('❌ Ошибка загрузки детей:', error);
    const list = document.getElementById('children-modal-list');
    if (list) {
      list.innerHTML = '<p style="text-align: center; color: #e74c3c; padding: 20px;">Ошибка загрузки детей</p>';
    }
  }
}

/**
 * Отображение списка детей в модальном окне
 */
function renderChildrenModalList() {
  const list = document.getElementById('children-modal-list');
  if (!list) return;
  
  list.innerHTML = '';
  
  if (currentChildren.length === 0) {
    list.innerHTML = `
      <div style="
        text-align: center;
        padding: 60px 20px;
        color: var(--text-muted);
      ">
        <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;">👶</div>
        <p style="
          font-size: 16px;
          font-weight: 500;
          margin: 0;
          color: var(--text-secondary);
        ">Дети еще не добавлены</p>
        <p style="
          font-size: 14px;
          margin: 8px 0 0 0;
          color: var(--text-muted);
        ">Нажмите кнопку ниже, чтобы добавить первого ребенка</p>
      </div>
    `;
    return;
  }
  
  currentChildren.forEach((child) => {
    const childItem = document.createElement('div');
    const isSelected = currentChildId === child.id;
    childItem.style.cssText = `
      display: flex;
      flex-direction: column;
      padding: 16px;
      margin-bottom: 12px;
      background: ${isSelected ? '#f8fafc' : '#ffffff'};
      border: 2px solid ${isSelected ? '#a78bfa' : '#e2e8f0'};
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: ${isSelected ? '0 4px 12px rgba(167, 139, 250, 0.2)' : '0 1px 3px rgba(0, 0, 0, 0.1)'};
      position: relative;
      overflow: visible;
    `;
    
    childItem.onmouseenter = function() {
      if (!isSelected) {
        this.style.borderColor = '#c4b5fd';
        this.style.boxShadow = '0 4px 12px rgba(167, 139, 250, 0.15)';
        this.style.transform = 'translateY(-2px)';
        this.style.background = '#f8fafc';
      }
    };
    
    childItem.onmouseleave = function() {
      if (!isSelected) {
        this.style.borderColor = '#e2e8f0';
        this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
        this.style.transform = 'translateY(0)';
        this.style.background = '#ffffff';
      }
    };
    
    // Верхняя часть: аватар и имя
    const topSection = document.createElement('div');
    topSection.style.cssText = `
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 16px;
      width: 100%;
      flex-shrink: 0;
      position: relative;
      z-index: 1;
    `;
    
    // Аватар
    const avatar = document.createElement('div');
    avatar.style.cssText = `
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: ${child.avatar || getDefaultAvatar(child.gender)};
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      border: 2px solid ${isSelected ? '#a78bfa' : '#f1f5f9'};
      box-shadow: var(--shadow-sm);
    `;
    if (!child.avatar) {
      avatar.textContent = child.gender === 'girl' ? '👧' : child.gender === 'boy' ? '👦' : '👤';
    }
    
    // Имя
    const nameDiv = document.createElement('div');
    nameDiv.style.cssText = `
      flex: 1;
      font-weight: 700;
      font-size: 20px;
      color: var(--text-primary);
      line-height: 1.4;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
    `;
    nameDiv.textContent = escapeHtml(child.name);
    
    topSection.appendChild(avatar);
    topSection.appendChild(nameDiv);
    
    // Кнопки действий (внизу)
    const actions = document.createElement('div');
    actions.style.cssText = `
      display: flex;
      gap: 10px;
      align-items: stretch;
      width: 100%;
      margin-top: 0;
      flex-shrink: 0;
      position: relative;
      z-index: 1;
    `;
    
    // Кнопка QR-кода
    const qrBtn = document.createElement('button');
    qrBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="5" height="5" fill="currentColor"/><rect x="16" y="3" width="5" height="5" fill="currentColor"/><rect x="3" y="16" width="5" height="5" fill="currentColor"/><rect x="7" y="7" width="3" height="3" fill="currentColor"/><rect x="14" y="7" width="3" height="3" fill="currentColor"/><rect x="7" y="14" width="3" height="3" fill="currentColor"/><rect x="14" y="11" width="3" height="1" fill="currentColor"/><rect x="14" y="14" width="3" height="3" fill="currentColor"/><rect x="18" y="14" width="3" height="1" fill="currentColor"/><rect x="18" y="17" width="3" height="3" fill="currentColor"/></svg>';
    qrBtn.title = 'QR-код для входа';
    qrBtn.style.cssText = `
      flex: 1;
      padding: 12px;
      border-radius: 12px;
      background: #f8f9fa;
      color: #64748b;
      border: 1px solid #e9ecef;
      font-size: 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      min-height: 44px;
    `;
    qrBtn.onmouseenter = function() {
      this.style.transform = 'translateY(-1px)';
      this.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.08)';
      this.style.background = '#f1f3f5';
      this.style.borderColor = '#dee2e6';
    };
    qrBtn.onmouseleave = function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
      this.style.background = '#f8f9fa';
      this.style.borderColor = '#e9ecef';
    };
    qrBtn.onclick = async (e) => {
      e.stopPropagation();
      // Меняем содержимое текущего модального окна на QR-код
      await showQRCodeInModal(child.id);
    };
    
    // Кнопка настроек
    const settingsBtn = document.createElement('button');
    settingsBtn.textContent = '⚙️';
    settingsBtn.title = 'Настройки';
    settingsBtn.style.cssText = `
      flex: 1;
      padding: 12px;
      border-radius: 12px;
      background: #f8f9fa;
      color: #64748b;
      border: 1px solid #e9ecef;
      font-size: 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      min-height: 44px;
    `;
    settingsBtn.onmouseenter = function() {
      this.style.transform = 'translateY(-1px)';
      this.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.08)';
      this.style.background = '#f1f3f5';
      this.style.borderColor = '#dee2e6';
    };
    settingsBtn.onmouseleave = function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
      this.style.background = '#f8f9fa';
      this.style.borderColor = '#e9ecef';
    };
    settingsBtn.onclick = (e) => {
      e.stopPropagation();
      openChildSettings(child.id);
    };
    
    // Кнопка удаления
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '🗑️';
    deleteBtn.title = 'Удалить';
    deleteBtn.style.cssText = `
      flex: 1;
      padding: 12px;
      border-radius: 12px;
      background: #f8f9fa;
      color: #64748b;
      border: 1px solid #e9ecef;
      font-size: 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      min-height: 44px;
    `;
    deleteBtn.onmouseenter = function() {
      this.style.transform = 'translateY(-1px)';
      this.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.08)';
      this.style.background = '#f1f3f5';
      this.style.borderColor = '#dee2e6';
    };
    deleteBtn.onmouseleave = function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
      this.style.background = '#f8f9fa';
      this.style.borderColor = '#e9ecef';
    };
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      deleteChild(child.id, child.name);
    };
    
    actions.appendChild(qrBtn);
    actions.appendChild(settingsBtn);
    actions.appendChild(deleteBtn);
    
    // Подпись под карточкой
    const instruction = document.createElement('div');
    instruction.style.cssText = `
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid #f1f5f9;
      font-size: 13px;
      color: #64748b;
      text-align: center;
      line-height: 1.4;
    `;
    instruction.textContent = `Для регистрации ребенка "${escapeHtml(child.name)}" отсканируй QR-код`;
    
    // Клик по элементу - переключение на ребенка
    childItem.onclick = () => {
      switchToChild(child.id);
    };
    
    childItem.appendChild(topSection);
    childItem.appendChild(actions);
    childItem.appendChild(instruction);
    list.appendChild(childItem);
  });
}

/**
 * Переключение на ребенка
 */
async function switchToChild(childId) {
  try {
    console.log('🔄 Переключение на ребенка:', childId);
    
    // Сохраняем выбранного ребенка
    currentChildId = childId;
    
    // Находим данные ребенка
    const child = currentChildren.find(c => c.id === childId);
    if (child) {
      // Обновляем имя в header
      updateHeaderChildName(child.name);
    }
    
    // Обновляем отображение
    renderChildrenModalList();
    
    // Закрываем модальное окно
    closeChildrenModal();
    
    // TODO: Загрузить настройки и данные выбранного ребенка
    console.log(`✅ Выбран ребенок: ${child ? child.name : childId}`);
    
  } catch (error) {
    console.error('❌ Ошибка переключения на ребенка:', error);
    alert('Ошибка переключения на ребенка');
  }
}

/**
 * Обновление имени ребенка в header
 */
function updateHeaderChildName(childName) {
  const headerChildName = document.getElementById('header-child-name');
  if (headerChildName) {
    headerChildName.textContent = childName || '';
  }
}

/**
 * Открытие настроек ребенка
 */
function openChildSettings(childId) {
  const child = currentChildren.find(c => c.id === childId);
  if (!child) {
    console.error('❌ Ребенок не найден:', childId);
    return;
  }
  
  // Создаем модальное окно настроек, если его нет
  let settingsModal = document.getElementById('child-settings-modal');
  if (!settingsModal) {
    createChildSettingsModal();
    settingsModal = document.getElementById('child-settings-modal');
  }
  
  if (!settingsModal) {
    console.error('❌ Не удалось создать модальное окно настроек');
    return;
  }
  
  // Заполняем форму данными ребенка
  const nameInput = document.getElementById('child-settings-name');
  const genderSelect = document.getElementById('child-settings-gender');
  const ageInput = document.getElementById('child-settings-age');
  const avatarPreview = document.getElementById('child-settings-avatar-preview');
  const avatarInput = document.getElementById('child-settings-avatar-input');
  
  if (nameInput) nameInput.value = child.name || '';
  if (genderSelect) genderSelect.value = child.gender || 'none';
  if (ageInput) ageInput.value = child.age || '';
  
  // Устанавливаем аватар
  if (avatarPreview) {
    if (child.avatar) {
      avatarPreview.style.backgroundImage = `url(${child.avatar})`;
      avatarPreview.style.backgroundSize = 'cover';
      avatarPreview.style.backgroundPosition = 'center';
    } else {
      avatarPreview.style.backgroundImage = 'none';
      avatarPreview.style.background = getDefaultAvatar(child.gender || 'none');
    }
  }
  
  // Сохраняем ID ребенка в data-атрибуте формы
  const form = document.getElementById('child-settings-form');
  if (form) {
    form.dataset.childId = childId;
  }
  
  // Показываем модальное окно
  settingsModal.style.display = 'flex';
  console.log('✅ Модальное окно настроек открыто для ребенка:', child.name);
}

/**
 * Создание модального окна настроек ребенка
 */
function createChildSettingsModal() {
  const modal = document.createElement('div');
  modal.id = 'child-settings-modal';
  modal.className = 'modal';
  modal.style.cssText = `
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 10003;
    align-items: center;
    justify-content: center;
  `;
  
  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: var(--surface);
    border-radius: 16px;
    padding: 24px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
  `;
  
  modalContent.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 style="margin: 0; color: var(--text-primary);">⚙️ Настройки ребенка</h2>
      <button onclick="closeChildSettingsModal()" style="
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: var(--text-secondary);
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
      ">×</button>
    </div>
    <form id="child-settings-form" onsubmit="saveChildSettings(event)">
      <!-- Аватар -->
      <div style="text-align: center; margin-bottom: 20px;">
        <div id="child-settings-avatar-preview" style="
          width: 100px;
          height: 100px;
          border-radius: 50%;
          margin: 0 auto 12px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 48px;
          border: 3px solid var(--border-color);
          transition: all 0.3s ease;
        " onclick="document.getElementById('child-settings-avatar-input').click()">
        </div>
        <input type="file" id="child-settings-avatar-input" accept="image/*" style="display: none;" onchange="onSettingsAvatarUpload(event)">
        <p style="font-size: 12px; color: var(--text-muted); margin: 0;">Нажмите для загрузки фото</p>
      </div>
      
      <!-- Имя -->
      <div style="margin-bottom: 16px;">
        <label for="child-settings-name" style="
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: var(--text-primary);
        ">Имя</label>
        <input 
          type="text" 
          id="child-settings-name" 
          required 
          placeholder="Введите имя"
          style="
            width: 100%;
            padding: 12px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 16px;
            color: var(--input-text);
            background: var(--input-bg);
            box-sizing: border-box;
          "
        />
      </div>
      
      <!-- Пол -->
      <div style="margin-bottom: 16px;">
        <label for="child-settings-gender" style="
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: var(--text-primary);
        ">Пол</label>
        <select 
          id="child-settings-gender" 
          onchange="onSettingsGenderChange()"
          style="
            width: 100%;
            padding: 12px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 16px;
            color: var(--input-text);
            background: var(--input-bg);
            box-sizing: border-box;
            appearance: none;
          "
        >
          <option value="none">Не указан</option>
          <option value="boy">Мальчик</option>
          <option value="girl">Девочка</option>
        </select>
      </div>
      
      <!-- Возраст -->
      <div style="margin-bottom: 24px;">
        <label for="child-settings-age" style="
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: var(--text-primary);
        ">Возраст</label>
        <input 
          type="number" 
          id="child-settings-age" 
          min="0" 
          max="18" 
          placeholder="Введите возраст"
          style="
            width: 100%;
            padding: 12px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 16px;
            color: var(--input-text);
            background: var(--input-bg);
            box-sizing: border-box;
          "
        />
      </div>
      
      <!-- Кнопки -->
      <div style="display: flex; gap: 12px;">
        <button 
          type="button"
          onclick="closeChildSettingsModal()" 
          style="
            flex: 1;
            padding: 12px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            background: var(--surface);
            color: var(--text-primary);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
          "
        >
          Отмена
        </button>
        <button 
          type="submit"
          class="action-button" 
          style="flex: 1;"
        >
          Сохранить
        </button>
      </div>
    </form>
  `;
  
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Закрытие по клику вне модального окна
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeChildSettingsModal();
    }
  });
  
  // Закрытие по Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display === 'flex') {
      closeChildSettingsModal();
    }
  });
}

/**
 * Закрытие модального окна настроек
 */
function closeChildSettingsModal() {
  const modal = document.getElementById('child-settings-modal');
  if (modal) {
    modal.style.display = 'none';
    // Сбрасываем форму
    const form = document.getElementById('child-settings-form');
    if (form) {
      form.reset();
      delete form.dataset.childId;
    }
  }
}

/**
 * Сохранение настроек ребенка
 */
async function saveChildSettings(event) {
  event.preventDefault();
  
  const form = document.getElementById('child-settings-form');
  if (!form) {
    console.error('❌ Форма настроек не найдена');
    return;
  }
  
  const childId = form.dataset.childId;
  if (!childId) {
    console.error('❌ ID ребенка не найден');
    return;
  }
  
  const nameInput = document.getElementById('child-settings-name');
  const genderSelect = document.getElementById('child-settings-gender');
  const ageInput = document.getElementById('child-settings-age');
  
  if (!nameInput || !genderSelect) {
    console.error('❌ Поля формы не найдены');
    return;
  }
  
  const name = nameInput.value.trim();
  if (!name) {
    alert('Введите имя ребенка');
    return;
  }
  
  try {
    console.log('💾 Сохранение настроек ребенка:', childId);
    
    // Подготавливаем данные для обновления
    const updateData = {
      name: name,
      gender: genderSelect.value
    };
    
    // Возраст пока не сохраняем, так как поле age отсутствует в модели Child
    // TODO: Добавить поле age в модель Child, если потребуется
    // if (ageInput && ageInput.value) {
    //   const age = parseInt(ageInput.value);
    //   if (!isNaN(age) && age >= 0 && age <= 18) {
    //     updateData.age = age;
    //   }
    // }
    
    // Обновляем ребенка через API
    const updatedChild = await apiClient.updateChild(childId, updateData);
    console.log('✅ Настройки сохранены:', updatedChild);
    
    // Обновляем список детей
    await loadChildrenForModal();
    
    // Обновляем имя в header, если это текущий выбранный ребенок
    if (currentChildId === childId && updatedChild.name) {
      updateHeaderChildName(updatedChild.name);
    }
    
    // Закрываем модальное окно
    closeChildSettingsModal();
    
    alert('Настройки успешно сохранены!');
  } catch (error) {
    console.error('❌ Ошибка сохранения настроек:', error);
    alert(`Ошибка сохранения настроек: ${error.message || 'Неизвестная ошибка'}`);
  }
}

/**
 * Обработка изменения пола в настройках
 */
function onSettingsGenderChange() {
  const genderSelect = document.getElementById('child-settings-gender');
  const avatarPreview = document.getElementById('child-settings-avatar-preview');
  
  if (genderSelect && avatarPreview) {
    const gender = genderSelect.value;
    // Обновляем аватар только если нет загруженного изображения
    if (!avatarPreview.style.backgroundImage || avatarPreview.style.backgroundImage === 'none') {
      avatarPreview.style.background = getDefaultAvatar(gender);
      avatarPreview.style.backgroundImage = 'none';
    }
  }
}

/**
 * Обработка загрузки аватара в настройках
 */
function onSettingsAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Проверяем тип файла
  if (!file.type.startsWith('image/')) {
    alert('Пожалуйста, выберите изображение');
    return;
  }
  
  // Проверяем размер файла (макс 5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('Размер файла не должен превышать 5MB');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    const avatarPreview = document.getElementById('child-settings-avatar-preview');
    if (avatarPreview) {
      avatarPreview.style.backgroundImage = `url(${e.target.result})`;
      avatarPreview.style.backgroundSize = 'cover';
      avatarPreview.style.backgroundPosition = 'center';
    }
  };
  reader.readAsDataURL(file);
  
  // TODO: Загрузка аватара на сервер будет реализована позже
  console.log('📸 Аватар выбран, но загрузка на сервер еще не реализована');
}

/**
 * Удаление ребенка
 */
async function deleteChild(childId, childName) {
  if (!confirm(`Вы уверены, что хотите удалить ребенка "${childName}"?\n\nЭто действие нельзя отменить. Все данные ребенка будут удалены.`)) {
    return;
  }
  
  try {
    console.log('🗑️ Удаление ребенка:', childId);
    
    await apiClient.deleteChild(childId);
    console.log('✅ Ребенок удален');
    
    // Обновляем список
    await loadChildrenForModal();
    
    // Если удалили текущего ребенка, сбрасываем выбор
    if (currentChildId === childId) {
      currentChildId = null;
    }
    
    alert('Ребенок успешно удален');
  } catch (error) {
    console.error('❌ Ошибка удаления ребенка:', error);
    alert(`Ошибка удаления ребенка: ${error.message || 'Неизвестная ошибка'}`);
  }
}

/**
 * Открытие модального окна управления детьми
 */
function openChildrenModal() {
  const modal = document.getElementById('children-management-modal');
  if (!modal) {
    initChildrenModal();
    return;
  }
  
  // Загружаем актуальный список детей
  loadChildrenForModal();
  
  modal.style.display = 'flex';
  console.log('✅ Модальное окно управления детьми открыто');
}

/**
 * Закрытие модального окна управления детьми
 */
function closeChildrenModal() {
  const modal = document.getElementById('children-management-modal');
  if (modal) {
    modal.style.display = 'none';
  }
}

/**
 * Получение аватара по умолчанию по полу
 * Использует функцию из children.js, если доступна
 */
function getDefaultAvatar(gender) {
  if (typeof window.getDefaultAvatar === 'function') {
    return window.getDefaultAvatar(gender);
  }
  // Fallback
  if (gender === 'girl') {
    return 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)';
  } else if (gender === 'boy') {
    return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  }
  return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
}

/**
 * Получение текста для пола
 * Использует функцию из children.js, если доступна
 */
function getGenderLabel(gender) {
  if (typeof window.getGenderLabel === 'function') {
    return window.getGenderLabel(gender);
  }
  // Fallback
  if (gender === 'girl') return 'Девочка';
  if (gender === 'boy') return 'Мальчик';
  return 'Не указан';
}

/**
 * Показ QR-кода в текущем модальном окне
 */
async function showQRCodeInModal(childId) {
  try {
    console.log('📱 Генерация QR-кода для ребенка:', childId);
    
    if (!childId) {
      throw new Error('ID ребенка не указан');
    }
    
    // Загружаем children.js если нужно
    if (typeof window.apiClient === 'undefined' || typeof window.apiClient.generateChildAccess === 'undefined') {
      const script = document.createElement('script');
      script.src = '/src/js/children.js';
      document.body.appendChild(script);
      await new Promise((resolve) => {
        script.onload = resolve;
      });
    }
    
    const access = await window.apiClient.generateChildAccess(childId);
    console.log('✅ QR-код сгенерирован:', access);
    
    if (!access || !access.qr_code) {
      throw new Error('QR-код не был сгенерирован сервером');
    }
    
    // Меняем содержимое модального окна
    const modalContent = window.childrenModalContent;
    if (!modalContent) {
      throw new Error('Модальное окно не найдено');
    }
    
    modalContent.innerHTML = `
      <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
        padding-bottom: 20px;
        border-bottom: 2px solid var(--border-light);
      ">
        <h2 style="
          margin: 0;
          color: var(--text-primary);
          font-size: 24px;
          font-weight: 700;
        ">
          QR-код для входа ребенка
        </h2>
        <button onclick="closeChildrenModal(); setTimeout(() => openChildrenModal(), 100);" style="
          background: var(--surface-hover);
          border: none;
          font-size: 20px;
          cursor: pointer;
          color: var(--text-secondary);
          padding: 0;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        " onmouseover="this.style.background='var(--border-color)'; this.style.color='var(--text-primary)'" onmouseout="this.style.background='var(--surface-hover)'; this.style.color='var(--text-secondary)'">×</button>
      </div>
      <div style="text-align: center; margin-bottom: 24px;">
        <img src="${access.qr_code}" alt="QR Code" style="max-width: 100%; border: 2px solid #e2e8f0; border-radius: 12px; padding: 16px; background: white;" />
      </div>
      <div style="
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 24px;
        text-align: center;
      ">
        <p style="
          margin: 0;
          font-size: 16px;
          color: #0f172a;
          font-weight: 500;
          line-height: 1.5;
        ">Наведите камеру телефона ребенка и отсканируйте</p>
      </div>
      <button onclick="closeChildrenModal(); setTimeout(() => openChildrenModal(), 100);" class="action-button" style="
        width: 100%;
        padding: 16px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 12px;
        background: linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #f0abfc 100%);
        color: white;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
      " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(167, 139, 250, 0.4)'; this.style.background='linear-gradient(135deg, #8b5cf6 0%, #a78bfa 50%, #c084fc 100%)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(167, 139, 250, 0.3)'; this.style.background='linear-gradient(135deg, #a78bfa 0%, #c084fc 50%, #f0abfc 100%)'">
        Назад к списку детей
      </button>
    `;
    
    console.log('✅ QR-код отображен в модальном окне');
  } catch (error) {
    console.error('❌ Ошибка генерации QR-кода:', error);
    const errorMessage = error.message || 'Неизвестная ошибка';
    alert(`Ошибка генерации QR-кода: ${errorMessage}`);
  }
}

/**
 * Экранирование HTML
 * Использует функцию из children.js, если доступна
 */
function escapeHtml(text) {
  if (typeof window.escapeHtml === 'function') {
    return window.escapeHtml(text);
  }
  // Fallback
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Экспорт функций
window.openChildrenModal = openChildrenModal;
window.closeChildrenModal = closeChildrenModal;
window.initChildrenModal = initChildrenModal;
window.switchToChild = switchToChild;
window.deleteChild = deleteChild;
window.updateHeaderChildName = updateHeaderChildName;
window.openChildSettings = openChildSettings;
window.loadChildrenForModal = loadChildrenForModal;
window.closeChildSettingsModal = closeChildSettingsModal;
window.saveChildSettings = saveChildSettings;
window.onSettingsGenderChange = onSettingsGenderChange;
window.onSettingsAvatarUpload = onSettingsAvatarUpload;


/**
 * Панель родителя
 * Управление правилами семьи, детьми, настройками
 */

let familyRules = [];

/**
 * Инициализация панели родителя
 */
async function initParentDashboard() {
  console.log('👨‍👩‍👧 Инициализация панели родителя...');
  
  try {
    // Загружаем правила семьи
    await loadFamilyRules();
    
    // Инициализируем управление детьми
    if (typeof initChildren === 'function') {
      await initChildren();
    } else {
      // Загружаем скрипт управления детьми
      const script = document.createElement('script');
      script.src = '/src/js/children.js';
      document.body.appendChild(script);
      await new Promise((resolve) => {
        script.onload = resolve;
      });
      if (typeof initChildren === 'function') {
        await initChildren();
      }
    }
    
    // Инициализируем обработчики событий
    initRulesHandlers();
    
    console.log('✅ Панель родителя инициализирована');
  } catch (error) {
    console.error('❌ Ошибка инициализации панели родителя:', error);
  }
}

/**
 * Загрузка правил семьи из backend
 */
async function loadFamilyRules() {
  try {
    console.log('📥 Загрузка правил семьи...');
    const response = await apiClient.get('/parent/rules');
    
    if (response && response.rules) {
      familyRules = response.rules;
      renderFamilyRules();
      console.log('✅ Правила семьи загружены:', familyRules);
    } else {
      console.warn('⚠️ Правила семьи не найдены, используем пустой список');
      familyRules = [];
      renderFamilyRules();
    }
  } catch (error) {
    console.error('❌ Ошибка загрузки правил семьи:', error);
    // Показываем ошибку пользователю
    const rulesList = document.getElementById('rules-list');
    if (rulesList) {
      rulesList.innerHTML = '<li style="color: #e74c3c;">Ошибка загрузки правил. Попробуйте обновить страницу.</li>';
    }
  }
}

/**
 * Сохранение правил семьи в backend
 */
async function saveFamilyRules() {
  try {
    console.log('💾 Сохранение правил семьи...', familyRules);
    await apiClient.put('/parent/rules', { rules: familyRules });
    console.log('✅ Правила семьи сохранены');
    return true;
  } catch (error) {
    console.error('❌ Ошибка сохранения правил семьи:', error);
    alert('Ошибка сохранения правил. Попробуйте еще раз.');
    return false;
  }
}

/**
 * Отображение правил семьи
 */
function renderFamilyRules() {
  const container = document.getElementById('rules-list');
  if (!container) {
    console.warn('⚠️ Контейнер правил не найден');
    return;
  }
  
  container.innerHTML = '';
  
  if (familyRules.length === 0) {
    container.innerHTML = '<li style="color: #999; font-style: italic;">Правила еще не добавлены</li>';
    return;
  }
  
  familyRules.forEach((rule, index) => {
    const li = document.createElement('li');
    li.className = 'rule-item';
    li.style.cssText = 'display: flex; align-items: center; justify-content: space-between; padding: 12px; margin-bottom: 8px; background: #f8f9fa; border-radius: 8px;';
    
    const ruleText = document.createElement('span');
    ruleText.textContent = rule;
    ruleText.style.cssText = 'flex: 1; margin-right: 12px;';
    ruleText.id = `rule-text-${index}`;
    
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.cssText = 'display: flex; gap: 8px;';
    
    // Кнопка редактирования
    const editBtn = document.createElement('button');
    editBtn.textContent = '✏️';
    editBtn.title = 'Редактировать';
    editBtn.style.cssText = 'background: #667eea; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 14px;';
    editBtn.onclick = () => editRule(index);
    
    // Кнопка удаления
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '🗑️';
    deleteBtn.title = 'Удалить';
    deleteBtn.style.cssText = 'background: #e74c3c; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 14px;';
    deleteBtn.onclick = () => deleteRule(index);
    
    buttonsContainer.appendChild(editBtn);
    buttonsContainer.appendChild(deleteBtn);
    
    li.appendChild(ruleText);
    li.appendChild(buttonsContainer);
    container.appendChild(li);
  });
}

/**
 * Добавление нового правила
 */
async function addFamilyRule() {
  const textInput = document.getElementById('new-rule-text');
  if (!textInput) {
    console.error('❌ Поле ввода правила не найдено');
    return;
  }
  
  const text = textInput.value.trim();
  if (!text) {
    alert('Введите текст правила');
    return;
  }
  
  familyRules.push(text);
  textInput.value = '';
  
  // Сохраняем в backend
  const saved = await saveFamilyRules();
  if (saved) {
    renderFamilyRules();
    // Закрываем модальное окно
    if (typeof window.closeRuleModal === 'function') {
      window.closeRuleModal();
    } else {
      const modal = document.getElementById('rule-modal');
      if (modal) {
        modal.classList.remove('active');
      }
    }
  } else {
    // Откатываем изменение при ошибке
    familyRules.pop();
  }
}

/**
 * Редактирование правила
 */
function editRule(index) {
  const currentText = familyRules[index];
  if (!currentText) {
    console.error('❌ Правило не найдено по индексу:', index);
    return;
  }
  
  // Показываем модальное окно редактирования
  const editModal = document.getElementById('edit-rule-modal');
  const editInput = document.getElementById('edit-rule-text');
  
  if (!editModal || !editInput) {
    // Создаем модальное окно, если его нет
    createEditRuleModal();
    // Повторяем вызов после создания
    setTimeout(() => editRule(index), 100);
    return;
  }
  
  editInput.value = currentText;
  editInput.dataset.ruleIndex = index;
  editModal.style.display = 'flex';
  editInput.focus();
}

/**
 * Сохранение отредактированного правила
 */
async function saveEditedRule() {
  const editInput = document.getElementById('edit-rule-text');
  const editModal = document.getElementById('edit-rule-modal');
  
  if (!editInput || !editModal) {
    console.error('❌ Элементы редактирования не найдены');
    return;
  }
  
  const newText = editInput.value.trim();
  if (!newText) {
    alert('Введите текст правила');
    return;
  }
  
  const index = parseInt(editInput.dataset.ruleIndex);
  if (isNaN(index) || index < 0 || index >= familyRules.length) {
    console.error('❌ Неверный индекс правила:', index);
    return;
  }
  
  const oldText = familyRules[index];
  familyRules[index] = newText;
  
  // Сохраняем в backend
  const saved = await saveFamilyRules();
  if (saved) {
    renderFamilyRules();
    closeEditRuleModal();
  } else {
    // Откатываем изменение при ошибке
    familyRules[index] = oldText;
  }
}

/**
 * Удаление правила
 */
async function deleteRule(index) {
  if (index < 0 || index >= familyRules.length) {
    console.error('❌ Неверный индекс правила:', index);
    return;
  }
  
  const ruleText = familyRules[index];
  if (!confirm(`Удалить правило "${ruleText}"?`)) {
    return;
  }
  
  const deletedRule = familyRules.splice(index, 1)[0];
  
  // Сохраняем в backend
  const saved = await saveFamilyRules();
  if (saved) {
    renderFamilyRules();
  } else {
    // Откатываем изменение при ошибке
    familyRules.splice(index, 0, deletedRule);
  }
}

/**
 * Инициализация обработчиков событий
 */
function initRulesHandlers() {
  // Создаем модальное окно редактирования, если его нет
  if (!document.getElementById('edit-rule-modal')) {
    createEditRuleModal();
  }
  
  // Убеждаемся, что функции openRuleModal и closeRuleModal доступны
  if (typeof window.openRuleModal === 'undefined') {
    window.openRuleModal = function() {
      const modal = document.getElementById('rule-modal');
      if (modal) {
        modal.classList.add('active');
        const input = document.getElementById('new-rule-text');
        if (input) {
          input.value = '';
          input.focus();
        }
      }
    };
  }
  
  if (typeof window.closeRuleModal === 'undefined') {
    window.closeRuleModal = function() {
      const modal = document.getElementById('rule-modal');
      if (modal) {
        modal.classList.remove('active');
      }
    };
  }
}

/**
 * Создание модального окна для редактирования правила
 */
function createEditRuleModal() {
  const modal = document.createElement('div');
  modal.id = 'edit-rule-modal';
  modal.style.cssText = `
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 10000;
    align-items: center;
    justify-content: center;
  `;
  
  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 30px;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  `;
  
  modalContent.innerHTML = `
    <h3 style="margin-top: 0; color: #333;">✏️ Редактировать правило</h3>
    <input 
      type="text" 
      id="edit-rule-text" 
      placeholder="Текст правила" 
      style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; margin-bottom: 20px; box-sizing: border-box;"
    />
    <div style="display: flex; gap: 10px; justify-content: flex-end;">
      <button 
        onclick="closeEditRuleModal()" 
        style="padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; background: #e0e0e0; color: #333;"
      >
        Отмена
      </button>
      <button 
        onclick="saveEditedRule()" 
        style="padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; background: #667eea; color: white;"
      >
        Сохранить
      </button>
    </div>
  `;
  
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Закрытие по клику вне модального окна
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeEditRuleModal();
    }
  });
  
  // Закрытие по Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display === 'flex') {
      closeEditRuleModal();
    }
  });
}

/**
 * Закрытие модального окна редактирования
 */
function closeEditRuleModal() {
  const modal = document.getElementById('edit-rule-modal');
  if (modal) {
    modal.style.display = 'none';
    const input = document.getElementById('edit-rule-text');
    if (input) {
      input.value = '';
      delete input.dataset.ruleIndex;
    }
  }
}

// Экспортируем функции для использования в HTML
window.initParentDashboard = initParentDashboard;
window.addFamilyRule = addFamilyRule;
window.editRule = editRule;
window.saveEditedRule = saveEditedRule;
window.deleteRule = deleteRule;
window.closeEditRuleModal = closeEditRuleModal;

// Экспортируем функции для модального окна добавления правила
window.openRuleModal = function() {
  const modal = document.getElementById('rule-modal');
  if (modal) {
    modal.classList.add('active');
    const input = document.getElementById('new-rule-text');
    if (input) {
      input.value = '';
      input.focus();
    }
  }
};

window.closeRuleModal = function() {
  const modal = document.getElementById('rule-modal');
  if (modal) {
    modal.classList.remove('active');
  }
};

// Экспортируем функции для использования в HTML
window.initParentDashboard = initParentDashboard;
window.addFamilyRule = addFamilyRule;
window.editRule = editRule;
window.saveEditedRule = saveEditedRule;
window.deleteRule = deleteRule;
window.closeEditRuleModal = closeEditRuleModal;


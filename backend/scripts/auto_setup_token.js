// Скрипт для автоматической установки токена в браузере
// Выполните этот код в консоли браузера (F12)

(function() {
    const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2MTM3NTI4LCJ0eXBlIjoiYWNjZXNzIn0.hD3XHJQ-a2MjIA-LLzk6s4KzgSC4Fdo9JUybWwkwRnM';
    
    console.log('🔐 Установка токена...');
    
    try {
        localStorage.setItem('admin_token', TOKEN);
        console.log('✅ Токен установлен в localStorage');
        
        // Проверяем установку
        const savedToken = localStorage.getItem('admin_token');
        if (savedToken === TOKEN) {
            console.log('✅ Токен успешно сохранен и проверен');
            console.log('📋 Токен (первые 50 символов):', TOKEN.substring(0, 50) + '...');
            
            // Тестируем токен
            console.log('🧪 Тестирование токена...');
            fetch('http://89.104.74.123:8000/api/admin/stats', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${TOKEN}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (response.ok) {
                    console.log('✅ Токен работает! Сервер принял запрос.');
                    return response.json();
                } else {
                    console.warn('⚠️ Сервер вернул статус:', response.status);
                    return response.text();
                }
            })
            .then(data => {
                console.log('📦 Ответ сервера:', data);
            })
            .catch(error => {
                console.error('❌ Ошибка проверки токена:', error);
            });
            
            console.log('🚀 Теперь обновите страницу админки (F5)');
        } else {
            console.error('❌ Ошибка: токен не сохранился правильно');
        }
    } catch (e) {
        console.error('❌ Ошибка установки токена:', e);
    }
})();


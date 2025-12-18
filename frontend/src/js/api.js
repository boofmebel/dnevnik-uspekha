/**
 * API клиент для работы с backend
 * Согласно rules.md: подготовка к backend интеграции
 * 
 * Этот модуль абстрагирует работу с API, позволяя легко переключиться
 * с localStorage на backend API в будущем
 */

const API_BASE_URL = window.location.origin + '/api';

/**
 * Базовый класс для работы с API
 */
class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this.accessToken = null;
  }

  /**
   * Установка access token
   * Согласно rules.md: токен хранится только в памяти
   */
  setAccessToken(token) {
    this.accessToken = token;
  }

  /**
   * Получение access token из памяти
   */
  getAccessToken() {
    return this.accessToken;
  }

  /**
   * Базовый метод для выполнения запросов
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Добавляем access token в заголовок (согласно rules.md)
    if (this.accessToken) {
      config.headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    try {
      const response = await fetch(url, config);
      
      // Обработка 401 - токен истёк, нужно обновить
      if (response.status === 401) {
        const newToken = await this.refreshToken();
        if (newToken) {
          config.headers['Authorization'] = `Bearer ${newToken}`;
          const retryResponse = await fetch(url, config);
          if (!retryResponse.ok) {
            const errorData = await retryResponse.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${retryResponse.status}`);
          }
          return await retryResponse.json();
        } else {
          // Если не удалось обновить токен, перенаправляем на страницу входа
          throw new Error('Требуется авторизация');
        }
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (window.errorHandler) {
        window.errorHandler.log(
          window.errorHandler.LogLevel.ERROR,
          'API request failed',
          { endpoint, error: error.message }
        );
      }
      throw error;
    }
  }

  /**
   * Обновление access token через refresh token
   * Согласно rules.md: refresh token в HttpOnly cookie
   */
  async refreshToken() {
    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include', // Для отправки HttpOnly cookie
      });

      if (response.ok) {
        const data = await response.json();
        this.setAccessToken(data.access_token);
        return data.access_token;
      }
    } catch (error) {
      if (window.errorHandler) {
        window.errorHandler.log(
          window.errorHandler.LogLevel.ERROR,
          'Token refresh failed',
          { error: error.message }
        );
      }
    }
    return null;
  }

  // Методы для работы с API

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // Методы для работы с конкретными endpoints

  // Аутентификация
  async login(email, password) {
    const data = await this.post('/auth/login', { email, password });
    if (data.access_token) {
      this.setAccessToken(data.access_token);
    }
    return data;
  }

  async logout() {
    await this.post('/auth/logout', {});
    this.setAccessToken(null);
  }

  // Дети
  async getChildren() {
    return this.get('/children/');
  }

  async createChild(childData) {
    return this.post('/children/', childData);
  }

  async updateChild(childId, childData) {
    return this.put(`/children/${childId}`, childData);
  }

  // Задачи
  async getTasks() {
    return this.get('/tasks/');
  }

  async createTask(taskData) {
    return this.post('/tasks/', taskData);
  }

  async updateTask(taskId, taskData) {
    return this.put(`/tasks/${taskId}`, taskData);
  }

  async deleteTask(taskId) {
    return this.delete(`/tasks/${taskId}`);
  }

  // Звёзды
  async getStars() {
    return this.get('/stars/');
  }

  async addStars(description, stars) {
    return this.post('/stars/add', { description, stars });
  }

  async exchangeStars(stars) {
    return this.post('/stars/exchange', { stars });
  }

  async checkStreak() {
    return this.post('/stars/check-streak', {});
  }

  // Копилка
  async getPiggy() {
    return this.get('/piggy/');
  }

  async updatePiggyGoal(name, amount) {
    return this.put('/piggy/goal', { name, amount });
  }

  async addPiggyMoney(amount, description) {
    return this.post('/piggy/add', { amount, description });
  }

  // Юридические тексты
  async getTerms() {
    return this.get('/legal/terms');
  }

  async getPrivacy() {
    return this.get('/legal/privacy');
  }

  async getSubscriptionTerms() {
    return this.get('/legal/subscription');
  }

  // Подписка
  async getSubscription() {
    return this.get('/subscription/');
  }

  async createParentConsent(childId, consentGiven, ipAddress, userAgent) {
    return this.post('/subscription/consent', {
      child_id: childId,
      consent_given: consentGiven,
      ip_address: ipAddress,
      user_agent: userAgent
    });
  }

  async cancelSubscription(reason) {
    return this.post('/subscription/cancel', { reason });
  }

  async requestRefund(reason, parentConsent) {
    return this.post('/subscription/refund-request', {
      reason,
      parent_consent: parentConsent
    });
  }

  // Поддержка
  async createComplaint(subject, message, parentConsent) {
    return this.post('/support/complaint', {
      subject,
      message,
      parent_consent: parentConsent
    });
  }

  // Настройки
  async getSettings() {
    return this.get('/settings/');
  }

  async updateSettings(starsToMoney, moneyPerStars) {
    return this.put('/settings/', { stars_to_money: starsToMoney, money_per_stars: moneyPerStars });
  }

  // Статистика
  async getWeeklyStats() {
    return this.get('/stats/');
  }

  async updateDailyStat() {
    return this.post('/stats/update', {});
  }

  // Дневник
  async getDiaryEntries() {
    return this.get('/diary/');
  }

  async createDiaryEntry(title, content) {
    return this.post('/diary/', { title, content });
  }

  async updateDiaryEntry(entryId, title, content) {
    return this.put(`/diary/${entryId}`, { title, content });
  }

  async deleteDiaryEntry(entryId) {
    return this.delete(`/diary/${entryId}`);
  }

  // Список желаний
  async getWishlist() {
    return this.get('/wishlist/');
  }

  async createWishlistItem(name, price, position) {
    return this.post('/wishlist/', { name, price, position });
  }

  async updateWishlistItem(itemId, name, price, achieved, position) {
    return this.put(`/wishlist/${itemId}`, { name, price, achieved, position });
  }

  async deleteWishlistItem(itemId) {
    return this.delete(`/wishlist/${itemId}`);
  }

  // Юридические тексты
  async getTerms() {
    return this.get('/legal/terms');
  }

  async getPrivacy() {
    return this.get('/legal/privacy');
  }

  async getSubscriptionTerms() {
    return this.get('/legal/subscription');
  }

  // Подписка
  async getSubscription() {
    return this.get('/subscription/');
  }

  async createParentConsent(childId, consentGiven) {
    return this.post('/subscription/consent', { child_id: childId, consent_given: consentGiven });
  }

  async cancelSubscription(reason) {
    return this.post('/subscription/cancel', { reason });
  }

  async requestRefund(reason, parentConsent) {
    return this.post('/subscription/refund-request', { reason, parent_consent: parentConsent });
  }

  // Поддержка
  async createComplaint(subject, message, parentConsent) {
    return this.post('/support/complaint', { subject, message, parent_consent: parentConsent });
  }

  // Админ-панель
  async getAdminStats() {
    return this.get('/admin/stats');
  }

  async getAdminUsers(skip = 0, limit = 50, role = null) {
    let url = `/admin/users?skip=${skip}&limit=${limit}`;
    if (role) url += `&role=${role}`;
    return this.get(url);
  }

  async updateAdminUser(userId, userData) {
    return this.put(`/admin/users/${userId}`, userData);
  }

  async deleteAdminUser(userId) {
    return this.delete(`/admin/users/${userId}`);
  }

  async getAdminChildren(skip = 0, limit = 50) {
    return this.get(`/admin/children?skip=${skip}&limit=${limit}`);
  }

  async getAdminSubscriptions(skip = 0, limit = 50, activeOnly = false) {
    let url = `/admin/subscriptions?skip=${skip}&limit=${limit}`;
    if (activeOnly) url += '&active_only=true';
    return this.get(url);
  }

  async getAdminNotifications(skip = 0, limit = 50, type = null) {
    let url = `/admin/notifications?skip=${skip}&limit=${limit}`;
    if (type) url += `&type=${type}`;
    return this.get(url);
  }
}

// Создаём глобальный экземпляр API клиента
const apiClient = new ApiClient();

// Экспорт для использования в других модулях
window.apiClient = apiClient;


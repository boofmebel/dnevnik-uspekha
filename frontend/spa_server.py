#!/usr/bin/env python3
"""SPA сервер для фронтенда с поддержкой клиентского роутинга и проксированием API"""
import http.server
import socketserver
from urllib.parse import urlparse, urlunparse
import os
import urllib.request
import json

BACKEND_URL = "http://localhost:8000"

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        # CORS headers для проксирования API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRF-Token')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Обработка preflight запросов CORS"""
        self.send_response(200)
        self.end_headers()
    
    def proxy_request(self, method):
        """Проксирование запроса на backend"""
        try:
            # Формируем URL для backend
            backend_url = f"{BACKEND_URL}{self.path}"
            if self.path.startswith('/api'):
                # Убираем /api из пути, так как backend уже имеет префикс /api
                backend_url = f"{BACKEND_URL}{self.path}"
            
            # Получаем заголовки
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'connection']:
                    headers[key] = value
            
            # Получаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Создаём запрос
            req = urllib.request.Request(backend_url, data=body, headers=headers, method=method)
            
            # Выполняем запрос
            with urllib.request.urlopen(req, timeout=30) as response:
                # Отправляем статус
                self.send_response(response.getcode())
                
                # Копируем заголовки (кроме некоторых)
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                
                self.end_headers()
                
                # Копируем тело ответа
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, f"Proxy error: {str(e)}")
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Проксируем API запросы на backend
        if path.startswith('/api'):
            self.proxy_request('GET')
            return
        
        # Специальная обработка для staff страниц
        if path == '/staff/login' or path == '/staff':
            staff_html_path = os.path.join(os.getcwd(), 'staff.html')
            if os.path.exists(staff_html_path):
                self.path = '/staff.html'
                return super().do_GET()
        if path == '/staff/dashboard' or path == '/staff-dashboard.html':
            staff_dashboard_path = os.path.join(os.getcwd(), 'staff-dashboard.html')
            if os.path.exists(staff_dashboard_path):
                self.path = '/staff-dashboard.html'
                return super().do_GET()
        
        # Если запрашивается файл (с расширением) - отдаём как есть
        if '.' in os.path.basename(path) and path != '/':
            if os.path.exists('.' + path):
                return super().do_GET()
        
        # Для всех остальных маршрутов отдаём index.html (SPA fallback)
        if os.path.exists('./index.html'):
            self.path = '/index.html'
            return super().do_GET()
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        if self.path.startswith('/api'):
            self.proxy_request('POST')
        else:
            self.send_error(404, "Not found")
    
    def do_PUT(self):
        if self.path.startswith('/api'):
            self.proxy_request('PUT')
        else:
            self.send_error(404, "Not found")
    
    def do_DELETE(self):
        if self.path.startswith('/api'):
            self.proxy_request('DELETE')
        else:
            self.send_error(404, "Not found")
    
    def do_PATCH(self):
        if self.path.startswith('/api'):
            self.proxy_request('PATCH')
        else:
            self.send_error(404, "Not found")

if __name__ == '__main__':
    PORT = 3000
    os.chdir('/Users/evgeniypomytkin/Вика/frontend')
    
    with socketserver.TCPServer(("", PORT), SPAHandler) as httpd:
        print(f"🚀 Frontend сервер запущен на http://localhost:{PORT}")
        print(f"📁 Рабочая директория: {os.getcwd()}")
        print(f"✅ SPA роутинг включен - все маршруты ведут на index.html")
        print(f"\n📌 Ссылки:")
        print(f"   - Product: http://localhost:{PORT}")
        print(f"   - Staff Login: http://localhost:{PORT}/staff/login")
        print(f"   (Нажмите Ctrl+C для остановки)\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Сервер остановлен")



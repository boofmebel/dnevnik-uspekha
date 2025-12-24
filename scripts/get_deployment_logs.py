#!/usr/bin/env python3
"""
Скрипт для получения логов деплоя из GitHub Actions
Требует GITHUB_TOKEN с правами: repo, workflow, actions:read
"""
import os
import sys
import json
import urllib.request
import urllib.error

def get_latest_run_logs(repo_owner="boofmebel", repo_name="dnevnik-uspekha", workflow_name="Deploy to Production"):
    """Получает логи последнего запуска workflow"""
    
    # Получаем токен
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print("❌ ОШИБКА: GITHUB_TOKEN не установлен!")
        print("\n📋 Установите токен:")
        print("export GITHUB_TOKEN='your-token-here'")
        return None
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Python-Script'
    }
    
    # 1. Получаем список последних запусков
    print("🔍 Получаю список запусков...")
    runs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs?per_page=1"
    
    try:
        req = urllib.request.Request(runs_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            runs = data.get('workflow_runs', [])
            if not runs:
                print("❌ Запуски не найдены")
                return None
            
            latest_run = runs[0]
            run_id = latest_run['id']
            run_url = latest_run['html_url']
            status = latest_run['status']
            conclusion = latest_run['conclusion']
            
            print(f"✅ Найден запуск: {run_id}")
            print(f"   Статус: {status}, Результат: {conclusion}")
            print(f"   URL: {run_url}")
            
            # 2. Получаем информацию о job
            print("\n🔍 Получаю информацию о job...")
            jobs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/jobs"
            req = urllib.request.Request(jobs_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                jobs_data = json.loads(response.read())
                jobs = jobs_data.get('jobs', [])
                if not jobs:
                    print("❌ Jobs не найдены")
                    return None
                
                job = jobs[0]
                job_id = job['id']
                job_name = job['name']
                job_conclusion = job['conclusion']
                
                print(f"✅ Job: {job_name} (ID: {job_id})")
                print(f"   Результат: {job_conclusion}")
                
                # 3. Получаем логи
                print("\n🔍 Получаю логи...")
                logs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs"
                req = urllib.request.Request(logs_url, headers=headers)
                
                try:
                    with urllib.request.urlopen(req) as response:
                        if response.status == 200:
                            # Логи возвращаются как tar.gz архив
                            logs_data = response.read()
                            print(f"✅ Логи получены ({len(logs_data)} байт)")
                            
                            # Сохраняем в файл
                            logs_file = f"deployment_logs_{run_id}.tar.gz"
                            with open(logs_file, 'wb') as f:
                                f.write(logs_data)
                            print(f"💾 Логи сохранены в: {logs_file}")
                            
                            # Пытаемся извлечь и показать ошибки
                            import tarfile
                            import io
                            try:
                                tar = tarfile.open(fileobj=io.BytesIO(logs_data))
                                print("\n📋 Содержимое логов:")
                                for member in tar.getmembers():
                                    if member.isfile():
                                        print(f"  - {member.name}")
                                        if 'Deploy via SSH' in member.name or 'deploy' in member.name.lower():
                                            file_obj = tar.extractfile(member)
                                            if file_obj:
                                                content = file_obj.read().decode('utf-8', errors='ignore')
                                                # Ищем ошибки
                                                lines = content.split('\n')
                                                error_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['error', 'failed', 'ошибка', 'не настроен', 'not configured', 'permission denied', 'connection refused'])]
                                                if error_lines:
                                                    print(f"\n❌ ОШИБКИ в {member.name}:")
                                                    for error_line in error_lines[:20]:  # Первые 20 строк с ошибками
                                                        print(f"   {error_line}")
                            except Exception as e:
                                print(f"⚠️  Не удалось распаковать логи: {e}")
                                print("   Используйте: tar -xzf deployment_logs_*.tar.gz")
                            
                            return logs_file
                        else:
                            print(f"❌ Статус ответа: {response.status}")
                            return None
                            
                except urllib.error.HTTPError as e:
                    print(f"❌ Ошибка при получении логов: {e.code}")
                    if e.code == 403:
                        print("⚠️  Нужны права: actions:read")
                        error_data = json.loads(e.read().decode())
                        print(f"   Сообщение: {error_data.get('message', 'N/A')}")
                    elif e.code == 404:
                        print("⚠️  Логи не найдены или еще не готовы")
                    else:
                        try:
                            error_data = json.loads(e.read().decode())
                            print(f"   Детали: {error_data.get('message', 'N/A')}")
                        except:
                            print(f"   Ответ: {e.read().decode()[:200]}")
                    return None
                    
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка HTTP: {e.code}")
        try:
            error_data = json.loads(e.read().decode())
            print(f"   Сообщение: {error_data.get('message', 'N/A')}")
        except:
            pass
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    get_latest_run_logs()


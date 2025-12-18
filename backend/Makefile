.PHONY: install run migrate upgrade downgrade test clean create-admin check

# Установка зависимостей
install:
	pip install -r requirements.txt

# Запуск приложения
run:
	python run.py

# Создание новой миграции
migrate:
	alembic revision --autogenerate -m "$(msg)"

# Применение миграций
upgrade:
	alembic upgrade head

# Откат миграций
downgrade:
	alembic downgrade -1

# Создание администратора
create-admin:
	python scripts/create_admin.py

# Проверка импортов
check:
	python scripts/check_imports.py

# Очистка
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete


# Конфигурация
VENV_DIR = venv
PROJECT_DIR = planner
REQUIREMENTS = requirements.txt
PIP = $(VENV_DIR)/bin/pip
MANAGE = cd $(PROJECT_DIR) && python3 manage.py

# Цвета для вывода
GREEN = \033[0;32m
NC = \033[0m

.PHONY: help run install makemigrations migrate shell test venv

# Помощь по командам
help:
	@echo "$(GREEN)Доступные команды:$(NC)"
	@echo "  make run            - Запуск сервера разработки"
	@echo "  make install        - Установка зависимостей"
	@echo "  make makemigrations - Создать миграции"
	@echo "  make migrate        - Применить миграции"
	@echo "  make shell          - Django shell"
	@echo "  make test           - Запуск тестов"

# Запуск сервера разработки
run:
	@echo "$(GREEN)Запуск сервера разработки...$(NC)"
	@$(MANAGE) runserver

# Установка зависимостей
install:
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r $(REQUIREMENTS)

# Создание миграций
makemigrations:
	@echo "$(GREEN)Создание миграций...$(NC)"
	@$(MANAGE) makemigrations

# Применение миграций
migrate:
	@echo "$(GREEN)Применение миграций...$(NC)"
	@$(MANAGE) migrate

# Django shell
shell:
	@$(MANAGE) shell

# Тесты
test:
	@echo "$(GREEN)Запуск тестов...$(NC)"
	@$(MANAGE) test
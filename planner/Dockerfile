FROM python:3.10.16-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

# Даем права на выполнение скриптов для запуска
RUN chmod +x deploy_scripts/*

CMD ["gunicorn", "planner.wsgi:application", "--bind", "0:8000", "--workers", "4" ]
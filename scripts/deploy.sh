#!/bin/bash

# Ручной деплой на сервер.
# Используется как запасной вариант, если автоматический CD (GitHub Actions)
# по какой-то причине недоступен — можно задеплоить руками одной командой.
#
# Запускается С ТВОЕГО компьютера:
#   ./scripts/deploy.sh

set -e

SERVER_USER="root"
SERVER_HOST="ВАШ_IP_СЕРВЕРА"
PROJECT_PATH="/home/notes-app"

echo "Подключаюсь к серверу и обновляю приложение..."

ssh "$SERVER_USER@$SERVER_HOST" << EOF
  set -e
  cd "$PROJECT_PATH"
  echo "Забираю последний код из main..."
  git pull origin main

  echo "Пересобираю и перезапускаю контейнеры..."
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

  echo "Готово. Текущий статус контейнеров:"
  docker-compose ps
EOF

echo "Деплой завершён."

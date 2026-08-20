#!/bin/bash

# Скрипт бэкапа базы данных Postgres.
# Делает дамп базы, архивирует, удаляет бэкапы старше 7 дней.
# Запускать на сервере через cron, например каждую ночь в 3:00.

set -e  # если любая команда завершится с ошибкой — сразу остановить скрипт

# ----- Настройки -----
BACKUP_DIR="/home/backups/notes-app"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/notes_db_$TIMESTAMP.sql.gz"

CONTAINER_NAME="notes-app-postgres-1"   # имя контейнера, docker ps покажет точное
DB_USER="notes_user"
DB_NAME="notes_db"

# ----- Сам бэкап -----
mkdir -p "$BACKUP_DIR"

echo "Создаю дамп базы данных..."
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "Бэкап сохранён: $BACKUP_FILE"

# ----- Удаление старых бэкапов -----
echo "Удаляю бэкапы старше 7 дней..."
find "$BACKUP_DIR" -name "notes_db_*.sql.gz" -mtime +7 -delete

echo "Готово."

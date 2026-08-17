# Notes App — Client (Kivy)

## Запуск локально

```bash
pip install -r requirements.txt
python main.py
```

По умолчанию приложение ходит на `http://localhost:8000` (backend).
Чтобы указать другой адрес:

```bash
API_BASE_URL=https://your-domain.com python main.py
```

## Тесты

```bash
pip install pytest
python -m pytest tests/ -v
```

## Структура

- `main.py` — точка входа, собирает ScreenManager из всех экранов
- `screens/` — экраны (логин, список заметок, редактор)
- `widgets/` — переиспользуемые виджеты (карточка заметки)
- `core/` — логика без Kivy: локальное хранилище (SQLite), API-клиент, синхронизация
- `tests/` — тесты core-логики

## Сборка APK

```bash
buildozer android debug
```

Готовый файл появится в `bin/*.apk`.

## Известные ограничения (MVP)

- Экран регистрации — заглушка, нужно доделать по паттерну login_screen
- Конфликты синхронизации разрешаются по правилу "кто новее — тот и победил"
  (по полю `updated_at`), без ручного разрешения конфликтов
- Токен авторизации не сохраняется между запусками приложения — нужно
  добавить его хранение (например, в том же SQLite или через keyring)

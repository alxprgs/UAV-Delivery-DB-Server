# UAV-Delivery-DB-Server

Серверная часть базы данных для проекта UAV-Delivery. Реализован на FastAPI, хранит данные в виде JSON-файлов, поддерживает авторизацию, CRUD-операции и резервное копирование.

## Возможности

- Аутентификация пользователей и сотрудников (JWT)
- CRUD-операции с коллекциями (insert, find, update, delete)
- Логирование действий и запросов
- Резервное копирование в Backblaze B2 (опционально)
- Простая настройка через `.env`
- Поддержка фильтрации, сортировки, пагинации

## Быстрый старт

1. **Установите зависимости:**
   ```
   pip install -r requirements.txt
   ```

2. **Настройте переменные окружения:**
   - Скопируйте `.env.example` в `.env` и заполните значения (или используйте уже существующий `.env`).

3. **Запустите сервер:**
   ```
   python run.py
   ```

4. **Документация API:**
   - Открыта по адресу: [http://localhost:31987/](http://localhost:31987/)

## Структура проекта

- `server/`
  - `core/` — ядро, конфиги, функции, инициализация пользователей
  - `routes/` — маршруты FastAPI (db, tools, specialized_db)
  - `logs/` — логи запросов и операций
  - `core/db_files/` — хранилище данных (users, workers, коллекции)
- `run.py` — точка входа

## Примеры запросов

- **Аутентификация:**
  ```
  POST /db/auth/db
  {
    "username": "root",
    "password": "<ROOT_PASSWORD>"
  }
  ```
- **Добавить элемент:**
  ```
  POST /db/insert/{db}/{collection}
  {
    "name": "Battery 4S",
    "capacity": 2200
  }
  ```
- **Поиск:**
  ```
  POST /db/find/{db}/{collection}
  {
    "name": "Battery 4S"
  }
  ```

## Переменные окружения

- `SECRET_KEY` — секрет для JWT
- `ROOT_PASSWORD` — пароль root-пользователя
- `SECURITY_ACCESS_CODE` — код доступа охраны
- `BACKBLAZE_APPLICATION_KEY`, `BACKBLAZE_APPLICATION_KEY_ID` — для резервного копирования (опционально)

## Лицензия

Проект распространяется по лицензии [Unlicense](LICENSE).

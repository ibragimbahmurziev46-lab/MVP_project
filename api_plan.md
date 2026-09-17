


# API Plan — Образовательная платформа

Базовый URL: `/api/v1`
Аутентификация: JWT

## Аутентификация
- POST `/auth/register` — регистрация
- POST `/auth/login` — вход
- GET `/auth/me` — текущий пользователь

## Курсы
- GET `/courses` — список курсов
- GET `/courses/{id}` — детали курса
- POST `/courses` — создать курс (преподаватель)
- POST `/courses/{id}/enroll` — записаться

## Уроки
- GET `/lessons/{id}` — детали урока
- POST `/lessons/{id}/complete` — отметить пройденным

## Тесты
- GET `/lessons/{id}/quiz` — получить тест
- POST `/lessons/{id}/quiz/submit` — отправить ответы

## Прогресс
- GET `/progress/me` — общий прогресс
- GET `/progress/courses/{id}` — прогресс по курсу

## Сертификаты
- GET `/certificates` — мои сертификаты
- GET `/certificates/verify/{code}` — проверка по коду

## Коды ошибок
400, 401, 403, 404, 409, 422 Добавить эндпоинт Get /materials 
## Курсы
- GET /courses
- POST /courses


Версия API: main
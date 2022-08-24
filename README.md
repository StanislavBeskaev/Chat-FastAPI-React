# Приложение чата
Простой чат на React + FastAPI  
Перед запуском необходимо заполнить файл .env в корне проекта. Обязательные переменные окружения:  
 - REACT_APP_WS_ADDRESS - хост:порт по которому подключаться к бекенду(8002 порт зашит в docker-compose.yaml )
 - ADMIN_PASSWORD - пароль админской учётной записи основного приложения(логин admin) 
 - GF_SECURITY_ADMIN_PASSWORD - пароль админской учётной записи для Grafana(логин admin)  

Запуск `docker-compose up`

## Сервисы
- 8002 порт - Основное приложение
- 9090 порт - Prometheus - сервис для сбора метрик
- 3421 порт - Grafana, есть преднастроенный dashboard для отображения метрик

## Установка зависимостей для разработки
Для управления зависимостями используется Poetry. Для установки зависомостей выполнить `poetry install`

## Тесты
Выполнить `python -m unittest`

## Code coverage
Собрать статистику покрытия: `coverage run -m unittest`
Отчёт о покрытии в консоли: `coverage report -m`
Отчёт о покрытии в html: `coverage html`

## Тесты и coverage
`coverage run -m unittest && coverage report -m`
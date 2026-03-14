# Organizational-Structure-API

RESTful API для управления организационной структурой компании с поддержкой иерархических подразделений и сотрудников.

**Try it out via Swagger UI**: http://localhost:8000/docs

`organizational-structure-api` — это  RESTful API для управления организационной структурой, разработанное на FastAPI. Оно предоставляет набор эндпоинтов для создания и управления иерархическими подразделениями и сотрудниками, с поддержкой сложных операций перемещения, каскадного удаления и глубокой вложенности.

Данный API включает поддержку всех основных операций CRUD для подразделений и сотрудников.

## Acknowledgements

Этот проект построен на основе современного стека технологий: **FastAPI**, **SQLAlchemy 2.0**, **Pydantic V2** и **PostgreSQL**. Мы благодарим всех авторов и контрибьюторов этих opensource-проектов за их вклад в сообщество разработчиков.

## Эндпоинты API

### Подразделения (Departments)

| Эндпоинт                       | Метод    | Описание                           | Параметры                           |
|--------------------------------|----------|------------------------------------|-------------------------------------|
| `/departments/`                | `POST`   | Создать подразделение              | `name`, `parent_id`                 |
| `/departments/{id}`            | `GET`    | Получить подразделение с деревом   | `depth`, `include_employees`        |
| `/departments/{id}`            | `PATCH`  | Обновить подразделение             | `name`, `parent_id`                 |
| `/departments/{id}`            | `DELETE` | Удалить подразделение              | `mode`, `reassign_to_department_id` |
| `/departments/{id}/employees`  | `GET`    | Получить сотрудников подразделения | `skip`, `limit`, `sort_by`          |
| `/departments/{id}/employees/` | `POST`   | Создать сотрудника в подразделении | `full_name`, `position`, `hired_at` |

### Сотрудники (Employees)

| Эндпоинт               | Метод    | Описание                  | Параметры                           |
|------------------------|----------|---------------------------|-------------------------------------|
| `/employees/{id}`      | `GET`    | Получить сотрудника по ID | -                                   |
| `/employees/{id}`      | `PATCH`  | Обновить сотрудника       | `full_name`, `position`, `hired_at` |
| `/employees/{id}`      | `DELETE` | Удалить сотрудника        | -                                   |
| `/employees/{id}/move` | `POST`   | Переместить сотрудника    | `new_department_id`                 |

## Установка и запуск

### Требования

- **Docker Desktop** или
- **Python 3.14+** и **PostgreSQL 16+** для локального запуска

### Старт с Docker 

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/VitalyShpak9222/Organizational-Structure-API/tree/dev
cd organizational-structure-api

# 2. Запустите Docker Desktop

# 3. Запустите приложение
docker-compose up --build
```

### Старт в Windows

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/VitalyShpak9222/Organizational-Structure-API/tree/dev
cd organizational-structure-api

# 2. Создайте и активируйте виртуальное окружение
python -m venv venv
venv\Scripts\activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Примините мигграции
alembic upgrade head

# 5. Запустите приложение
uvicorn app.main:app --reload
```

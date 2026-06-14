# Документация модуля базы данных

## Обзор

Модуль `database` предоставляет полнофункциональный ORM-интерфейс для взаимодействия с базой данных PostgreSQL в приложении VK Tinder Bot. Использует SQLAlchemy с пулом соединений для эффективных операций и потокобезопасным управлением сессиями.

## Архитектура

```
database/
├── __init__.py      # Публичный API и инициализация
├── base.py          # Базовый класс моделей
├── db_manager.py    # Менеджер подключения к БД
└── models/
    ├── user.py      # Модель BotUser
    ├── profile.py   # Модель VKProfile
    ├── interest.py  # Модель Interest и ассоциации M2M
    ├── interaction.py # Взаимодействия пользователей (лайки, просмотры, блокировки)
    ├── match.py     # Модели Match и Message
    └── location.py  # Модель Location
```

## Основные компоненты

### DatabaseManager (`db_manager.DatabaseManager`)

Управляет подключениями к PostgreSQL через SQLAlchemy с пулом соединений и scoped-сессиями для потокобезопасности.

**Ключевые возможности:**
- Пул соединений (QueuePool: 10 основных, 20 дополнительных)
- Автоматическая проверка состояния соединения (pool_pre_ping)
- Потокобезопасное управление сессиями через scoped_session
- Контекстный менеджер для безопасной работы с сессиями
- Поддержка выполнения сырого SQL

#### Пример использования

```python
from database.db_manager import db_manager

# Инициализация подключения к БД
db_manager.initialize()  # Использует настройки из config.py
# или
db_manager.initialize("postgresql://user:pass@host:5432/dbname")

# Создание таблиц
db_manager.create_tables(drop_first=False)

# Использование в контексте (автоматический commit/rollback)
with db_manager.get_session() as session:
    users = session.query(BotUser).filter_by(is_active=True).all()
    
# Выполнение сырого SQL
results = db_manager.execute_raw(
    "SELECT * FROM bot_users WHERE city = %(city)s", 
    {"city": "Москва"}
)

# Корректное завершение работы
db_manager.close()
```

#### Методы

**`initialize(db_url: Optional[str] = None) -> None`**

Инициализирует подключение к базе данных.

*Аргументы:*
- `db_url` (str, optional): Строка подключения к PostgreSQL. Если не указано, используются значения из `config.py`.

*Возможные исключения:*
- `ValueError`: Если параметры подключения отсутствуют.

**`create_tables(drop_first: bool = False) -> None`**

Создаёт все таблицы, определённые в моделях.

*Аргументы:*
- `drop_first` (bool): Если True, удаляет существующие таблицы перед созданием новых.

**`get_session() -> Generator[Session, None, None]`**

Контекстный менеджер, предоставляющий потокобезопасную сессию базы данных.

*Возвращает:*
- `Session`: Объект сессии SQLAlchemy.

*Пример:*
```python
with db_manager.get_session() as session:
    # Сессия автоматически коммитится или откатывается
    user = BotUser(vk_id=123, name="Иван")
    session.add(user)
```

**`execute_raw(query: str, params: dict | None = None) -> Any`**

Выполняет сырой SQL-запрос.

*Аргументы:*
- `query` (str): Строка SQL-запроса с именованными плейсхолдерами.
- `params` (dict, optional): Словарь параметров запроса.

*Возвращает:*
- Результаты для SELECT-запросов, количество затронутых строк для INSERT/UPDATE/DELETE.

**`close() -> None`**

Закрывает все соединения с базой данных и освобождает ресурсы движка.

---

### Базовый класс (`base.Base`)

Абстрактный базовый класс для всех моделей SQLAlchemy, предоставляющий общие поля и служебные методы.

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | Автоинкрементный первичный ключ |
| `created_at` | datetime | Время создания записи |
| `updated_at` | datetime | Время последнего обновления |

#### Методы

**`to_dict() -> dict`**

Преобразует экземпляр модели в словарь, пригодный для сериализации в JSON.

*Возвращает:*
- Словарь с именами столбцов в качестве ключей и значениями столбцов.

*Пример:*
```python
user = BotUser(vk_id=123, name="Иван")
user_dict = user.to_dict()
# {'id': 1, 'vk_id': 123, 'name': 'Иван', 'created_at': ..., 'updated_at': ...}
```

---

## Модели

### BotUser (`models.user.BotUser`)

Представляет пользователя бота, который ищет знакомства.

**Таблица:** `bot_users`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `vk_id` | int | ID пользователя ВКонтакте (уникальный) |
| `name` | str | Имя пользователя |
| `surname` | str | Фамилия пользователя |
| `birthdate` | date | Дата рождения (опционально) |
| `gender` | int | 0-не указано, 1-женщина, 2-мужчина |
| `looking_for` | int | 0-не важно, 1-женщины, 2-мужчины |
| `city` | str | Город проживания (опционально) |
| `age_min` | int | Минимальный возраст для мэтчей (по умолчанию: 18) |
| `age_max` | int | Максимальный возраст для мэтчей (по умолчанию: 99) |
| `max_distance` | int | Максимальное расстояние в км (по умолчанию: 50) |
| `is_active` | bool | Активен ли аккаунт |
| `last_active` | date | Дата последней активности (опционально) |

#### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `full_name` | str | Полное имя (имя + фамилия) |
| `age` | int | Возраст, вычисляемый по дате рождения |

#### Связи

- `interactions`: Один-ко-многим с `UserInteraction`
- `matches_as_user1`: Один-ко-многим с `Match` (как user1)
- `matches_as_user2`: Один-ко-многим с `Match` (как user2)
- `interests`: Многие-ко-многим с `Interest`

#### Индексы

- `idx_user_looking_gender`: (looking_for, gender)
- `idx_user_age_range`: (age_min, age_max)
- `idx_user_city_gender`: (city, gender)

---

### VKProfile (`models.profile.VKProfile`)

Представляет анкету пользователя ВКонтакте (потенциальный мэтч для пользователей).

**Таблица:** `vk_profiles`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `vk_id` | int | ID анкеты ВКонтакте (уникальный) |
| `first_name` | str | Имя анкеты |
| `last_name` | str | Фамилия анкеты |
| `birth_year` | int | Год рождения (опционально) |
| `gender` | int | 0-не указано, 1-женщина, 2-мужчина |
| `city` | str | Город (опционально) |
| `photo_urls` | list[str] | Список URL фото (опционально) |
| `relation` | int | Семейное положение (опционально) |
| `education` | str | Образование (опционально) |

#### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `age` | int | Возраст, вычисляемый по году рождения |
| `full_name` | str | Полное имя (имя + фамилия) |

#### Связи

- `interests`: Многие-ко-многим с `Interest`

#### Индексы

- `idx_profile_city_gender_age`: (city, gender, birth_year)
- `idx_profile_full_name`: (first_name, last_name)

---

### Interest (`models.interest.Interest`)

Представляет интерес/хобби (справочник для сопоставления пользователей и профилей).

**Таблица:** `interests`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `title` | str | Название интереса (уникальное) |
| `category` | str | Категория (music, sport и т.д.) |
| `vk_external_id` | int | ID группы/страницы ВКонтакте (опционально) |

#### Связи

- `users`: Многие-ко-многим с `BotUser`
- `profiles`: Многие-ко-многим с `VKProfile`

#### Индексы

- `idx_interest_title_trigram`: GIN-индекс для поиска по триграммам

---

### UserInteraction (`models.interaction.UserInteraction`)

Отслеживает все действия пользователей над анкетами (просмотр, лайк, дизлайк, блокировка).

**Таблица:** `user_interactions`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | int | ID пользователя, выполнившего действие |
| `profile_id` | int | ID целевой анкеты |
| `action` | str | Тип действия: view, like, dislike, block |

#### Связи

- `user`: Ссылка на `BotUser`
- `profile`: Ссылка на `VKProfile`

#### Ограничения

- Уникальное ограничение по (user_id, profile_id) — одно действие на пару
- Проверочное ограничение: action должен быть одним из ('view', 'like', 'dislike', 'block')

#### Индексы

- `idx_interaction_user_profile`: (user_id, profile_id) - уникальный
- `idx_interaction_user_action`: (user_id, action)
- `idx_interaction_profile_action`: (profile_id, action)

---

### MutualLike (`models.interaction.MutualLike`)

Представляет взаимные лайки (мэтчи) между пользователями и анкетами.

**Таблица:** `mutual_likes`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | int | ID пользователя, поставившего лайк |
| `profile_id` | int | ID анкеты, получившей лайк |
| `is_notified` | bool | Был ли пользователь уведомлён |

#### Индексы

- `idx_mutual_user_profile`: (user_id, profile_id) - уникальный

---

### Match (`models.match.Match`)

Представляет мэтч между двумя пользователями бота (взаимные лайки).

**Таблица:** `matches`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `user1_id` | int | ID первого пользователя (всегда меньший ID) |
| `user2_id` | int | ID второго пользователя (всегда больший ID) |
| `matched_at` | datetime | Время создания мэтча |
| `is_active` | bool | Активен ли мэтч |

#### Связи

- `user1`: Ссылка на `BotUser` (user1_id)
- `user2`: Ссылка на `BotUser` (user2_id)
- `messages`: Один-ко-многим с `Message`

#### Ограничения

- Проверочное ограничение: user1_id < user2_id
- Уникальное ограничение по (user1_id, user2_id)

#### Индексы

- `idx_match_users`: (user1_id, user2_id) - уникальный
- `idx_match_active_ordered`: (is_active, matched_at)

---

### Message (`models.match.Message`)

Представляет сообщение в чате мэтча.

**Таблица:** `messages`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `match_id` | int | ID мэтча |
| `sender_id` | int | ID отправителя |
| `text` | str | Текст сообщения |
| `sent_at` | datetime | Время отправки |
| `is_read` | bool | Прочитано ли сообщение |

#### Связи

- `match`: Ссылка на `Match`
- `sender`: Ссылка на `BotUser`

#### Индексы

- `idx_message_match_sent`: (match_id, sent_at)
- `idx_message_unread`: (match_id, is_read)

---

### Location (`models.location.Location`)

Хранит географическую информацию о городах.

**Таблица:** `locations`

#### Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `city_name` | str | Название города (уникальное) |
| `country` | str | Страна (по умолчанию: "Россия") |
| `latitude` | decimal | Широта (-90 до 90) |
| `longitude` | decimal | Долгота (-180 до 180) |
| `timezone` | str | Часовой пояс |
| `population` | int | Население |

#### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `coordinates` | tuple | Возвращает (широта, долгота) или None |

#### Индексы

- `idx_location_coords`: (latitude, longitude)
- `idx_location_country`: (country)

---

## Публичный API

### Экспорты модуля

Модуль `database/__init__.py` предоставляет удобный доступ ко всем компонентам:

```python
from database import (
    Base,
    db_manager,
    BotUser,
    VKProfile,
    Interest,
    UserInteraction,
    MutualLike,
    Match,
    Message,
    Location,
    user_interests,  # Ассоциативная таблица
    profile_interests  # Ассоциативная таблица
)
```

### Инициализация

```python
from database import init_db

# Инициализация с настройками по умолчанию
init_db()

# Инициализация с пользовательским URL
init_db("postgresql://user:pass@localhost:5432/mydb")

# Инициализация с удалением существующих таблиц
init_db(drop_tables=True)
```

---

## Примеры использования

### Создание таблиц

```python
from database.db_manager import db_manager

db_manager.initialize()
db_manager.create_tables()
```

### Добавление нового пользователя

```python
from database import db_manager, BotUser, Interest

with db_manager.get_session() as session:
    # Создание пользователя
    user = BotUser(
        vk_id=123456,
        name="Иван",
        surname="Петров",
        gender=2,
        looking_for=1,
        city="Москва",
        age_min=20,
        age_max=30
    )
    session.add(user)
    
    # Добавление интересов
    python_interest = session.query(Interest).filter_by(title="Python").first()
    if python_interest:
        user.interests.append(python_interest)
    
    # Сессия автоматически коммитится при успешном завершении
```

### Поиск потенциальных мэтчей

```python
from database import db_manager, BotUser, VKProfile

def find_potential_matches(user_id: int):
    with db_manager.get_session() as session:
        user = session.query(BotUser).get(user_id)
        
        # Поиск анкет, подходящих под критерии пользователя
        profiles = session.query(VKProfile).filter(
            VKProfile.gender == user.looking_for,
            VKProfile.city == user.city,
            VKProfile.birth_year >= user.birthdate.year - user.age_max,
            VKProfile.birth_year <= user.birthdate.year - user.age_min
        ).all()
        
        return profiles
```

### Запись лайка

```python
from database import db_manager, UserInteraction, MutualLike

def record_like(user_id: int, profile_id: int):
    with db_manager.get_session() as session:
        # Запись лайка
        interaction = UserInteraction(
            user_id=user_id,
            profile_id=profile_id,
            action="like"
        )
        session.add(interaction)
        
        # Проверка на взаимный лайк
        existing = session.query(UserInteraction).filter_by(
            user_id=profile_id,  # Предполагается, что профили используют те же ID
            profile_id=user_id,
            action="like"
        ).first()
        
        if existing:
            # Создание взаимного мэтча
            mutual = MutualLike(user_id=user_id, profile_id=profile_id)
            session.add(mutual)
```

### Получение непрочитанных сообщений

```python
from database import db_manager, Message

def get_unread_messages(user_id: int):
    with db_manager.get_session() as session:
        messages = session.query(Message).join(Match).filter(
            (Match.user1_id == user_id) | (Match.user2_id == user_id),
            Message.sender_id != user_id,
            Message.is_read == False
        ).all()
        return messages
```

---

## Конфигурация базы данных

Параметры подключения к базе данных загружаются из переменных окружения через `config.py`:

```python
class Config:
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    DATABASE = os.getenv('DATABASE')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
```

Установите эти переменные в вашем файле `.env`:

```env
HOST=localhost
PORT=5432
DATABASE=vk_tinder
USER=postgres
PASSWORD=ваш_пароль
```

---

## Рекомендации

1. **Всегда используйте контекстные менеджеры** для работы с сессиями базы данных:

```python
with db_manager.get_session() as session:
    # Операции с БД
    pass
# Сессия автоматически закрывается
```

2. **Явно обрабатывайте транзакции** для сложных операций:

```python
with db_manager.get_session() as session:
    try:
        # Несколько операций
        session.commit()
    except Exception as e:
        session.rollback()
        raise
```

3. **Используйте индексы** для часто запрашиваемых столбцов (уже определены в моделях)

4. **Избегайте N+1 запросов**, используя `lazy="selectin"` или `lazy="joined"` для связей

5. **Закрывайте соединения** при завершении работы приложения:

```python
# При завершении работы приложения
db_manager.close()
```

---

## Обработка ошибок

Распространённые ошибки и их решения:

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `psycopg2.OperationalError` | Не удалось подключиться к БД | Проверьте параметры подключения и доступность сервера |
| `SQLAlchemyError` | Ошибка выполнения запроса | Оберните в try/except, используйте session.rollback() |
| `IntegrityError` | Нарушение уникального ограничения | Проверьте существование записи перед вставкой |

```python
from sqlalchemy.exc import SQLAlchemyError

try:
    with db_manager.get_session() as session:
        # Операции с БД
        pass
except SQLAlchemyError as e:
    print(f"Ошибка БД: {e}")
    # Обработайте ошибку соответствующим образом
```

---

## Стратегия миграции

Для изменений схемы базы данных рекомендуется использовать Alembic:

```bash
pip install alembic
alembic init migrations
```

Настройте `alembic.ini` и `migrations/env.py` для использования вашего `db_manager.engine`.

---

*Документация модуля database для VK-Tinder-Bot v1.0*

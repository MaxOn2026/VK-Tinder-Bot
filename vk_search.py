"""Модуль поиска кандидатов ВКонтакте."""

import logging
from vk_client import get_vk_user_session

logger = logging.getLogger(__name__)


def get_user_info(user_id: int) -> dict:
    """Получает информацию о пользователе через VK API."""
    vk_user = get_vk_user_session().get_api()

    try:
        response = vk_user.users.get(
            user_ids=user_id, fields="sex,city,bdate,photo_200"
        )

        if not response:
            logger.warning(f"⚠️ Пользователь {user_id} не найден в VK API")
            return None

        user = response[0]

        # Определяем пол
        sex = user.get("sex", 0)  # 1-жен, 2-муж

        # Определяем возраст
        age = None
        if "bdate" in user:
            try:
                parts = user["bdate"].split(".")
                if len(parts) == 3:
                    age = 2026 - int(parts[2])
            except (ValueError, IndexError) as e:
                logger.debug(f"Не удалось распарсить дату рождения для {user_id}: {e}")

        # Определяем город
        city_id = None
        city_name = None
        if "city" in user:
            city_id = user["city"].get("id")
            city_name = user["city"].get("title")

        logger.info(f"✅ Получены данные пользователя {user_id}: пол={sex}, возраст={age}, город={city_name}")

        return {
            "id": user_id,
            "sex": sex,
            "age": age,
            "city_id": city_id,
            "city_name": city_name,
            "photo": user.get("photo_200", ""),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка получения данных пользователя {user_id}: {e}", exc_info=True)
        return None


def search_candidates(
    user_info: dict, user_id: int, count: int = 20, settings: dict = None
):
    """Ищет кандидатов для пользователя с учётом настроек."""
    vk_user = get_vk_user_session().get_api()

    # Параметры поиска
    sex = 1 if user_info["sex"] == 2 else 2  # Ищем противоположный пол
    city_id = user_info["city_id"]

    # Применяем настройки пользователя
    age_min = 18
    age_max = 99
    max_distance = 50

    if settings:
        age_min = settings.get("age_min", 18)
        age_max = settings.get("age_max", 99)
        max_distance = settings.get("max_distance", 50)

    logger.info(f"🔍 Поиск кандидатов для пользователя {user_id}: пол={sex}, город={city_id}, возраст={age_min}-{age_max}")

    try:
        # Поиск через VK API
        response = vk_user.users.search(
            sex=sex,
            city=city_id,
            age_from=age_min,
            age_to=age_max,
            has_photo=1,
            count=count * 2,
            fields="sex,city,bdate,photo_200",
        )

        if "items" not in response:
            logger.warning(f"⚠️ VK API не вернул items для пользователя {user_id}")
            return []

        candidates = []

        for item in response["items"]:
            candidate_id = item["id"]

            # Пропускаем самого пользователя
            if candidate_id == user_id:
                continue

            # Проверяем пол
            if item.get("sex") != sex:
                continue

            candidates.append(item)

            if len(candidates) >= count:
                break

        logger.info(f"✅ Найдено {len(candidates)} кандидатов из {len(response.get('items', []))} (после фильтрации)")
        return candidates

    except Exception as e:
        logger.error(f"❌ Ошибка поиска кандидатов для пользователя {user_id}: {e}", exc_info=True)
        return []


def format_candidate_info(candidate: dict) -> str:
    """Форматирует информацию о кандидате."""
    first_name = candidate.get("first_name", "")
    last_name = candidate.get("last_name", "")
    candidate_id = candidate["id"]
    profile_link = f"https://vk.com/id{candidate_id}"

    age_text = ""
    if "bdate" in candidate:
        try:
            parts = candidate["bdate"].split(".")
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except (ValueError, IndexError) as e:
            logger.debug(f"Не удалось распарсить дату рождения для кандидата {candidate_id}: {e}")

    city_text = ""
    if "city" in candidate:
        city_text = f", {candidate['city'].get('title', '')}"

    return f" {first_name} {last_name}{age_text}{city_text}\n🔗 {profile_link}"


def get_top_photos(user_id: int, count: int = 3) -> str:
    """Получает топ-N фото пользователя по лайкам."""
    vk_user = get_vk_user_session().get_api()

    try:
        photos = vk_user.photos.get(
            owner_id=user_id, album_id="profile", extended=1, count=100
        )

        if not photos or "items" not in photos:
            logger.warning(f"⚠️ Фотографии не найдены для пользователя {user_id}")
            return ""

        sorted_photos = sorted(
            photos["items"],
            key=lambda x: x.get("likes", {}).get("count", 0),
            reverse=True,
        )

        top_photos = sorted_photos[:count]

        attachments = []
        for photo in top_photos:
            attachment = f"photo{photo['owner_id']}_{photo['id']}"
            attachments.append(attachment)

        logger.info(f"📸 Получено {len(top_photos)} фото для пользователя {user_id}")
        return ",".join(attachments)

    except Exception as e:
        logger.error(f"❌ Ошибка получения фото для пользователя {user_id}: {e}", exc_info=True)
        return ""
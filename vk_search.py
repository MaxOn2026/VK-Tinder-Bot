"""Модуль для поиска людей через VK API."""
from vk_client import get_vk_user_session


def get_user_info(user_id):
    """
    Получает информацию о пользователе (пол, возраст, город).
    """
    vk_user = get_vk_user_session().get_api()
    
    try:
        response = vk_user.users.get(
            user_ids=user_id,
            fields='sex,city,bdate'
        )[0]
        
        age = None
        if 'bdate' in response:
            try:
                parts = response['bdate'].split('.')
                if len(parts) == 3:
                    birth_year = int(parts[2])
                    age = 2026 - birth_year
            except:
                pass
        
        city_id = response.get('city', {}).get('id')
        city_name = response.get('city', {}).get('title', 'Неизвестно')
        
        return {
            'sex': response.get('sex'),
            'age': age,
            'city_id': city_id,
            'city_name': city_name
        }
    except Exception as e:
        print(f"❌ Ошибка получения данных пользователя: {e}")
        return None


def search_candidates(user_info, user_id, count=20):
    """
    Ищет кандидатов через VK API users.search.
    Исключает заблокированных, избранных и уже просмотренных.
    """
    vk_user = get_vk_user_session().get_api()
    
    sex = user_info.get('sex')
    age = user_info.get('age')
    city_id = user_info.get('city_id')
    
    target_sex = 2 if sex == 1 else 1
    
    params = {
        'sex': target_sex,
        'count': count,
        'fields': 'photo_200,city,bdate'
    }
    
    if age:
        params['age_from'] = max(14, age - 3)
        params['age_to'] = min(100, age + 3)
    
    if city_id:
        params['city'] = city_id
    
    try:
        response = vk_user.users.search(**params)
        items = response.get('items', [])
        
        # Получаем списки для фильтрации
        from data_storage import get_favorites, get_blocked, get_views
        favorites = get_favorites(user_id)
        blocked = get_blocked(user_id)
        views = get_views(user_id)
        
        # Фильтруем
        filtered = []
        for item in items:
            candidate_id = item['id']
            
            # Пропускаем закрытые профили
            if item.get('is_closed', False):
                continue
            
            # Пропускаем себя
            if candidate_id == user_id:
                continue
            
            # Пропускаем заблокированных
            if candidate_id in blocked:
                continue
            
            # Пропускаем избранных
            if candidate_id in favorites:
                continue
            
            # Пропускаем уже просмотренных
            if candidate_id in views:
                continue
            
            filtered.append(item)
        
        print(f"✅ Найдено {len(filtered)} кандидатов из {count} (после фильтрации)")
        return filtered
        
    except Exception as e:
        print(f"❌ Ошибка поиска кандидатов: {e}")
        return []


def get_top_photos(user_id: int, count: int = 3) -> str:
    """Получает топ-N фото пользователя по лайкам."""
    from vk_client import get_vk_user_session
    
    vk_user = get_vk_user_session().get_api()
    
    try:
        # Получаем все фото пользователя
        photos = vk_user.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1,
            count=100
        )
        
        if not photos or 'items' not in photos:
            return ""
        
        # Сортируем по лайкам
        sorted_photos = sorted(
            photos['items'],
            key=lambda x: x.get('likes', {}).get('count', 0),
            reverse=True
        )
        
        # Берём топ-N фото
        top_photos = sorted_photos[:count]
        
        # Формируем строку вложений
        attachments = []
        for photo in top_photos:
            attachment = f"photo{photo['owner_id']}_{photo['id']}"
            attachments.append(attachment)
        
        return ','.join(attachments)
        
    except Exception as e:
        print(f"❌ Ошибка получения фото: {e}")
        return ""


def format_candidate_info(candidate):
    """
    Форматирует информацию о кандидате для сообщения.
    """
    first_name = candidate.get('first_name', '')
    last_name = candidate.get('last_name', '')
    candidate_id = candidate['id']
    profile_link = f"https://vk.com/id{candidate_id}"
    
    age_text = ""
    if 'bdate' in candidate:
        try:
            parts = candidate['bdate'].split('.')
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except:
            pass
    
    city_text = ""
    if 'city' in candidate:
        city_text = f", {candidate['city'].get('title', '')}"
    
    message = f"👤 {first_name} {last_name}{age_text}{city_text}\n🔗 {profile_link}"
    
    return message
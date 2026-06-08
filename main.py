import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import os
from dotenv import load_dotenv

load_dotenv()

GROUP_TOKEN = os.getenv('GROUP_TOKEN')

vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()

group_id = vk_session.method('groups.getById')[0]['id']
longpoll = VkBotLongPoll(vk_session, group_id=group_id)

print("🤖 Бот запущен! Жду сообщения...")
print("💡 Напишите боту что-нибудь в ВК\n")


def create_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('В избранное', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def send_message(user_id, message, attachment=None, keyboard=None):
    params = {
        'user_id': user_id,
        'message': message,
        'random_id': random.randint(-2147483648, 2147483647)
    }
    if attachment:
        params['attachment'] = attachment
    if keyboard:
        params['keyboard'] = keyboard
    
    vk.messages.send(**params)


"""Главный цикл"""
for event in longpoll.listen():
    print(f"\n📨 Получено событие: {event.type}")
    print(f"📋 Данные: {event.obj}")
    
    # Проверяем все типы событий
    if event.type == VkBotEventType.MESSAGE_NEW:
        print("✅ Это новое сообщение!")
        
        try:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']
            
            print(f"👤 От: {user_id}")
            print(f"💬 Текст: '{text}'")
            
            text_lower = text.lower().strip()
            
            if text_lower in ['начать', 'привет', '/start', 'hi', 'hello']:
                print("  → Отправляю приветствие с кнопками")
                send_message(
                    user_id, 
                    "Привет! Я VKinder Bot. Найду тебе пару! 👇", 
                    keyboard=create_keyboard()
                )
                print("  ✅ Отправлено!")
            
            elif text_lower == 'начать поиск':
                send_message(user_id, "🔍 Ищу подходящую пару...")
            
            elif text_lower == 'дальше':
                send_message(user_id, "➡️ Показываю следующего...")
            
            elif text_lower == 'в избранное':
                send_message(user_id, "❤️ Добавлено в избранное!")
            
            else:
                print("  → Неизвестная команда")
                send_message(
                    user_id,
                    "Я не понял. Вот что я умею:",
                    keyboard=create_keyboard()
                )
                
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("⏭️ Пропускаю другое событие")
from config import Config
from database.models.db_manager import DBManager

class User:
    def __init__(self, name: str, surname: str, # имя и фамилия пользователя
                birth_year: int, # год рождения пользователя
                vk_id: int, # id пользователя ВКонтакте
                gender: int, looking_for: int, # Пол пользователя и желаемый пол кандидата 1-мужской, 2-женский, 0-неизвестно
                age_min: int, age_max: int, # минимальный и максимальный возраст кандидата
                max_distance: int # максимальное расстояние до кандидата в км
                ):
    
        self.name = name
        self.surname = surname
        self.birth_year = birth_year
        self.vk_id = vk_id
        self.gender = gender
        self.looking_for = looking_for
        self.age_min = age_min
        self.age_max = age_max
        self.max_distance = max_distance
        
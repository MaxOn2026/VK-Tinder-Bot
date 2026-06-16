from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    DATABASE = os.getenv('DATABASE')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')

    VK_TOKEN = os.getenv('VK_TOKEN')
    VK_API_VERSION = ''

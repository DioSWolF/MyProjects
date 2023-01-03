import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage



bot_id = ""
token = ""      


bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())

save_image_folder = r"./save_data/image_list/"

db_folder = r"sqlite:///./database/anime_bd.db"


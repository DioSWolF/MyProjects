import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage



bot_id = ""
token = ""      


bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())


save_image_folder = r"./save_data/image_list/"
<<<<<<< HEAD:SerialBot/config/bot_token.py

db_folder = r"sqlite:///./database/anime_bd.db"
=======
>>>>>>> 30f24587c6cb47aa78245572f548567a829e1f83:SerialBot/bot_token.py

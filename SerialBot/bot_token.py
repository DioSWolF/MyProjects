import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage



bot_id = ""
token = ""      


bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())

find_anime_link = f"https://your_site.us/search/anime?q="
find_anime_num_page = "&type=list&page="
find_new_anime_link = "https://your_site.ua"

save_image_folder = r"./image_list/"

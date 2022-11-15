import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage



bot_id = 5604497270
token = ""      


bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())

find_anime_link = f"https://animego.org/search/anime?q="
find_anime_num_page = "&type=list&page="
find_new_anime_link = "https://animego.org"

# save_image_folder = r"/home/diosvolk/save_data/image_list/"
# save_file_folder = r"/home/diosvolk/save_data/save_bin_file/"
save_image_folder = r"./image_list/"
save_file_folder = r"./save_bin_file/"

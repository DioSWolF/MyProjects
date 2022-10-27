import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage

bot_id = int
token = ""      # test bot

# token = ""      # work bot
bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())

find_anime_link = f"https://********?q="
find_anime_num_page = "&type=list&page="
find_new_anime_link = "https://**********/"



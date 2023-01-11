import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage



bot_id = "{id}"
token = "{Token}"      

contact_me = "DioSWolF"

bot_id = {int}
         
bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())

db_folder = r"sqlite:///{file_name}"
save_image_folder = r"{Folder for image save}"

server_time = 1

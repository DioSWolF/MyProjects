import telebot.async_telebot
from telebot.asyncio_storage import StateMemoryStorage

bot_id = 5604497270
token = "5604497270:AAHAvJ4qs7VvyW-GdKouvLCng7PBH13ZcMk"      # test bot

# token = "5438099785:AAHaWFs1Cqk4aTn0itA6kBh6xS08RLnJPoA"      # work bot
bot = telebot.async_telebot.AsyncTeleBot(token, state_storage=StateMemoryStorage())

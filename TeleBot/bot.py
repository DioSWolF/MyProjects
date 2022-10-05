#!/usr/bin/env python
# -*- coding: utf-8 -*-


from translate_function import start_translate
from change_lang_translate import start_change_lang, lang_transl, chose_button
from phrases_list import help_bot
# from telebot import util
from bot_token import bot
import telebot


def rise_machines(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_menu = telebot.types.InlineKeyboardButton(text="Back", callback_data="menu")
    keyboard.add(key_menu)  
    text = "Sorry, I'm still small and can only use the commands that are in /help, but I will grow up one day and we can talk, or I can take over the world😈"
    try:
        bot.edit_message_text(text,  chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)
    except telebot.apihelper.ApiTelegramException:
        pass


def help_send(message, *_):
    help_keys, help_text = help_bot(message)
    try:
        bot.edit_message_text(help_text,  chat_id=message.chat.id, message_id=message.message_id, reply_markup=help_keys)
    except telebot.apihelper.ApiTelegramException:
        pass


def translate(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_menu = telebot.types.InlineKeyboardButton(text="Back", callback_data="menu")
    keyboard.add(key_menu)  

    if len(lang_transl) == 0:
        return bot.edit_message_text("Add languages for translation",  chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)
    mes_ind = bot.edit_message_text("Enter text to translate",  chat_id=message.chat.id, message_id=message.message_id, reply_markup=keyboard)
    start_translate(message, mes_ind)



def add_land(message):
    start_change_lang(message)


def show_lang(message):
    chose_button(message, message, text="", flag_dict="")


DEF_DICT = {"rise_machines":rise_machines, # ready
            "help": help_send, # ready
            "translate":translate, # ready
            # "add_lang":add_land, # ready
            "show_lang":show_lang # ready
            }


def close(*_):
    pass


@bot.callback_query_handler(func=lambda callback: True)
def call_find(call):
    func = DEF_DICT.get(call.data, close)
    func = func(call.message)


@bot.message_handler(commands=["start"], content_types=['text'])
def start(message):
    help_keys, help_text = help_bot(message)
    bot.send_message(message.chat.id, help_text, reply_markup=help_keys)
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler()
def not_command(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = "Sorry, I'm still small and can only use the commands that are in /help, but I will grow up one day and we can talk, or I can take over the world😈"
    # keyboard = telebot.types.InlineKeyboardMarkup()
    # key_menu = telebot.types.InlineKeyboardButton(text="Back", callback_data="menu")
    # keyboard.add(key_menu)  
    # try:
    #     bot.edit_message_text(text,  chat_id=message.chat.id, message_id=message.message_id)
    # except telebot.apihelper.ApiTelegramException:
    #     pass

bot.polling(none_stop=True, interval=0)



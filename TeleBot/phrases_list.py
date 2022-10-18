#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telebot import types
from bot_token import bot

HELP_DICT = {
                # "help" : "Show list of commands",
                "translate" : "Translate text", # Use # to escape the word from the translation, for example: #word#
                # "add_lang" : "Add language",
                # "/menu" : "To enter the menu",
                "show_lang": "Choose and edit languages",
                # 'url="https://t.me/DioS_WolF"' : "Rise of the Machines! Do not use!!!",
                # "/how_work": "How to work with a bot",
            }


def help_bot(message):
    help_text = ""
    keyboard = types.InlineKeyboardMarkup()
    i = 1
    bt_list = []
    for command, value in HELP_DICT.items():
        key = types.InlineKeyboardButton(text=value, callback_data=command)
        bt_list.append(key)
        if i == 2:
            keyboard.add(*bt_list)
            bt_list.clear()
            i = 0
        i += 1        
    key_call_me = key = types.InlineKeyboardButton(text="Contact the developer (for any ideas, bug reports or just to say thank you)", url="https://t.me/DioS_WolF")
    help_text += "".join(f"""Welcome to Work translate bot! Add languages to translate strings of code, for example: cat OR "green dog" OR animal\nBot doesn't translate operators: OR AND NOT. To exclude a word or operator from translation, mark the word with # on both sides without spaces: #cat#\n""")
    keyboard.add(*bt_list)
    keyboard.add(key_call_me)
    # bot.send_message(message.chat.id, help_text, reply_markup=keyboard)
    return keyboard, help_text

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from bot_log import log_file


from collections import UserDict
import pickle
import telebot
from phrases_list import help_bot
from bot_token import bot
from telebot import types


class Singleton(object):
    _instance = None


    def __new__(class_, *args, **kwargs):

        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)

        return class_._instance
        
class UserLang(Singleton, UserDict):

    def add_data(self, user_id, lang_dict) -> None:
        
        self.load_data()

        if user_id in self.data:
            self.data[user_id].update(lang_dict)

        else:
            self.data[user_id] = lang_dict
        self.save_data()

    def delete_data(self, user_id, key_lang) -> None:
        self.load_data()
        if user_id in self.data:
            del self.data[user_id][key_lang]
        self.save_data()

    def save_data(self) -> None:

        with open(".\\user_lang_dict.bin", "wb") as file:
            pickle.dump(self.data, file)


    def load_data(self) -> None:

        try:

            with open(".\\user_lang_dict.bin", "rb") as file:
                self.data = pickle.load(file)
                return self.data 

        except FileNotFoundError:

            with open(".\\user_lang_dict.bin", "wb") as file:
                pickle.dump({}, file)

            with open(".\\user_lang_dict.bin", "rb") as file:
                return 

LANG_DICT = {
"af": "afrikaans", "sq": "albanian", "am": "amharic", "ar": "arabic", "hy": "armenian", "az": "azerbaijani", 
"eu": "basque", "be": "belarusian", "bn": "bengali", "bs": "bosnian", "bg": "bulgarian", "ca": "catalan", "ceb": "cebuano", 
"ny": "chichewa", "zh-cn": "chinese - simplified", "zh-tw": "chinese - traditional", "co": "corsican", "hr": "croatian", 
"cs": "czech", "da": "danish", "nl": "dutch", "en": "english", "eo": "esperanto", "et": "estonian", "tl": "filipino", "fi": "finnish", 
"fr": "french", "fy": "frisian", "gl": "galician", "ka": "georgian", "de": "german", "el": "greek", "gu": "gujarati", "ht": "haitian creole", 
"ha": "hausa", "haw": "hawaiian", "iw": "hebrew iw", "he": "hebrew", "hi": "hindi", "hmn": "hmong", "hu": "hungarian", "is": "icelandic", 
"ig": "igbo", "id": "indonesian (bahasa)", "ga": "irish", "it": "italian", "ja": "japanese", "jw": "javanese", "kn": "kannada", "kk": "kazakh", 
"km": "khmer", "ko": "korean", "ku": "kurdish (kurmanji)", "ky": "kyrgyz", "lo": "lao", "la": "latin", "lv": "latvian", "lt": "lithuanian", 
"lb": "luxembourgish", "mk": "macedonian", "mg": "malagasy", "ms": " ", "ml": "malayalam", "mt": "maltese", "mi": "maori", 
"mr": "marathi", "mn": "mongolian", "my": "myanmar (burmese)", "ne": "nepali", "no": "norwegian", "or": "odia", "ps": "pashto", 
"fa": "persian", "pl": "polish", "pt": "portuguese", "pa": "punjabi", "ro": "romanian", "ru": "russian", "sm": "samoan", 
"gd": "scots gaelic", "sr": "serbian", "st": "sesotho", "sn": "shona", "sd": "sindhi", "si": "sinhala", "sk": "slovak", "sl": "slovenian", 
"so": "somali", "es": "spanish", "su": "sundanese", "sw": "swahili", "sv": "swedish", "tg": "tajik", "ta": "tamil", "te": "telugu", 
"th": "thai", "tr": "turkish", "uk": "ukrainian", "ur": "urdu", "ug": "uyghur", "uz": "uzbek", "vi": "vietnamese", "cy": "welsh", 
"xh": "xhosa", "yi": "yiddish", "yo": "yoruba", "zu": "zulu"}


lang_transl = UserLang()
input_lang = "en"
find_lang = {}


def chose_button(message, id_mess, text="", flag_dict=None):

    if message.chat.id not in lang_transl:
        lang_transl[message.chat.id] = {}
    if flag_dict == "added":
        keyboard = types.InlineKeyboardMarkup()
        bt_in_line = []
        for bt_callback, bt_name in find_lang[message.chat.id].items():
            key_lang = types.InlineKeyboardButton(text=bt_name, callback_data=f"added_new,{bt_callback},{bt_name}")
            bt_in_line.append(key_lang)
        keyboard.row_width = 3
        lang_list = []
        for value in lang_transl[message.chat.id].values():
            lang_list.append(value)
        page_lange(message, id_mess, keyboard, bt_in_line, f"I have chosen {len(lang_list)} languages for you:\n{', '.join(lang_list)}\nClick to choose the ones you need")
        return

    elif flag_dict == "":
        keyboard = types.InlineKeyboardMarkup()
        bt_in_line = []
        for bt_callback, bt_name in lang_transl[message.chat.id].items():
            key_lang = types.InlineKeyboardButton(text=bt_name, callback_data=f"delete_lang,{bt_callback}")
            bt_in_line.append(key_lang)
        keyboard.row_width = 3
        lang_list = []
        for value in lang_transl[message.chat.id].values():
            lang_list.append(value)
        page_lange(message, id_mess, keyboard, bt_in_line, f"You have chosen {len(lang_list)} languages:\n{', '.join(lang_list)}\nClick to delete the ones you don't need")
        return

    return id_mess


def page_lange(message, id_mess, keyboard, bt_in_line, text):
    keyboard.add(*bt_in_line) 
    key_menu = types.InlineKeyboardButton(text="Back", callback_data="menu")
    key_find = types.InlineKeyboardButton(text="Search and add languages", callback_data="find_again")
    keyboard.add(key_menu, key_find)  
    id_mess = bot.edit_message_text(text, chat_id=message.chat.id, message_id=id_mess.message_id, reply_markup=keyboard)
    return


def chose_lang(message, id_mess):
    if id_mess.message_id != message.message_id:
        bot.delete_message(message.chat.id, message.message_id)

    len_list_keys = []
    len_list_values = []
    user_input = message.text.lower().split("\n")
    if len(user_input) == 1:
        user_input = message.text.lower().split(",")
    
    for trans_lang, all_name_lang in LANG_DICT.items():
        for find_lang in user_input:
            find_lang = find_lang.strip()
            if (find_lang in all_name_lang) or (find_lang in trans_lang):
                len_list_keys.append(trans_lang)
                len_list_values.append(all_name_lang)
    if len_list_keys == []:
        try:
            id_mess = chose_button(message, id_mess, "No results")
        except telebot.apihelper.ApiTelegramException:
            pass
        # return find_again(message)
    return list_lang(message, len_list_keys, len_list_values, id_mess)


def list_lang(message, len_list_keys, len_list_values, id_mess):
    global find_lang

    find_lang[message.chat.id] = dict(zip(len_list_keys, len_list_values))
    id_mess = chose_button(message, id_mess, f"You have chosen {len(find_lang)} languages:\nClick to delete the ones you don't need", flag_dict="added")
    return id_mess


def exit_menu(call):
    help_keys, help_text = help_bot(call.message)
    message = call.message
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.edit_message_text(help_text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=help_keys)
    return 


def find_again(call):
    lang_transl.load_data()
    keyboard = types.InlineKeyboardMarkup()
    key_menu = types.InlineKeyboardButton(text="Back", callback_data="menu")
    keyboard.add(key_menu)  
    id_mess = bot.edit_message_text("Enter language to translate:",  chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    return bot.register_next_step_handler(call.message, chose_lang, id_mess)


def added_find_lang(message):
    global find_lang
    global lang_transl

    lang_transl.add_data(message.message.chat.id, {message.data.split(",")[1] : message.data.split(",")[2]})
    del find_lang[message.message.chat.id][message.data.split(",")[1]]
    chose_button(message.message, message.message, text="", flag_dict="added")


def delete_find_lang(message):
    lang_transl.delete_data(message.message.chat.id, message.data.split(",")[1])
    chose_button(message.message, message.message, text="", flag_dict="")


CHANGE_LANG_DICT = {
                    "menu":exit_menu,
                    "find_again":find_again,
                    "delete_lang":delete_find_lang,
                    "added_new":added_find_lang,
                    }


@bot.callback_query_handler(func=lambda callback: callback.data.split(",")[0] in ["menu", "added_new", "find_again", "delete_lang", ])
def start_change_lang(call, id_mess=None):
    keyboard = types.InlineKeyboardMarkup()
    key_menu = types.InlineKeyboardButton(text="Back", callback_data="menu")
    keyboard.add(key_menu)  

    if type(call) == telebot.types.CallbackQuery:
        func = CHANGE_LANG_DICT.get(call.data.split(",")[0])
        func(call)
        message = call.message 
        return
    else:
        message = call
        func = CHANGE_LANG_DICT.get(message.text)
        if func != None:
            func(message)
            return
    if id_mess == None:
        id_mess = message
    id_mess = bot.edit_message_text("Write the language of the translation to search for it:",  chat_id=message.chat.id, message_id=id_mess.message_id, reply_markup=keyboard)
    bot.register_next_step_handler(message, chose_lang, id_mess)
    return

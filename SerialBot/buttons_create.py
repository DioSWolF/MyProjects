from PIL import Image

from telebot.async_telebot import types
from all_classes import Anime, AnimeToday
from singleton_classes import ImageAnimeDict
from bot_token import save_image_folder

def contact_with_me(keyboard):
    key_contact = types.InlineKeyboardButton(text="Contact the developer (for any ideas, bug reports or just to say thank you)", url="https://t.me/DioS_WolF")
    keyboard.add(key_contact)
    return keyboard

def anime_today_buttons(anime_dict: dict[AnimeToday]) -> types.InlineKeyboardMarkup | list[str]:
    keyboard = types.InlineKeyboardMarkup()
    buttons = {}
    bt_list = []
    message_text = []
    
    for anime_today in anime_dict:
  
        message_text.append(f"{anime_today.name.value}\n"\
            f"Series {anime_today.series_number.value}, voice acting: {anime_today.voice_acting.value}\n\n")

        if anime_today.name.value not in buttons:
            buttons[anime_today.name.value] = types.InlineKeyboardButton(text=anime_today.name.value, url=anime_today.page.value)
    for bt in buttons.values():
        bt_list.append(bt)
    keyboard.add(*bt_list)

    return keyboard, message_text


def one_type_buttons_create(dict_functions: dict, byttons_in_row:int, keybord_row: int = 3, callback: str = None):

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = keybord_row
    i = 1
    keys_list = []
    
    for keys, values in dict_functions.items():
        if callback != None:
            values = callback

        key_menu = types.InlineKeyboardButton(text=keys, callback_data=values)
        keys_list.append(key_menu)

        if i == byttons_in_row:
            keyboard.add(*keys_list)  
            keys_list.clear()
            i = 0
        i += 1

    keyboard.add(*keys_list)  
    keys_list.clear()

    return keyboard


def anime_butoons_create(list_objects: list[Anime], callback: str = None, buttons_in_row: int = 3, url: str = None):
    
    keyboard = types.InlineKeyboardMarkup()
    if list_objects == None:
        return keyboard
    keyboard.row_width = buttons_in_row
    keys_list = []
    i = 0
    for objects in list_objects:  
        bt_text = f"{objects.rus_title.value} | {objects.eng_title.value}"

        if url == None:
            key_menu = types.InlineKeyboardButton(text=bt_text, callback_data=f"{callback}#{str(i)}")

        else:
            url_anime = objects.page.value
            key_menu = types.InlineKeyboardButton(text=bt_text, url=url_anime)
        
        keys_list.append(key_menu)
        i += 1

    keyboard.add(*keys_list) 

    keys_list.clear()

    return keyboard


def create_special_buttons(keyboards: types.InlineKeyboardMarkup, dict_keys: dict[str : str]) -> list[types.InlineKeyboardButton]:
    keys_list = []

    for text_bt, callback in dict_keys.items():

        key_add = types.InlineKeyboardButton(text=text_bt, callback_data=callback)
        keys_list.append(key_add)

    keyboards.add(*keys_list)

    return keyboards


def return_anime_dict(anime_dict, num_list = 9):

    dict_anime = {}
    i = 1
    I = 0
    anim_list = []
    for anime in anime_dict:
        anim_list.append(anime)
        if i == num_list:
            dict_anime[I] = anim_list
            anim_list = []
            i = 0
            I += 1
        i += 1
    if anim_list != []:
        dict_anime[len(dict_anime)] = anim_list
        anim_list = []

    return dict_anime


def dump_num(call: types.CallbackQuery, anime_pagin_dict: dict|list, dict_num: int) -> int:
    
    try:
        if call.data.split("|||")[0] == "back_page":
            dict_num -= 1

        elif call.data.split("|||")[0] == "next_page":
            dict_num += 1
    except:
        pass

    if dict_num > len(anime_pagin_dict) - 1:
        dict_num = len(anime_pagin_dict) - 1

    elif 0 > dict_num:
        dict_num = 0

    if dict_num == -1:
        dict_num = 0
        
    return dict_num


def create_image_text_message(anime_list):
    new_list = []
    image_dict = ImageAnimeDict().load_data()
    for anime in anime_list:
        for image_page, image in image_dict.items():
            if anime.image.page == image_page:
                image_and_text = types.InputMediaPhoto(Image.open(f"{save_image_folder}{image.name}"), caption=f"{anime.rus_title.value}\n{anime.eng_title.value}")
                new_list.append(image_and_text)
    return new_list





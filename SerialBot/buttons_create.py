
from telebot.async_telebot import types
from all_classes import Anime
from PIL import Image
from singleton_classes import ImageAnimeDict


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
                image_and_text = types.InputMediaPhoto(Image.open(f".\image\{image.name}"), caption=f"{anime.rus_title.value}\n{anime.eng_title.value}")
                new_list.append(image_and_text)
    return new_list
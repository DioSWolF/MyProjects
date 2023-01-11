#!/usr/bin/env python
# -*- coding: utf-8 -*-


from random import randrange
from PIL import Image
import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from telebot.async_telebot import types
from config.bot_token import contact_me, save_image_folder

from database.mymodels import AnimeDB, AnimeTodayDB, session_db


def contact_with_me(keyboard: types.InlineKeyboardMarkup) -> types.InlineKeyboardMarkup:
    key_contact = types.InlineKeyboardButton(text="Contact the developer (for any ideas, bug reports or just to say thank you)", url=f"https://t.me/{contact_me}")
    keyboard.add(key_contact)
    return keyboard


def anime_today_buttons(anime_dict: dict[AnimeTodayDB]) -> types.InlineKeyboardMarkup | list[str]:
    keyboard = types.InlineKeyboardMarkup()
    buttons = {}
    bt_list = []
    message_text = []

    for anime_today in anime_dict:

        if anime_today.site_name == "anitube":
            edit_text = f"\n{anime_today.eng_name}\n{anime_today.voice_acting}\n"

        else:
            edit_text = f"\n{anime_today.eng_name} | {anime_today.rus_name}\nSeries: {anime_today.series_number}, voice acting: {anime_today.voice_acting}\n"

        message_text.append(edit_text)

        if anime_today.eng_name not in buttons:
            buttons[anime_today.eng_name] = types.InlineKeyboardButton(text=f"{anime_today.eng_name} | {anime_today.rus_name}", url=anime_today.anime_page)

    for bt in buttons.values():
        bt_list.append(bt)
    keyboard.add(*bt_list)

    return keyboard, message_text


def one_type_buttons_create(dict_functions: dict, byttons_in_row:int, keybord_row: int = 3, callback: str = None) -> types.InlineKeyboardMarkup:
    
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


def anime_butoons_create(list_objects: list[AnimeDB], callback: str = None, buttons_in_row: int = 3, url: str = None) -> types.InlineKeyboardMarkup:
    
    keyboard = types.InlineKeyboardMarkup()

    if list_objects == None:
        return keyboard

    keyboard.row_width = buttons_in_row
    keys_list = []
    i = 0
    
    for objects in list_objects:  
        bt_text = f"{objects.eng_title} | {objects.rus_title}"

        if url == None:
            key_menu = types.InlineKeyboardButton(text=bt_text, callback_data=f"{callback}#{str(i)}")

        else:
            url_anime = objects.anime_page
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


async def create_image_text_message(anime_list: list[AnimeDB]) -> list[types.InputMediaPhoto]:
    new_list = []
    for anime in anime_list:
        try:

            image_and_text = types.InputMediaPhoto(Image.open(f"{anime.image_path}{anime.image_name}"), caption=f"{anime.rus_title}\n{anime.eng_title}")
            
        except FileNotFoundError:

            anime = await load_image(anime)

        image_and_text = types.InputMediaPhoto(Image.open(f"{anime.image_path}{anime.image_name}"), caption=f"{anime.rus_title}\n{anime.eng_title}")

        new_list.append(image_and_text)
   
    return new_list



async def load_image(anime: AnimeDB) -> AnimeDB:

    async with aiohttp.ClientSession() as client_session:
        
        headers = {"User-Agent" : UserAgent().random, 
                "Keep-Alive": str(randrange(60, 100)),
                "Connection": "keep-alive"
                }

        async with client_session.request(method="GET", headers=headers, url=anime.image_page) as resp:

            if resp.status == 404:

                async with client_session.request(method="GET", headers=headers, url=anime.anime_page) as resp_img:

                    if resp_img.status == 200:

                        soup = BeautifulSoup(await resp_img.text(), "lxml")
                        soup = soup.select_one(".anime-poster").find("img").get("src")
                        session_db.query(AnimeDB).filter_by(eng_title=anime.eng_title).update(\
                                                            {AnimeDB.image_page : soup}, \
                                                            synchronize_session=False)
                        session_db.commit()
                        anime = session_db.query(AnimeDB).filter_by(eng_title=anime.eng_title, anime_site_link = anime.anime_site_link).first()
                        resp.status = 200

            if resp.status == 200:

                image_path = save_image_folder + anime.anime_site_link + "/" + anime.image_name
                
                async with aiofiles.open(image_path, "wb") as f:

                    await f.write(await resp.read())
                    image_path = save_image_folder + anime.anime_site_link + "/"

                    session_db.query(AnimeDB).filter_by(eng_title=anime.eng_title).update(\
                    {AnimeDB.image_name : anime.image_name,\
                    AnimeDB.image_path : image_path}, \
                    synchronize_session=False)
    
                    session_db.commit()
                    anime = session_db.query(AnimeDB).filter_by(eng_title=anime.eng_title, anime_site_link = anime.anime_site_link).first()
                
        return anime
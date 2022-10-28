#!/usr/bin/env python
# -*- coding: utf-8 -*-


import asyncio
from copy import deepcopy
from datetime import datetime
import aiohttp
import requests
from bs4 import BeautifulSoup
import telebot.async_telebot
from bot_token import find_anime_link, find_anime_num_page, find_new_anime_link

# save data classes
from singleton_classes import ImageAnimeDict, AnimeToChatIdDict, ChatIdToAnimeDict, InfoUserDict
# classes for find function
from all_classes import EngTitleAnime, RusTitleAnime, PageAnime, ImageAnime, Anime, FindAnimeList, FindText
# classes for add-delete functions
from all_classes import IdChat, ChatIdMessage, IdChatUser, JsonChat, InfoChat
# classes for create user info
from all_classes import IdUser, IdUserChat, UserLogin, UserFistName, IsBot, UserLanguage, UserPremium, JsonUserInfo, InfoUser
from fake_useragent import UserAgent


# find anime function

def find_anime_animego(find_text: FindText, find_anime_list: FindAnimeList) -> None:

    page_list = 1
    stop = []
    session = requests.Session()
    
    while stop == []:
        headers = {"User-Agent": UserAgent().random}
        
        find_link = f"{find_anime_link}{find_text}{find_anime_num_page}{page_list}"

        with session.get(find_link, headers=headers) as html_doc:
            soup = BeautifulSoup(html_doc.content, "lxml")

        stop = soup.select(".alert-warning")

        create_anime(find_anime_list, soup)

        page_list += 1

    return


def create_anime(find_anime_list: FindAnimeList, soup: BeautifulSoup) -> None:
    counter = len(find_anime_list)

    for element in soup.select(".animes-grid-item"): 
        eng_title = EngTitleAnime(element)
        rus_title = RusTitleAnime(element)
        page = PageAnime(element)
        image = ImageAnime(element)

        anime = Anime(eng_title, rus_title, page, image,  counter)

        find_anime_list.add_data(anime)

        counter += 1
    return 


async def download_image(image_dict: ImageAnimeDict, find_anime_dict: FindAnimeList) -> None:
    
    image_dict.load_data()
    image_dict.save_data()
    session = requests.Session()
    
    for anime in find_anime_dict:
        headers = {"User-Agent": UserAgent().random}
        if anime.image.page not in image_dict:
            try:
                with session.get(anime.image.page, headers=headers) as save_img:
                    out_img = open(f".\\image\\{anime.image.name}", "wb")
                    out_img.write(save_img.content)
                    out_img.close()     
                    image_dict.add_data(anime)
                    image_dict.save_data() 
            except:
                await asyncio.sleep(3)
                with session.get(anime.image.page) as save_img:
                    out_img = open(f".\\image\\{anime.image.name}", "wb")
                    out_img.write(save_img.content)
                    out_img.close()     
                    image_dict.add_data(anime)
                    image_dict.save_data() 

    return


async def return_find_anime(message: telebot.async_telebot.types.CallbackQuery) -> list[FindAnimeList, ImageAnimeDict]:

    find_text = FindText(message)
    find_anime_dict = FindAnimeList()
    image_dict = ImageAnimeDict()
    find_anime_animego(find_text.value, find_anime_dict)
    await download_image(image_dict, find_anime_dict)

    return_anime_dict = deepcopy(find_anime_dict)
    find_anime_dict.clear()

    return return_anime_dict


# Add-delete anime function (need to update!!!)

def info_chat_create(info_chat: telebot.async_telebot.types.CallbackQuery) -> InfoChat:

    id_chat = IdChat(info_chat)
    message_id = ChatIdMessage(info_chat)
    id_user = IdChatUser(info_chat)
    json_info = JsonChat(info_chat)
    info_chat = InfoChat(id_chat, message_id, id_user, json_info)

    return info_chat


def user_info_create(user_info: telebot.async_telebot.types.CallbackQuery) -> InfoUser:
    save_user = InfoUserDict()

    user_id = IdUser(user_info)
    chat_id = IdUserChat(user_info)
    user_login = UserLogin(user_info)
    user_name = UserFistName(user_info)
    user_is_bot = IsBot(user_info)
    user_lang = UserLanguage(user_info)
    user_prem = UserPremium(user_info)

    user_json = JsonUserInfo(user_info)

    new_user_info = InfoUser(user_id, chat_id, user_login, user_name, user_is_bot, user_lang, user_prem, user_json)

    save_user.add_data(new_user_info)
    return new_user_info


def find_user_info(chat: InfoChat) -> InfoUser:

    save_user = InfoUserDict()
    save_user.load_data()

    return save_user[chat.chat_id.value]


def get_user_bazedata() -> InfoUserDict:
    save_user = InfoUserDict()
    save_user.load_data()
    save_user.save_data()

    return save_user


def add_new_anime_and_user(anime: Anime, user: InfoUser) -> None:
    
    dict_anime_to_chat = AnimeToChatIdDict()
    dict_chatid_to_anime = ChatIdToAnimeDict()
    
    dict_anime_to_chat.add_data(anime, user)
    dict_chatid_to_anime.add_data(anime, user)


def delete_anime_in_chat_id(anime: Anime, user: InfoUser) -> None:

    dict_anime_to_chat = AnimeToChatIdDict()
    dict_chatid_to_anime = ChatIdToAnimeDict()

    dict_anime_to_chat.delete_anime_in_chatid(anime, user)
    dict_chatid_to_anime.delete_chatid_in_anime(anime, user)
    

# Show list anime   ready

def get_list_anime() -> AnimeToChatIdDict:

    dict_anime_to_chat = AnimeToChatIdDict()

    dict_anime_to_chat.load_data()
    dict_anime_to_chat.save_data()

    return dict_anime_to_chat


def return_image_dict()-> list[ImageAnimeDict]:

    image_dict = ImageAnimeDict().load_data()
    return image_dict





async def find_new_seria():
    async with aiohttp.ClientSession() as session:
        async with session.get(find_new_anime_link) as resp:
            print(resp.status)
            print(await resp.text())
















        
parse_telegramm_call = """{'id': '2728426268170004564', 'from_user': {'id': 635261244, 'is_bot': False, 
'first_name': 'Димитрий', 'username': 'Dios_Wolf', 'last_name': None, 'language_code': 'ru', 
'can_join_groups': None, 'can_read_all_group_messages': None, 'supports_inline_queries': None, 
'is_premium': None, 'added_to_attachment_menu': None}, 'message': {'content_type': 'text', 'id': 3782, 
'message_id': 3782, 'from_user': <telebot.async_telebot.types.User object at 0x000001D886D02D70>, 'date': 1665002461, 
'chat': <telebot.async_telebot.types.Chat object at 0x000001D886D02CE0>, 'sender_chat': None, 'forward_from': None, 
'forward_from_chat': None, 'forward_from_message_id': None, 'forward_signature': None, 'forward_sender_name': None, 
'forward_date': None, 'is_automatic_forward': None, 'reply_to_message': None, 'via_bot': None, 'edit_date': 1665427705,
 'has_protected_content': None, 'media_group_id': None, 'author_signature': None, 
 'text': 'Welcome to Work translate bot! Add languages to translate strings of code, for example: cat OR "green dog" OR animal\nBot doesn\'t translate operators: OR AND NOT. To exclude a word or operator from translation, mark the word with # on both sides without spaces: #cat#', 
 'entities': None, 'caption_entities': None, 'audio': None, 'document': None, 'photo': None, 'sticker': None, 
 'video': None, 'video_note': None, 'voice': None, 'caption': None, 'contact': None, 'location': None, 'venue': None, 
 'animation': None, 'dice': None, 'new_chat_member': None, 'new_chat_members': None, 'left_chat_member': None, 
 'new_chat_title': None, 'new_chat_photo': None, 'delete_chat_photo': None, 'group_chat_created': None, 
 'supergroup_chat_created': None, 'channel_chat_created': None, 'migrate_to_chat_id': None, 
 'migrate_from_chat_id': None, 'pinned_message': None, 'invoice': None, 'successful_payment': None, 
 'connected_website': None, 'reply_markup': <telebot.async_telebot.types.InlineKeyboardMarkup object at 0x000001D886D02D10>, 
 'json': {'message_id': 3782, 'from': {'id': 5604497270, 'is_bot': True, 'first_name': 'test_bot', 
 'username': 'dios_test_bot'}, 'chat': {'id': 635261244, 'first_name': 'Димитрий', 'username': 'Dios_Wolf', 
 'type': 'private'}, 'date': 1665002461, 'edit_date': 1665427705, 'text': 'Welcome to Work translate bot! Add languages to translate strings 
of code, for example: cat OR "green dog" OR animal\nBot doesn\'t translate operators: OR AND NOT. To exclude a word or operator from translation, mark the word with # on both sides without spaces: #cat#', 
'reply_markup': {'inline_keyboard': [[{'text': 'Translate text', 'callback_data': 'translate'}, 
{'text': 'Choose and edit languages', 'callback_data': 'show_lang'}], 
[{'text': 'Rise of the Machines! Do not use!!!', 'callback_data': 'rise_machines'}]]}}}, 'inline_message_id': None, 
'chat_instance': '-1291528170873247750', 'data': 'translate', 'game_short_name': None, 
'json': {'id': '2728426268170004564', 'from': {'id': 635261244, 'is_bot': False, 'first_name': 'Димитрий', 
'username': 'Dios_Wolf', 'language_code': 'ru'}, 'message': {'message_id': 3782, 
'from': {'id': 5604497270, 'is_bot': True, 'first_name': 'test_bot', 'username': 'dios_test_bot'}, 
'chat': {'id': 635261244, 'first_name': 'Димитрий', 'username': 'Dios_Wolf', 'type': 'private'}, 
'date': 1665002461, 'edit_date': 1665427705, 'text': 'Welcome to Work translate bot! Add languages to translate strings of code, for example: cat OR "green dog" OR animal\nBot doesn\'t translate operators: OR AND NOT. To exclude a word or operator from translation, mark the word with # on both sides without spaces: #cat#', 
'reply_markup': {'inline_keyboard': [[{'text': 'Translate text', 'callback_data': 'translate'}, 
{'text': 'Choose and edit languages', 'callback_data': 'show_lang'}], 
[{'text': 'Rise of the Machines! Do not use!!!', 'callback_data': 'rise_machines'}]]}}, 
'chat_instance': '-1291528170873247750', 'data': 'translate'}}"""




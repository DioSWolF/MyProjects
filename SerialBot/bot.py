#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot.async_telebot
from random_word import RandomWords
from bot_token import bot
import asyncio
#~~~~~~~~~~~~~~~~~~~~~ create buttons ~~~~~~~~~~~~~~~~~~~~~
from buttons_create import one_type_buttons_create, anime_butoons_create, create_special_buttons, return_anime_dict, dump_num, create_image_text_message
#~~~~~~~~~~~~~~~~~~~~~ bot functions ~~~~~~~~~~~~~~~~~~~~~
from bot_functions import return_find_anime, add_new_anime_and_user, delete_anime_in_chat_id, info_chat_create, user_info_create, get_list_anime, return_image_dict, get_user_bazedata
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.async_telebot import logging

class MyStates(StatesGroup):
    find_text = State()


functions_ready = {
                    "find anime" : "ready",
                        "~add anime in list" : "ready", 
                    "show anime list" : "",
                        "~ delete anime in list" : "nead to update", 
                    "find new series" : "", 
                    "choice push" : "", 
                        "~ mute" : "",
                        "~ when find new series push user" : "",
                        "~ choice push time" : "",
                            "~~ add new  push time" : "",
                            "~~ change push time" : "", 
                            "~~ delete push time" : ""
}



#~~~~~~~~~~~~~~~~~~~~~ get close function ~~~~~~~~~~~~~~~~~~~~~ ready

async def close(*_):
    pass


#~~~~~~~~~~~~~~~~~~~~~ callback_functions ~~~~~~~~~~~~~~~~~~~~~

@bot.message_handler(commands=["start"], content_types=['text'])
@bot.callback_query_handler(func=lambda callback: True)
async def call_find(call):

    try:
        func = DICT_FUNC_WORK.get(call.data.split("#")[0], close)
    
    except AttributeError:

        func = DICT_FUNC_WORK.get(call.text, close)

        user_bazedata = get_user_bazedata()

        if call.chat.id not in user_bazedata and call.from_user.id != 5604497270:
            user_info_create(call)

    await func(call)


#~~~~~~~~~~~~~~~~~~~~~ find anime to user list ~~~~~~~~~~~~~~~~~~~~~   ready

# global anime list

ANIME_FIND_DICT = {}
DICT_NUM_FIND = {}
FIND_ANIME_DICT_PAGINATION = {}
MEDIA_MESSAGE_ID = {}

# start find


async def find_anime(call: telebot.async_telebot.types.CallbackQuery) -> None:

    try:
        message = call.message
    except AttributeError:
        message = call

    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION
    
    user_bazedata = get_user_bazedata()

    chat_info = info_chat_create(message)
    user_id = user_bazedata[chat_info.chat_id.value].user_id.value

    ANIME_FIND_DICT[chat_info.chat_id.value] = []
    FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value] = []
    DICT_NUM_FIND[chat_info.chat_id.value] = 0

    if chat_info.chat_id.value not in DICT_NUM_FIND:
        DICT_NUM_FIND[chat_info.chat_id.value] = 0

    edit_text = "Write text to find anime"

    keyboard = one_type_buttons_create(FUNC_BACK_DICT, 2)

    await bot.set_state(user_id, MyStates.find_text, message.chat.id)
    await bot.edit_message_text(edit_text, chat_id=chat_info.chat_id.value, message_id=chat_info.message_id.value, reply_markup=keyboard)

    return 


# find and get anime list
@bot.message_handler(state=MyStates.find_text)
async def get_find_list_anime(call, callback: telebot.async_telebot.types.CallbackQuery = None) -> None:
    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION
    global MEDIA_MESSAGE_ID


    if type(call) == list:
        call = call[0]

    try:
        message = call.message
    except AttributeError:
        message = call

    chat_info = info_chat_create(message)

    if callback == None:
        callback = call

    if chat_info.chat_id.value not in ANIME_FIND_DICT:
        ANIME_FIND_DICT[chat_info.chat_id.value] = []
        FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value] = []
        DICT_NUM_FIND[chat_info.chat_id.value] = 0

    if len(ANIME_FIND_DICT[chat_info.chat_id.value]) == 0:
        ANIME_FIND_DICT[chat_info.chat_id.value] = return_find_anime(message)
        FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[chat_info.chat_id.value])

    if len(ANIME_FIND_DICT[chat_info.chat_id.value]) == 0:
        return find_anime(callback)

    DICT_NUM_FIND[chat_info.chat_id.value] = dump_num(callback, FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value], DICT_NUM_FIND[chat_info.chat_id.value])

    keyboard = anime_butoons_create(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]], url="")

    spec_dict = {"Back" : "back", "Add series" : "change_buttons_add_new", "Find again" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value]) > 1:
        navig_bt = {"Back page":"back_page|||find", "Next page":"next_page|||find"}
        keyboard = create_special_buttons(keyboard, navig_bt)
   
    try:
        for mes_id in MEDIA_MESSAGE_ID[chat_info.chat_id.value]:
            
            await bot.delete_message(chat_id=chat_info.chat_id.value, message_id=mes_id.message_id)

    except KeyError:
        pass
    image_text_message = create_image_text_message(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]])
    
    edit_text = f"We find {len(ANIME_FIND_DICT[chat_info.chat_id.value])} anime.\n\nClick on button to open website anime\nPage №{DICT_NUM_FIND[chat_info.chat_id.value] + 1}"
    
    MEDIA_MESSAGE_ID[chat_info.chat_id.value] = await bot.send_media_group(chat_id=chat_info.chat_id.value, media=image_text_message)
    message_id = await bot.send_message(chat_id=chat_info.chat_id.value, text=edit_text, reply_markup=keyboard)

    MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(message_id)

    return  



#~~~~~~~~~~~~~~~~~~~~~ add anime to user list ~~~~~~~~~~~~~~~~~~~~~   ready

#create add buttons

async def change_buttons_add_new(call):
    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION

    message = call.message
    
    chat_info = info_chat_create(message)

    DICT_NUM_FIND[chat_info.chat_id.value] = dump_num(call, FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value], DICT_NUM_FIND[chat_info.chat_id.value])

    keyboard = anime_butoons_create(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]], callback="add_new")

    spec_dict = {"Back" : "get_find_list_anime", "Find again" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value]) > 1:
        navig_bt = {"Back page":"back_page|||change_add", "Next page":"next_page|||change_add"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    anime_list = []
    for anime in FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]]:
        anime_list.append(f"{anime.rus_title.value}\n{anime.eng_title.value}\n\n")

    edit_text = f"We find {len(ANIME_FIND_DICT[chat_info.chat_id.value])} anime.\n\n{''.join(anime_list)}Click on button to add anime in your list\nPage №{DICT_NUM_FIND[chat_info.chat_id.value] + 1}"
    try:
        for mes_id in MEDIA_MESSAGE_ID[chat_info.chat_id.value]:
            await bot.delete_message(chat_id=chat_info.chat_id.value, message_id=mes_id.message_id)
    except KeyError:
        pass
    image_text_message = create_image_text_message(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]])
    
    edit_text = f"We find {len(ANIME_FIND_DICT[chat_info.chat_id.value])} anime.\n\nClick on button to open website anime\nPage №{DICT_NUM_FIND[chat_info.chat_id.value] + 1}"
    
    MEDIA_MESSAGE_ID[chat_info.chat_id.value] = await bot.send_media_group(chat_id=chat_info.chat_id.value, media=image_text_message)
    message_id = await bot.send_message(chat_id=chat_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(message_id)
 
 
async def add_anime_in_list(call):
    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION

    message = call.message
    chat_info = info_chat_create(message)

    FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[chat_info.chat_id.value])

    DICT_NUM_FIND[chat_info.chat_id.value] = dump_num(call, FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value], DICT_NUM_FIND[chat_info.chat_id.value])

    spec_dict = {"Back" : "get_find_list_anime", "Find again" : "find_anime"}


    for anime in FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]]:
        anime_indx = FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]].index(anime)

        try:
            if call.data.split("#")[1] == str(anime_indx):
                for anime_save in ANIME_FIND_DICT[chat_info.chat_id.value]:
                    if anime_save.eng_title.value == anime.eng_title.value:
                        add_new_anime_and_user(anime_save, chat_info)
                        index_anime_save = ANIME_FIND_DICT[chat_info.chat_id.value].index(anime_save)
                        ANIME_FIND_DICT[chat_info.chat_id.value].pop(index_anime_save)
                FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]].pop(anime_indx)
        except IndexError:
            pass

    FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[chat_info.chat_id.value])

    if DICT_NUM_FIND[chat_info.chat_id.value] >= len(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value]):
        DICT_NUM_FIND[chat_info.chat_id.value] = dump_num(call, FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value], DICT_NUM_FIND[chat_info.chat_id.value])

    if len(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value]) == 0:
        rand_word = RandomWords()
        message.text = rand_word.get_random_word()[0:3]
        ANIME_FIND_DICT[chat_info.chat_id.value] = return_find_anime(message)
        FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[chat_info.chat_id.value])
        return await get_find_list_anime(message, callback=call)

    keyboard = anime_butoons_create(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]], callback="add_new")
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value]) > 1:
        navig_bt = {"Back page":"back_page|||add", "Next page":"next_page|||add"}
        keyboard = create_special_buttons(keyboard, navig_bt)    
    
    anime_list = []
    for anime in FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]]:
        anime_list.append(f"{anime.rus_title.value}\n{anime.eng_title.value}\n\n")

    edit_text = f"We find {len(ANIME_FIND_DICT[chat_info.chat_id.value])} anime.\n\n{''.join(anime_list)}Click on button to add it in list\nPage №{DICT_NUM_FIND[chat_info.chat_id.value] + 1}"
    try:
        for mes_id in MEDIA_MESSAGE_ID[chat_info.chat_id.value]:
            await bot.delete_message(chat_id=chat_info.chat_id.value, message_id=mes_id.message_id)
    except KeyError:
        pass
    image_text_message = create_image_text_message(FIND_ANIME_DICT_PAGINATION[chat_info.chat_id.value][DICT_NUM_FIND[chat_info.chat_id.value]])
    
    edit_text = f"We find {len(ANIME_FIND_DICT[chat_info.chat_id.value])} anime.\n\nClick on button to open website anime\nPage №{DICT_NUM_FIND[chat_info.chat_id.value] + 1}"
    
    MEDIA_MESSAGE_ID[chat_info.chat_id.value] = await bot.send_media_group(chat_id=chat_info.chat_id.value, media=image_text_message)
    message_id = await bot.send_message(chat_id=chat_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(message_id)

    return

#~~~~~~~~~~~~~~~~~~~~~ send push ~~~~~~~~~~~~~~~~~~~~~   nees update

async def time_send_push(call):
    message = call.message
    send_text = "need text in send push function"

    chat_info = info_chat_create(message)
    
    await bot.send_message(chat_info.chat_id.value, send_text)  
    return



#~~~~~~~~~~~~~~~~~~~~~ back button ~~~~~~~~~~~~~~~~~~~~~ ready

async def back_callback(call):
    global ANIME_FIND_DICT
    try:
        message = call.message
    except AttributeError:
        message = call

    chat_info = info_chat_create(message)
    ANIME_FIND_DICT[chat_info.chat_id.value] = []

    edit_text = "need text in start back button function "

    keyboard = one_type_buttons_create(DEF_DICT, 3)
    user_bazedata = get_user_bazedata()
    user_id = user_bazedata[chat_info.chat_id.value].user_id.value

    await bot.delete_state(user_id, chat_info.chat_id.value)

    await bot.edit_message_text(edit_text, chat_id=chat_info.chat_id.value, message_id=chat_info.message_id.value, reply_markup=keyboard)

    return 


#~~~~~~~~~~~~~~~~~~~~~ /start bot ~~~~~~~~~~~~~~~~~~~~~ ready

async def start(message):
    edit_text = "You wrote f*cking shit"

    chat_info = info_chat_create(message)
    keyboard = one_type_buttons_create(DEF_DICT, 3)
    
    mes_id = await bot.send_message(chat_info.chat_id.value, edit_text, reply_markup=keyboard)
    try:
        MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(mes_id)
    except KeyError:
        MEDIA_MESSAGE_ID[chat_info.chat_id.value] = [mes_id]
    await bot.delete_message(chat_info.chat_id.value, chat_info.message_id.value)
    return


#~~~~~~~~~~~~~~~~~~~~~ delete strange message ~~~~~~~~~~~~~~~~~~~~~ ready

@bot.message_handler()
async def delete_message(message):

    chat_info = info_chat_create(message)
    user_bazedata = get_user_bazedata()

    user_id = user_bazedata[chat_info.chat_id.value].user_id.value

    await bot.delete_message(chat_info.chat_id.value, chat_info.message_id.value)

    return


#~~~~~~~~~~~~~~~~~~~~~ show list ~~~~~~~~~~~~~~~~~~~~~ ready

ANIME_SHOW_PAGIN_DICT = {}
DICT_NUM = {}

async def start_show_list_anime(call):
    global ANIME_SHOW_PAGIN_DICT
    global DICT_NUM

    message = call.message
    chat_info = info_chat_create(message)
    anime_list_in_chatid = get_list_anime()

    try:    
        if chat_info.chat_id.value not in anime_list_in_chatid:
            return 
    except TypeError:
        return   
    if chat_info.chat_id.value not in DICT_NUM:
        DICT_NUM[chat_info.chat_id.value] = 0

    ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value] = ""
    chat_anime = anime_list_in_chatid[chat_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value] = return_anime_dict(chat_anime)

    DICT_NUM[chat_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value], DICT_NUM[chat_info.chat_id.value])
    
    spec_dict = {"Back" : "back", "Delete my anime" : "change_buttons_delete", "Find new anime": "find_anime"}

    if len(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value]) == 0:
        return

    keyboard = anime_butoons_create(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]], url="")
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value]) > 1:
        navig_bt = {"Back page":"back_page|||show", "Next page":"next_page|||show"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    edit_text = f"You have {len(chat_anime)} anime.\n\nClick on button to open website anime\n Page №{DICT_NUM[chat_info.chat_id.value] + 1}"
    try:
        for mes_id in MEDIA_MESSAGE_ID[chat_info.chat_id.value]:
            await bot.delete_message(chat_id=chat_info.chat_id.value, message_id=mes_id.message_id)
    except KeyError:
        pass
    image_text_message = create_image_text_message(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]])
    
    
    MEDIA_MESSAGE_ID[chat_info.chat_id.value] = await bot.send_media_group(chat_id=chat_info.chat_id.value, media=image_text_message)
    message_id = await bot.send_message(chat_id=chat_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(message_id)

    return   


#~~~~~~~~~~~~~~~~~~~~~ delete anime in my list ~~~~~~~~~~~~~~~~~~~~~ ready

# change buttons to delete function

async def change_buttons_delete(call):
    global ANIME_SHOW_PAGIN_DICT
    global DICT_NUM

    message = call.message
    chat_info = info_chat_create(message)

    anime_list_in_chatid = get_list_anime()
    chat_anime = anime_list_in_chatid[chat_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value] = return_anime_dict(chat_anime)

    DICT_NUM[chat_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value], DICT_NUM[chat_info.chat_id.value])

    spec_dict = {"Back" : "show_all", "Find new anime": "find_anime", } 

    keyboard = anime_butoons_create(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]], callback="delete_anime")
    keyboard = create_special_buttons(keyboard, spec_dict)
    if len(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value]) > 1:
        navig_bt = {"Back page":"back_page|||change_delete", "Next page":"next_page|||change_delete"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    edit_text = f"You have {len(chat_anime)} anime.\n\nClick on button to delete anime\nPage №{DICT_NUM[chat_info.chat_id.value] + 1}"
    try:
        for mes_id in MEDIA_MESSAGE_ID[chat_info.chat_id.value]:
            await bot.delete_message(chat_id=chat_info.chat_id.value, message_id=mes_id.message_id)
    except KeyError:
        pass
    image_text_message = create_image_text_message(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]])
    
    
    MEDIA_MESSAGE_ID[chat_info.chat_id.value] = await bot.send_media_group(chat_id=chat_info.chat_id.value, media=image_text_message)
    message_id = await bot.send_message(chat_id=chat_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(message_id)
 
    return  

# delete anime

async def delete_anime(call):
    global ANIME_SHOW_PAGIN_DICT
    global DICT_NUM
    message = call.message

    chat_info = info_chat_create(message)
    anime_list_in_chatid = get_list_anime()
    chat_anime = anime_list_in_chatid[chat_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value] = return_anime_dict(chat_anime)
 
    DICT_NUM[chat_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value], DICT_NUM[chat_info.chat_id.value])
    
    for anime in ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]]:
        index_anime = ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]].index(anime)
        try:
            if call.data.split("#")[1] == str(index_anime):
                for anime_save in chat_anime:
                    if anime_save.eng_title.value == anime.eng_title.value:
                        delete_anime_in_chat_id(anime_save, chat_info)
                        index_anime_save = chat_anime.index(anime_save)
                        chat_anime.pop(index_anime_save)
                ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]].pop(index_anime)
        except IndexError:
            pass

    anime_list_in_chatid = get_list_anime()

    chat_anime = anime_list_in_chatid[chat_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value] = return_anime_dict(chat_anime)
    if  DICT_NUM[chat_info.chat_id.value] >= len(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value]):
        DICT_NUM[chat_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value], DICT_NUM[chat_info.chat_id.value])

    if len(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value]) == 0:
        return await back_callback(call)

    keyboard = anime_butoons_create(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]], callback="delete_anime")
    spec_dict = {"Back" : "show_all", "Find new anime" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value]) > 1:
        navig_bt = {"Back page":"back_page|||delete", "Next page":"next_page|||delete"}
        keyboard = create_special_buttons(keyboard, navig_bt)
    
    edit_text = f"You have {len(chat_anime)} anime.\n\nClick on button to delete anime\nPage №{DICT_NUM[chat_info.chat_id.value] + 1}"
    try:
        for mes_id in MEDIA_MESSAGE_ID[chat_info.chat_id.value]:
            await bot.delete_message(chat_id=chat_info.chat_id.value, message_id=mes_id.message_id)
    except KeyError:
        pass
    image_text_message = create_image_text_message(ANIME_SHOW_PAGIN_DICT[chat_info.chat_id.value][DICT_NUM[chat_info.chat_id.value]])
    
    
    MEDIA_MESSAGE_ID[chat_info.chat_id.value] = await bot.send_media_group(chat_id=chat_info.chat_id.value, media=image_text_message)
    message_id = await bot.send_message(chat_id=chat_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[chat_info.chat_id.value].append(message_id)
    
    return


#~~~~~~~~~~~~~~~~~~~~~ dicts for buttons ~~~~~~~~~~~~~~~~~~~~~ nees update

DICT_FUNC_WORK = {  
                    "/start" : start,
                    "back" : back_callback, 
                    # find buttons
                    "find_anime": find_anime, 
                    "get_find_list_anime" : get_find_list_anime,

                    # # need add functions
                    # "find_new_series" : "",
                    # "selected_pushtime_" : "",

                    # add buttons  
                    "change_buttons_add_new" : change_buttons_add_new,
                    "add_new" : add_anime_in_list,

                    # show buttons
                    "show_all" : start_show_list_anime,

                    # delete buttons 
                    "delete_anime" : delete_anime,
                    "change_buttons_delete" : change_buttons_delete,

                    # navigations buttons
                    "back_page|||show": start_show_list_anime,
                    "next_page|||show" : start_show_list_anime,

                    "back_page|||change_delete" : change_buttons_delete, 
                    "next_page|||change_delete" : change_buttons_delete, 

                    "back_page|||delete" : delete_anime,
                    "next_page|||delete" : delete_anime,

                    "back_page|||find" : get_find_list_anime,
                    "next_page|||find" : get_find_list_anime,  

                    "back_page|||change_add" : change_buttons_add_new,
                    "next_page|||change_add" : change_buttons_add_new,

                    "back_page|||add" : add_anime_in_list,
                    "next_page|||add" : add_anime_in_list,
                }


DEF_DICT = {
            "Find anime" : "find_anime",                               # need to update
            "Show my anime list" : "show_all",                     # need to add
            "Find new series(CRASHED)" : "find_new_series",                        # need to add
            "Choice time to send push(CRASHED)" : "selected_pushtime_",                # need to add
            }


FUNC_BACK_DICT =    {
                    "Back" : "back"
                    }



from telebot import asyncio_filters
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
asyncio.run(bot.polling(none_stop=True, interval=0))

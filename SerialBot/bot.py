#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot.async_telebot
from random_word import RandomWords
from bot_token import bot, bot_id
import asyncio
#~~~~~~~~~~~~~~~~~~~~~ create buttons ~~~~~~~~~~~~~~~~~~~~~
from buttons_create import one_type_buttons_create, anime_butoons_create, create_special_buttons, return_anime_dict, dump_num, create_image_text_message, anime_today_buttons, contact_with_me
#~~~~~~~~~~~~~~~~~~~~~ bot functions ~~~~~~~~~~~~~~~~~~~~~
from bot_functions import return_find_anime, add_new_anime_and_user, delete_anime_in_chat_id, info_chat_create, user_info_create, get_list_anime, get_user_bazedata, find_user_info, send_anime_today
#~~~~~~~~~~~~~~~~~~~~~ state class ~~~~~~~~~~~~~~~~~~~~~
from push_while_true import find_new_anime_today
from all_classes import MyStates 
from telebot import asyncio_filters

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

        if call.chat.id not in user_bazedata and call.from_user.id != bot_id:
            user_info_create(call)

    await func(call)


#~~~~~~~~~~~~~~~~~~~~~ find anime to user list ~~~~~~~~~~~~~~~~~~~~~   ready

# global anime list

ANIME_FIND_DICT = {}
DICT_NUM_FIND = {}
FIND_ANIME_DICT_PAGINATION = {}
MEDIA_MESSAGE_ID = {}


async def find_anime(call: telebot.async_telebot.types.CallbackQuery) -> None:

    try:
        message = call.message
    except AttributeError:
        message = call

    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION

    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    ANIME_FIND_DICT[user_info.chat_id.value] = []
    FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = []
    DICT_NUM_FIND[user_info.chat_id.value] = 0

    if user_info.chat_id.value not in DICT_NUM_FIND:
        DICT_NUM_FIND[user_info.chat_id.value] = 0

    edit_text = f"{user_info.user_name.value}-san, enter the name of the anime and I will find it for you!"

    keyboard = one_type_buttons_create(FUNC_BACK_DICT, 2)

    await bot.set_state(user_info.user_id.value, MyStates.find_text, message.chat.id)
    
    await asyncio.sleep(0.5)
    
    await bot.edit_message_text(edit_text, chat_id=user_info.chat_id.value, message_id=chat_info.message_id.value, reply_markup=keyboard)

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
    user_info = find_user_info(chat_info)

    for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:  

        try:
            await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
        except:
            pass

    if callback == None:
        callback = call

    if user_info.chat_id.value not in ANIME_FIND_DICT:
        ANIME_FIND_DICT[user_info.chat_id.value] = []
        FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = []
        DICT_NUM_FIND[user_info.chat_id.value] = 0

    if len(ANIME_FIND_DICT[user_info.chat_id.value]) == 0:
        ANIME_FIND_DICT[user_info.chat_id.value] = await return_find_anime(message)
        FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[user_info.chat_id.value])

    if len(ANIME_FIND_DICT[user_info.chat_id.value]) == 0:
        rand_word = RandomWords()
        message.text = rand_word.get_random_word()[0:3]
        
        ANIME_FIND_DICT[user_info.chat_id.value] = await return_find_anime(message)
        FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[user_info.chat_id.value])
        # return find_anime(callback)

    DICT_NUM_FIND[user_info.chat_id.value] = dump_num(callback, FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value], DICT_NUM_FIND[user_info.chat_id.value])

    keyboard = anime_butoons_create(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]], url="")

    spec_dict = {"Back" : "back", "Add series to your anime list" : "change_buttons_add_new", "Search again" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value]) > 1:
        navig_bt = {"Previous page":"back_page|||find", "Next page":"next_page|||find"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    image_text_message = create_image_text_message(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]])
    
    edit_text = f"{user_info.user_name.value}-san, I have found {len(ANIME_FIND_DICT[user_info.chat_id.value])} anime for you!\n\nClick the button to open anime on website\nPage №{DICT_NUM_FIND[user_info.chat_id.value] + 1}/{len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value])}"
    
    MEDIA_MESSAGE_ID[user_info.chat_id.value] = await bot.send_media_group(chat_id=user_info.chat_id.value, media=image_text_message)
    
    await asyncio.sleep(0.5)
    
    message_id = await bot.send_message(chat_id=user_info.chat_id.value, text=edit_text, reply_markup=keyboard)

    MEDIA_MESSAGE_ID[user_info.chat_id.value].append(message_id)

    return  



#~~~~~~~~~~~~~~~~~~~~~ add anime to user list ~~~~~~~~~~~~~~~~~~~~~   ready

#create add buttons

async def change_buttons_add_new(call):
    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION

    message = call.message
    
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:

        try:
            await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
        except:
            pass

    DICT_NUM_FIND[user_info.chat_id.value] = dump_num(call, FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value], DICT_NUM_FIND[user_info.chat_id.value])

    keyboard = anime_butoons_create(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]], callback="add_new")

    spec_dict = {"Back" : "get_find_list_anime", "Search again" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value]) > 1:
        navig_bt = {"Previous page":"back_page|||change_add", "Next page":"next_page|||change_add"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    anime_list = []
    for anime in FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]]:
        anime_list.append(f"{anime.rus_title.value}\n{anime.eng_title.value}\n\n")
    
    image_text_message = create_image_text_message(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]])
    
    edit_text = f"{user_info.user_name.value}-san, I have found {len(ANIME_FIND_DICT[user_info.chat_id.value])} anime for you!\n\nClick to add series to your anime list\nPage №{DICT_NUM_FIND[user_info.chat_id.value] + 1}/{len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value])}"
    
    MEDIA_MESSAGE_ID[user_info.chat_id.value] = await bot.send_media_group(chat_id=user_info.chat_id.value, media=image_text_message)
    
    await asyncio.sleep(0.5)
    
    message_id = await bot.send_message(chat_id=user_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[user_info.chat_id.value].append(message_id)
 
 
async def add_anime_in_list(call):
    global ANIME_FIND_DICT
    global DICT_NUM_FIND
    global FIND_ANIME_DICT_PAGINATION

    message = call.message
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[user_info.chat_id.value])

    DICT_NUM_FIND[user_info.chat_id.value] = dump_num(call, FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value], DICT_NUM_FIND[user_info.chat_id.value])

    spec_dict = {"Back" : "get_find_list_anime", "Search again" : "find_anime"}

    
    for anime in FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]]:
        anime_indx = FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]].index(anime)

        try:
            if call.data.split("#")[1] == str(anime_indx):
                for anime_save in ANIME_FIND_DICT[user_info.chat_id.value]:
                    if anime_save.eng_title.value == anime.eng_title.value:
                        user_info = find_user_info(user_info)
                        add_new_anime_and_user(anime_save, user_info)
                        index_anime_save = ANIME_FIND_DICT[user_info.chat_id.value].index(anime_save)
                        ANIME_FIND_DICT[user_info.chat_id.value].pop(index_anime_save)
                FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]].pop(anime_indx)
        except IndexError:
            pass

    FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[user_info.chat_id.value])

    if DICT_NUM_FIND[user_info.chat_id.value] >= len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value]):
        DICT_NUM_FIND[user_info.chat_id.value] = dump_num(call, FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value], DICT_NUM_FIND[user_info.chat_id.value])

    if len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value]) == 0:

        for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:  
            try:

                await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
            except:
                pass

        rand_word = RandomWords()
        message.text = rand_word.get_random_word()[0:3]
        
        ANIME_FIND_DICT[user_info.chat_id.value] = await return_find_anime(message)
        FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value] = return_anime_dict(ANIME_FIND_DICT[user_info.chat_id.value])
        
        return await get_find_list_anime(message, callback=call)

    keyboard = anime_butoons_create(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]], callback="add_new")
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value]) > 1:
        navig_bt = {"Previous page":"back_page|||add", "Next page":"next_page|||add"}
        keyboard = create_special_buttons(keyboard, navig_bt)    
    
    anime_list = []
    for anime in FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]]:
        anime_list.append(f"{anime.rus_title.value}\n{anime.eng_title.value}\n\n")
    
    for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:

        try:
            await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
        except:
            pass

    image_text_message = create_image_text_message(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value][DICT_NUM_FIND[user_info.chat_id.value]])
    
    edit_text = f"{user_info.user_name.value}-san, I have found {len(ANIME_FIND_DICT[user_info.chat_id.value])} anime for you!\n\n{''.join(anime_list)}Click to add series to your anime list\nPage №{DICT_NUM_FIND[user_info.chat_id.value] + 1}/{len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id.value])}"
    
    MEDIA_MESSAGE_ID[user_info.chat_id.value] = await bot.send_media_group(chat_id=user_info.chat_id.value, media=image_text_message)
    
    await asyncio.sleep(0.5)

    message_id = await bot.send_message(chat_id=user_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[user_info.chat_id.value].append(message_id)

    return


#~~~~~~~~~~~~~~~~~~~~~ back button ~~~~~~~~~~~~~~~~~~~~~ ready

async def back_callback(call):
    global ANIME_FIND_DICT
    try:
        message = call.message
    except AttributeError:
        message = call

    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    ANIME_FIND_DICT[chat_info.chat_id.value] = []

    edit_text = f"\nIrasshaimase, {user_info.user_name.value}-san!"

    keyboard = one_type_buttons_create(DEF_DICT, 3)

    keyboard = contact_with_me(keyboard)

    await bot.delete_state(user_info.user_id.value, user_info.chat_id.value)
    await bot.edit_message_text(edit_text, chat_id=user_info.chat_id.value, message_id=chat_info.message_id.value, reply_markup=keyboard)

    return 


#~~~~~~~~~~~~~~~~~~~~~ /start bot ~~~~~~~~~~~~~~~~~~~~~ ready

async def start(message):
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    edit_text = f"\nIrasshaimase, {user_info.user_name.value}-san!"

    keyboard = one_type_buttons_create(DEF_DICT, 3)
    keyboard = contact_with_me(keyboard)

    mes_id = await bot.send_message(user_info.chat_id.value, edit_text, reply_markup=keyboard)

    try:
        MEDIA_MESSAGE_ID[user_info.chat_id.value].append(mes_id)
    except KeyError:
        MEDIA_MESSAGE_ID[user_info.chat_id.value] = [mes_id]

    try:
        await bot.delete_message(user_info.chat_id.value, chat_info.message_id.value)
    except:
        pass
    return


#~~~~~~~~~~~~~~~~~~~~~ delete strange message ~~~~~~~~~~~~~~~~~~~~~ ready

@bot.message_handler()
async def delete_message(message):

    chat_info = info_chat_create(message)
    try:
        await bot.delete_message(chat_info.chat_id.value, chat_info.message_id.value)
    except:
        pass
    return


#~~~~~~~~~~~~~~~~~~~~~ show list ~~~~~~~~~~~~~~~~~~~~~ ready

ANIME_SHOW_PAGIN_DICT = {}
DICT_NUM = {}

async def start_show_list_anime(call):
    global ANIME_SHOW_PAGIN_DICT
    global DICT_NUM

    message = call.message
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    anime_list_in_chatid = get_list_anime()

    try:    
        if user_info.chat_id.value not in anime_list_in_chatid:
            return 
    except TypeError:
        return   


    for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:
        try:
            await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
        except:
            pass

    if user_info.chat_id.value not in DICT_NUM:
        DICT_NUM[user_info.chat_id.value] = 0

    ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value] = ""
    chat_anime = anime_list_in_chatid[user_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value] = return_anime_dict(chat_anime)

    if len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value]) == 0:
        return

    DICT_NUM[user_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value], DICT_NUM[user_info.chat_id.value])
    
    spec_dict = {"Back" : "back", "Delete series from your anime list" : "change_buttons_delete", "Search for new anime": "find_anime"}

    keyboard = anime_butoons_create(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]], url="")
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value]) > 1:
        navig_bt = {"Previous page":"back_page|||show", "Next page":"next_page|||show"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    edit_text = f"{user_info.user_name.value}-san, you have {len(chat_anime)} anime.\n\nClick the button to open anime on website\n Page №{DICT_NUM[user_info.chat_id.value] + 1}/{len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value])}"
    
    image_text_message = create_image_text_message(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]])
    
    MEDIA_MESSAGE_ID[user_info.chat_id.value] = await bot.send_media_group(chat_id=user_info.chat_id.value, media=image_text_message)
    
    await asyncio.sleep(0.5)

    message_id = await bot.send_message(chat_id=user_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[user_info.chat_id.value].append(message_id)

    return   


#~~~~~~~~~~~~~~~~~~~~~ delete anime in my list ~~~~~~~~~~~~~~~~~~~~~ ready

# change buttons to delete function

async def change_buttons_delete(call):
    global ANIME_SHOW_PAGIN_DICT
    global DICT_NUM

    message = call.message
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:
        try:
            await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
        except:
            pass

    anime_list_in_chatid = get_list_anime()
    chat_anime = anime_list_in_chatid[user_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value] = return_anime_dict(chat_anime)

    DICT_NUM[user_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value], DICT_NUM[user_info.chat_id.value])

    spec_dict = {"Back" : "show_all", "Search for new anime": "find_anime", } 

    keyboard = anime_butoons_create(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]], callback="delete_anime")
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value]) > 1:
        navig_bt = {"Previous page":"back_page|||change_delete", "Next page":"next_page|||change_delete"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    edit_text = f"{user_info.user_name.value}-san, you have {len(chat_anime)} anime.\n\nClick to delete series from your anime list\nPage №{DICT_NUM[user_info.chat_id.value] + 1}/{len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value])}"

    image_text_message = create_image_text_message(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]])
    
    MEDIA_MESSAGE_ID[user_info.chat_id.value] = await bot.send_media_group(chat_id=user_info.chat_id.value, media=image_text_message)
    
    await asyncio.sleep(0.5)

    message_id = await bot.send_message(chat_id=user_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[user_info.chat_id.value].append(message_id)
 
    return  


# delete anime

async def delete_anime(call):
    global ANIME_SHOW_PAGIN_DICT
    global DICT_NUM
    message = call.message

    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    anime_list_in_chatid = get_list_anime()
    
    chat_anime = anime_list_in_chatid[user_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value] = return_anime_dict(chat_anime)
 
    DICT_NUM[user_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value], DICT_NUM[user_info.chat_id.value])
    
    for anime in ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]]:
        index_anime = ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]].index(anime)
        try:
            if call.data.split("#")[1] == str(index_anime):
                for anime_save in chat_anime:
                    if anime_save.eng_title.value == anime.eng_title.value:
                        user_info = find_user_info(chat_info)
                        delete_anime_in_chat_id(anime_save, user_info)
                        index_anime_save = chat_anime.index(anime_save)
                        chat_anime.pop(index_anime_save)
                ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]].pop(index_anime)
        except IndexError:
            pass

    anime_list_in_chatid = get_list_anime()

    chat_anime = anime_list_in_chatid[user_info.chat_id.value]["anime_list"]

    ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value] = return_anime_dict(chat_anime)
    if  DICT_NUM[user_info.chat_id.value] >= len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value]):
        DICT_NUM[user_info.chat_id.value] = dump_num(call, ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value], DICT_NUM[user_info.chat_id.value])

    if len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value]) == 0:
        return await back_callback(call)

    keyboard = anime_butoons_create(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]], callback="delete_anime")
    spec_dict = {"Back" : "show_all", "Search for new anime" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value]) > 1:
        navig_bt = {"Previous page":"back_page|||delete", "Next page":"next_page|||delete"}
        keyboard = create_special_buttons(keyboard, navig_bt)
    
    edit_text = f"{user_info.user_name.value}-san, you have {len(chat_anime)} anime.\n\nClick to delete series from your anime list\nPage №{DICT_NUM[user_info.chat_id.value] + 1}/ {len(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value])}"

    for mes_id in MEDIA_MESSAGE_ID[user_info.chat_id.value]:
        
        try:
            await bot.delete_message(chat_id=user_info.chat_id.value, message_id=mes_id.message_id)
        except:
            pass

    image_text_message = create_image_text_message(ANIME_SHOW_PAGIN_DICT[user_info.chat_id.value][DICT_NUM[user_info.chat_id.value]])
    
    MEDIA_MESSAGE_ID[user_info.chat_id.value] = await bot.send_media_group(chat_id=user_info.chat_id.value, media=image_text_message)
   
    await asyncio.sleep(0.5)

    message_id = await bot.send_message(chat_id=user_info.chat_id.value, text=edit_text, reply_markup=keyboard)
    MEDIA_MESSAGE_ID[user_info.chat_id.value].append(message_id)
    
    return


#~~~~~~~~~~~~~~~~~~~~~ send anime list today to user ~~~~~~~~~~~~~~~~~~~~~ 
show_list = {}
message_id_pagin = {}
message_id_pagin_delete = {}

async def send_anime_today_message(call):
    global show_list
    global message_id_pagin

    message = call.message
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)

    if call.data.split("|||")[0] == "find_new_series":
        show_list[user_info.chat_id.value] = 0 

    anime_dict = await send_anime_today()

    if len(anime_dict) <= 1:
        return
        
    try:
        await bot.delete_message(chat_id=user_info.chat_id.value, message_id=message_id_pagin[user_info.chat_id.value])
        index =  message_id_pagin_delete[user_info.chat_id.value].index(message_id_pagin[user_info.chat_id.value])
        message_id_pagin_delete[user_info.chat_id.value].pop(index)
    except:
        pass

    del anime_dict["time_date"]
    
    anime_list = []
    for anime_today in anime_dict.values():
        anime_list.append(anime_today)

    anime_pagin = return_anime_dict(anime_list[::-1])

    show_list[user_info.chat_id.value] = dump_num(call, anime_pagin, show_list[user_info.chat_id.value])
    keyboard, message_text = anime_today_buttons(anime_pagin[show_list[user_info.chat_id.value]])

    if len(anime_pagin) > 1:
        navig_bt = {"Previous page":"back_page|||find_new_series", "Next page":"next_page|||find_new_series"}
        keyboard = create_special_buttons(keyboard, navig_bt) 
          
    del_bt = {"Delete message" :"delete_all_push_mes"}
    keyboard = create_special_buttons(keyboard, del_bt)   

    edit_text = f"{user_info.user_name.value}-san, you have {len(anime_dict)} anime.\n\n{''.join(message_text)}Page №{show_list[user_info.chat_id.value] + 1}/{len(anime_pagin)}"

    message_id = await bot.send_message(user_info.user_id.value, edit_text, reply_markup=keyboard)

    message_id_pagin[user_info.chat_id.value] = message_id.message_id
    if user_info.chat_id.value not in message_id_pagin_delete:
        message_id_pagin_delete[user_info.chat_id.value] = [message_id.message_id]
    else:
        message_id_pagin_delete[user_info.chat_id.value].append(message_id.message_id)

    return 


async def delete_all_push_mes(call):
    global message_id_pagin_delete
    message = call.message
    chat_info = info_chat_create(message)
    user_info = find_user_info(chat_info)
    for mes_id in message_id_pagin_delete[user_info.chat_id.value]:
        try:
            await bot.delete_message(user_info.chat_id.value, mes_id)
            message_id_pagin_delete[user_info.chat_id.value] = []
            del message_id_pagin[user_info.chat_id.value]
        except:
            pass
  
    return 

#~~~~~~~~~~~~~~~~~~~~~ dicts for buttons ~~~~~~~~~~~~~~~~~~~~~ nees update

DICT_FUNC_WORK = {  
                    "/start" : start,
                    "back" : back_callback, 
                    # find buttons
                    "find_anime": find_anime, 
                    "get_find_list_anime" : get_find_list_anime,

                    # # need add functions
                    "find_new_series" : send_anime_today_message,
                    "delete_all_push_mes" : delete_all_push_mes,
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
                    "back_page|||find_new_series" : send_anime_today_message,
                    "next_page|||find_new_series" : send_anime_today_message,
                }


DEF_DICT = {
            "Search anime" : "find_anime",                               # need to update
            "Show my anime list" : "show_all",                     # need to add
            "Show ongoing anime series" : "find_new_series",                        # need to add
            # "Choice time to send push(NOT WORCKED)" : "selected_pushtime_",                # need to add
            }


FUNC_BACK_DICT =    {
                    "Back" : "back"
                    }





async def main():
    futures = [bot.polling(none_stop=True, interval=0), find_new_anime_today()]
    await asyncio.gather(*futures)

    
if __name__ == '__main__':
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    asyncio.run(main())

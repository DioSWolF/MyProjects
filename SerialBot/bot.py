#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telebot.types import CallbackQuery
from telebot import asyncio_filters

import asyncio

from buttons_create import one_type_buttons_create, anime_butoons_create, create_special_buttons, create_image_text_message, anime_today_buttons, contact_with_me

from push_func.push_while_true import find_new_anime_today
from parse.find_anime import MyStates 

from classes.bot_query import AnimeToUser, PaginFindAnime, QueryAnime, ShowUserList
from classes.user_info import QueryUserInfo
from classes.message import MessageDeleteId
from classes.push_query import QueryAnimeToday
from classes.analitic import AnaliticClickData
from classes.error_decorator import ChangeSubscription

from config.bot_token import bot
from config.search_dicts import BT_DICT, SITE_FLAG


#~~~~~~~~~~~~~~~~~~~~~ get close function ~~~~~~~~~~~~~~~~~~~~~ ready

async def close(*_) -> None:
    pass


#~~~~~~~~~~~~~~~~~~~~~ callback_functions ~~~~~~~~~~~~~~~~~~~~~


@bot.message_handler(commands=["start"], content_types=['text'])
@bot.callback_query_handler(func=lambda callback: True)
@AnaliticClickData
@ChangeSubscription
async def call_find(call: CallbackQuery) -> None:
    
    try:
        func = DICT_FUNC_WORK.get(call.data.split("#")[0], close)

    except AttributeError:
        func = DICT_FUNC_WORK.get(call.text, close)

    await func(call)


#~~~~~~~~~~~~~~~~~~~~~ /start bot ~~~~~~~~~~~~~~~~~~~~~ ready


async def change_search_site(call: CallbackQuery) -> None:
    try:
        message = call.message
    except AttributeError:
        message = call

    user_query = QueryUserInfo(message)
    user_info = user_query.get_user()
    
    if len(call.data.split("#")) >= 2:
        user_query.change_user_site(call.data.split("#")[1])
        user_info = user_query.get_user()
    
    edit_text = f"You have chosen site: {SITE_FLAG[user_info.chose_site]}\nChange anime source?"

    keyboard = one_type_buttons_create(BT_DICT, 1)

    await bot.edit_message_text(edit_text, chat_id=user_info.chat_id, message_id=message.id, reply_markup=keyboard)



async def start(message: CallbackQuery) -> None:

    try:
        message = message.message
    except AttributeError:
        message = message

    user_query = QueryUserInfo(message)
    user_info = user_query.get_user()

    message_delete = MessageDeleteId()

    if user_query.user_info == None:
        user_query.add_new_user()
        user_info = user_query.get_user()

#!
    edit_text = f"\n{SITE_FLAG[user_info.chose_site]}Irasshaimase, {user_info.user_name}-san!{SITE_FLAG[user_info.chose_site]}"

    keyboard = one_type_buttons_create(DEF_DICT, 3)
    keyboard = contact_with_me(keyboard)
#^
    message_info = await bot.send_message(user_info.chat_id, edit_text, reply_markup=keyboard)

    message_delete.add_message_id(user_info, message_info)
    await message_delete.safe_message_delete(user_info, message)

    return


#~~~~~~~~~~~~~~~~~~~~~ back button ~~~~~~~~~~~~~~~~~~~~~ ready

async def back_callback(call: CallbackQuery) -> None:

    try:
        message = call.message
    except AttributeError:
        message = call

    user_query = QueryUserInfo(message)
    user_info = user_query.get_user()
   
    message_delete = MessageDeleteId()
    await message_delete.special_delete(user_info, 0, -1)
#!
    edit_text = f"\n{SITE_FLAG[user_info.chose_site]}Irasshaimase, {user_info.user_name}-san!{SITE_FLAG[user_info.chose_site]}"

    keyboard = one_type_buttons_create(DEF_DICT, 3)
    keyboard = contact_with_me(keyboard)
#^
    await bot.delete_state(user_info.user_id, user_info.chat_id)
    await bot.edit_message_text(edit_text, chat_id=user_info.chat_id, message_id=message.id, reply_markup=keyboard)

    # await bot.edit_message_text(edit_text, chat_id=user_info.chat_id, message_id=chat_info.message_id.value, reply_markup=keyboard)
    return 


#~~~~~~~~~~~~~~~~~~~~~ find anime to user list ~~~~~~~~~~~~~~~~~~~~~   ready


async def find_anime(call: CallbackQuery) -> None:

    try:
        message = call.message
    except AttributeError:
        message = call
    
    user_query = QueryUserInfo(message)
    user_info = user_query.get_user()
    
    message_delete = MessageDeleteId()

    await message_delete.special_delete(user_info, 0, -1)
#!
    edit_text = f"{user_info.user_name}-san, enter the name of the anime and I will find it for you!"
    keyboard = one_type_buttons_create(FUNC_BACK_DICT, 2)
#^
    await bot.set_state(user_info.user_id, MyStates.find_text, message.chat.id)
    await asyncio.sleep(0.5)

    await bot.edit_message_text(edit_text, chat_id=user_info.chat_id, message_id=message.id, reply_markup=keyboard)

    # await bot.edit_message_text(edit_text, chat_id=user_info.chat_id, message_id=chat_info.message_id.value, reply_markup=keyboard)
    
    return 


# find and get anime list
@bot.message_handler(state=MyStates.find_text)
async def get_find_list_anime(call: CallbackQuery, callback: CallbackQuery = None) -> None:

    if type(call) == list:
        call = call[0]

    try:
        message = call.message
        call_data = call.data
    except AttributeError:
        message = call
        call_data = ""
    
    user_query = QueryUserInfo(message)
    query_anime = QueryAnime()
    pagin_anime = PaginFindAnime()
    message_delete = MessageDeleteId()

    user_info = user_query.get_user()

    await message_delete.delete_message_list(user_info)

    pagin_anime.add_num_pagin(user_info)
    try:
        anime_list = pagin_anime.get_anime_list(user_info)
    except:
        return
    if callback == None:
        callback = call
    
    if call_data == "":
        await query_anime.find_anime(message, user_info)
        anime_list = pagin_anime.get_anime_list(user_info)

        while len(anime_list) == 0:
            await query_anime.find_random_anime()
            anime_list = pagin_anime.get_anime_list(user_info)

    anime_pagin_dict = pagin_anime.get_pagin_anime_dict(user_info)
    dump_num = pagin_anime.dump_num(callback, user_info, anime_pagin_dict)
#!!!
    keyboard = anime_butoons_create(anime_pagin_dict[dump_num], url="")

    spec_dict = {"Back" : "back", "Add series to your anime list" : "change_buttons_add_new", "Search again" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||find", "Next page":"next_page|||find"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    image_text_message = await create_image_text_message(anime_pagin_dict[dump_num])

    edit_text = f"{user_info.user_name}-san, I have found {len(anime_list)} anime for you!\n\nClick the button to open anime on website\nPage №{dump_num + 1}/{len(anime_pagin_dict)}"
#^^^
    mes_id = await bot.send_media_group(chat_id=user_info.chat_id, media=image_text_message)
    message_delete.add_message_id(user_info, mes_id)
    
    await asyncio.sleep(0.5)
    
    mes_id = await bot.send_message(chat_id=user_info.chat_id, text=edit_text, reply_markup=keyboard)
    message_delete.add_message_id(user_info, mes_id)
    return  



#~~~~~~~~~~~~~~~~~~~~~ add anime to user list ~~~~~~~~~~~~~~~~~~~~~   ready

#create add buttons

async def change_buttons_add_new(call: CallbackQuery) -> None:
    message = call.message

    user_query = QueryUserInfo(message)
    pagin_anime = PaginFindAnime()
    message_delete = MessageDeleteId()

    user_info = user_query.get_user()
    
    await message_delete.delete_message_list(user_info)

    anime_pagin_dict = pagin_anime.get_pagin_anime_dict(user_info)
    anime_list = pagin_anime.get_anime_list(user_info)
    dump_num = pagin_anime.dump_num(call, user_info, anime_pagin_dict)

#!!!
    keyboard = anime_butoons_create(anime_pagin_dict[dump_num], callback="add_new")

    spec_dict = {"Back" : "get_find_list_anime", "Search again" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||change_add", "Next page":"next_page|||change_add"}
        keyboard = create_special_buttons(keyboard, navig_bt)
    
    image_text_message = await  create_image_text_message(anime_pagin_dict[dump_num])
    
    edit_text = f"{user_info.user_name}-san, I have found {len(anime_list)} anime for you!\n\nClick to add series to your anime list\nPage №{dump_num + 1}/{len(anime_pagin_dict)}"
#^^^
    mes_id = await bot.send_media_group(chat_id=user_info.chat_id, media=image_text_message)
    message_delete.add_message_id(user_info, mes_id)
    
    await asyncio.sleep(0.5)

    mes_id = await bot.send_message(chat_id=user_info.chat_id, text=edit_text, reply_markup=keyboard)
    message_delete.add_message_id(user_info, mes_id)

    return

 
async def add_anime_in_list(call: CallbackQuery) -> None:
    message = call.message

    user_query = QueryUserInfo(message)
    message_delete = MessageDeleteId()
    pagin_anime = PaginFindAnime()
    user_to_anime = AnimeToUser()
    query_anime = QueryAnime()

    user_info = user_query.get_user()

    anime_pagin_dict = pagin_anime.get_pagin_anime_dict(user_info)
    dump_num = pagin_anime.dump_num(call, user_info, anime_pagin_dict)

    try:
        anime_index = int(call.data.split("#")[1])
        anime = anime_pagin_dict[dump_num][anime_index]
        user_to_anime.add_anime_user(user_info, anime)
        pagin_anime.del_anime_in_pagin(user_info, anime)

    except IndexError:
        pass

    anime_pagin_dict = pagin_anime.get_pagin_anime_dict(user_info)

    if dump_num >= len(anime_pagin_dict):
        dump_num = pagin_anime.dump_num(call, user_info, anime_pagin_dict)

    if len(anime_pagin_dict) == 0:
        await message_delete.delete_message_list(user_info)
        await query_anime.find_random_anime(message, user_info)

        anime_list = pagin_anime.get_anime_list(user_info)
        anime_pagin_dict = pagin_anime.get_pagin_anime_dict(user_info)

        return await get_find_list_anime(message, callback=call) 
#!!!
    spec_dict = {"Back" : "get_find_list_anime", "Search again" : "find_anime"}
    keyboard = anime_butoons_create(anime_pagin_dict[dump_num], callback="add_new")
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||add", "Next page":"next_page|||add"}
        keyboard = create_special_buttons(keyboard, navig_bt)    
    
    anime_list = pagin_anime.get_anime_list(user_info)
    await message_delete.delete_message_list(user_info)

    image_text_message = await  create_image_text_message(anime_pagin_dict[dump_num])
    
    # edit_text = f"{user_info.user_name.value}-san, I have found {len(ANIME_FIND_DICT[user_info.chat_id])} anime for you!\n\n{''.join(anime_list)}Click to add series to your anime list\nPage №{DICT_NUM_FIND[user_info.chat_id] + 1}/{len(FIND_ANIME_DICT_PAGINATION[user_info.chat_id])}"
    edit_text = f"{user_info.user_name}-san, I have found {len(anime_list)} anime for you!\n\nClick to add series to your anime list\nPage №{dump_num + 1}/{len(anime_pagin_dict)}"
#^^^  
    mes_id = await bot.send_media_group(chat_id=user_info.chat_id, media=image_text_message)
    message_delete.add_message_id(user_info, mes_id)

    await asyncio.sleep(0.5)

    mes_id = await bot.send_message(chat_id=user_info.chat_id, text=edit_text, reply_markup=keyboard)
    message_delete.add_message_id(user_info, mes_id)

    return


#~~~~~~~~~~~~~~~~~~~~~ show list ~~~~~~~~~~~~~~~~~~~~~ ready


async def start_show_list_anime(call: CallbackQuery) -> None:
    message = call.message

    user_query = QueryUserInfo(message)
    message_delete = MessageDeleteId()
    show_user_anime_query = ShowUserList()

    user_info = user_query.get_user()
    show_user_anime_query.add_pagin_num(user_info)
    anime_list = show_user_anime_query.get_anime_list(user_info)

    if len(anime_list) == 0:
        return
    
    await message_delete.delete_message_list(user_info)
    
    anime_pagin_dict = show_user_anime_query.get_pagin_anime_dict(user_info)

    dump_num = show_user_anime_query.dump_num(call, user_info, anime_pagin_dict)
#!!!
    spec_dict = {"Back" : "back", "Delete series from your anime list" : "change_buttons_delete", "Search for new anime": "find_anime"}
    keyboard = anime_butoons_create(anime_pagin_dict[dump_num], url="")
    keyboard = create_special_buttons(keyboard, spec_dict)

    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||show", "Next page":"next_page|||show"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    edit_text = f"{user_info.user_name}-san, you have {len(anime_list)} anime.\n\nClick the button to open anime on website\n Page №{dump_num + 1}/{len(anime_pagin_dict)}"
  
    image_text_message = await create_image_text_message(anime_pagin_dict[dump_num])
#^^^
    mes_id = await bot.send_media_group(chat_id=user_info.chat_id, media=image_text_message)
    message_delete.add_message_id(user_info, mes_id)

    await asyncio.sleep(0.5)

    mes_id = await bot.send_message(chat_id=user_info.chat_id, text=edit_text, reply_markup=keyboard)
    message_delete.add_message_id(user_info, mes_id)

    return   


#~~~~~~~~~~~~~~~~~~~~~ delete anime in my list ~~~~~~~~~~~~~~~~~~~~~ ready

# change buttons to delete function

async def change_buttons_delete(call: CallbackQuery) -> None:
    message = call.message

    user_query = QueryUserInfo(message)
    show_user_anime_query = ShowUserList()
    message_delete = MessageDeleteId()

    user_info = user_query.get_user()

    await message_delete.delete_message_list(user_info)

    anime_list = show_user_anime_query.get_anime_list(user_info)
    anime_pagin_dict = show_user_anime_query.get_pagin_anime_dict(user_info)

    dump_num = show_user_anime_query.dump_num(call, user_info, anime_pagin_dict)
#!!!
    spec_dict = {"Back" : "show_all", "Search for new anime": "find_anime", } 
    keyboard = anime_butoons_create(anime_pagin_dict[dump_num], callback="delete_anime")
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||change_delete", "Next page":"next_page|||change_delete"}
        keyboard = create_special_buttons(keyboard, navig_bt)

    edit_text = f"{user_info.user_name}-san, you have {len(anime_list)} anime.\n\nClick to delete series from your anime list\nPage №{dump_num + 1}/{len(anime_pagin_dict)}"

    image_text_message = await create_image_text_message(anime_pagin_dict[dump_num])
#^^^
    mes_id = await bot.send_media_group(chat_id=user_info.chat_id, media=image_text_message)
    message_delete.add_message_id(user_info, mes_id)

    await asyncio.sleep(0.5)

    mes_id = await bot.send_message(chat_id=user_info.chat_id, text=edit_text, reply_markup=keyboard)
    message_delete.add_message_id(user_info, mes_id)
 
    return  


# delete anime

async def delete_anime(call: CallbackQuery) -> None:
    message = call.message

    user_query = QueryUserInfo(message)
    show_user_anime_query = ShowUserList()
    message_delete = MessageDeleteId()
    user_to_anime = AnimeToUser()

    user_info = user_query.get_user()

    anime_list = show_user_anime_query.get_anime_list(user_info)
    anime_pagin_dict = show_user_anime_query.get_pagin_anime_dict(user_info)
    dump_num = show_user_anime_query.dump_num(call, user_info, anime_pagin_dict)

    try:
        anime_index = int(call.data.split("#")[1])
        anime = anime_pagin_dict[dump_num][anime_index]
        user_to_anime.del_anime_user(user_info, anime)

    except IndexError:
        pass
        
    anime_pagin_dict = show_user_anime_query.get_pagin_anime_dict(user_info)
    anime_list = show_user_anime_query.get_anime_list(user_info)
    if dump_num >= len(anime_pagin_dict):
        dump_num = show_user_anime_query.dump_num(call, user_info, anime_pagin_dict)

    if len(anime_pagin_dict) == 0:
        return await back_callback(call)

    keyboard = anime_butoons_create(anime_pagin_dict[dump_num], callback="delete_anime")
    spec_dict = {"Back" : "show_all", "Search for new anime" : "find_anime"}
    keyboard = create_special_buttons(keyboard, spec_dict)
    
    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||delete", "Next page":"next_page|||delete"}
        keyboard = create_special_buttons(keyboard, navig_bt)
    
    edit_text = f"{user_info.user_name}-san, you have {len(anime_list)} anime.\n\nClick to delete series from your anime list\nPage №{dump_num + 1}/ {len(anime_pagin_dict)}"
#^^^
    await message_delete.delete_message_list(user_info)

    image_text_message = await create_image_text_message(anime_pagin_dict[dump_num])
    
    mes_id = await bot.send_media_group(chat_id=user_info.chat_id, media=image_text_message)
    message_delete.add_message_id(user_info, mes_id)

    await asyncio.sleep(0.5)

    mes_id = await bot.send_message(chat_id=user_info.chat_id, text=edit_text, reply_markup=keyboard)
    message_delete.add_message_id(user_info, mes_id)
    
    return


#~~~~~~~~~~~~~~~~~~~~~ send ongoing list today to user ~~~~~~~~~~~~~~~~~~~~~ 

def send_ongoing_list(call: CallbackQuery) -> None:
    message = call.message

    user_query = QueryUserInfo(message)
    message_delete = MessageDeleteId()
    
    user_info = user_query.get_user()


#~~~~~~~~~~~~~~~~~~~~~ send anime list today to user ~~~~~~~~~~~~~~~~~~~~~ 


async def send_anime_today_message(call: CallbackQuery) -> None:

    message = call.message

    user_query = QueryUserInfo(message)
    message_delete = MessageDeleteId()
    animetoday_query = QueryAnimeToday()

    user_info = user_query.get_user()
    anime_list = animetoday_query.all_records_today(user_info)
    animetoday_query.add_num_pagin(user_info)
    anime_pagin_dict = animetoday_query.get_pagin_dict()

    if len(anime_list) < 1:
        return

    await message_delete.del_pg_save_mes(user_info)
#!!!

    dump_num = animetoday_query.dump_num(call, user_info, anime_pagin_dict)

    keyboard, message_text = anime_today_buttons(anime_pagin_dict[dump_num])

    if len(anime_pagin_dict) > 1:
        navig_bt = {"Previous page":"back_page|||find_new_series", "Next page":"next_page|||find_new_series"}
        keyboard = create_special_buttons(keyboard, navig_bt) 

    del_bt = {"Delete message" :"delete_all_push_mes"}
    keyboard = create_special_buttons(keyboard, del_bt)   

    edit_text = f"{user_info.user_name}-san, you have {len(anime_list)} new episodes.\n\n{''.join(message_text)}Page №{dump_num + 1}/{len(anime_pagin_dict)}"
#^^^
    mes_id = await bot.send_message(user_info.user_id, edit_text, reply_markup=keyboard)

    message_delete.add_save_pg_mes_id(user_info, mes_id)
    # message_delete.add_pagin_mes_id(user_info, mes_id)
    return 


async def delete_all_push_mes(call: CallbackQuery) -> None:
    message = call.message

    message_delete = MessageDeleteId()
    user_query = QueryUserInfo(message)

    user_info = user_query.get_user()
    
    await message_delete.delete_pagin_mes_list(user_info, message)

    return 


#~~~~~~~~~~~~~~~~~~~~~ delete strange message ~~~~~~~~~~~~~~~~~~~~~ 

@bot.message_handler()
async def delete_message(message: CallbackQuery) -> None:

    user_query = QueryUserInfo(message)
    user_info = user_query.get_user()

    message_delete = MessageDeleteId()
    await message_delete.safe_message_delete(user_info, message)

    return


#~~~~~~~~~~~~~~~~~~~~~ dicts for buttons ~~~~~~~~~~~~~~~~~~~~~ nees update

DICT_FUNC_WORK = {  
                    "/start" : start,
                    "back" : back_callback, 

                    # find buttons
                    "find_anime": find_anime, 
                    "get_find_list_anime" : get_find_list_anime,
                    "change_search_site" : change_search_site,

                    # need add functions
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
            "Search anime" : "find_anime",                               
            "Show my anime list" : "show_all",                     
            "Show ongoing anime series" : "find_new_series",                        
            "Change anime source" : "change_search_site",                
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

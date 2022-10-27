import asyncio
from telebot.async_telebot import types
from bot_token import find_new_anime_link, bot

import aiohttp
from bs4 import BeautifulSoup

from singleton_classes import AnimeFindToday, ChatIdToAnimeDict
from all_classes import NameFindAnimeToday, SeriesNumberToday, VoiceActingToday, AnimeToday


async def find_new_anime_today() -> None:
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(10)
            async with session.get(find_new_anime_link) as resp:
                
                soup = BeautifulSoup(await resp.text(), "lxml")
                soup = soup.select_one("#slide-toggle-1")

            await create_new_anime_today(soup)
            user_push_dict = await create_message_text_dict()
            await send_push_message(user_push_dict)
            

async def create_new_anime_today(anime_today_list: BeautifulSoup) -> None:
    anime_list = []

    for element in anime_today_list:
        anime_name = NameFindAnimeToday(element)
        series_num = SeriesNumberToday(element)
        voice_acting = VoiceActingToday(element)

        find_anime = AnimeToday(anime_name, series_num, voice_acting)
        anime_list.append(find_anime)
        
    anime_save = AnimeFindToday()
    anime = ChatIdToAnimeDict().load_data()
    
    anime_save.load_data()
    await anime_save.add_data(anime_list, anime)
    anime_save.clean_data()

    return


async def create_message_text_dict() -> dict[int : str]:

    anime_save = AnimeFindToday()
    anime = ChatIdToAnimeDict()
    anime_save.load_data()
    anime.load_data()

    user_push_dict = {}

    for key, value in anime_save.items():
        if key != "time_date":
            for anime_name, anime_info in anime.items():
                if (value["anime"] != None) and (value["anime"].eng_title.value == anime_name) and (value["push_flag"] != True):
                    for user in anime_info["info_chat"]:

                        anime_save.change_push_flag(value["anime_today"])

                        message_text = (f"{value['anime'].rus_title.value} | {value['anime'].eng_title.value} "\
                            f"\nSeries {value['anime_today'].series_number.value}, voice acting: {value['anime_today'].voice_acting.value}\n\n")

                        button_text = f"{value['anime'].rus_title.value} | {value['anime'].eng_title.value}"
                        button_url = value['anime'].page.value

                        if user.user_id.value not in user_push_dict:
                            user_push_dict[user.user_id.value] = {"anime" : ["You have new series:\n\n", message_text], "keyboard_keys" : {button_text : button_url}}
                        
                        else:
                            user_push_dict[user.user_id.value]["anime"].append(message_text)
                            user_push_dict[user.user_id.value]["keyboard_keys"].update({button_text : button_url})
    return user_push_dict


async def send_push_message(user_push_dict:dict[int : str]) -> None:
    
    for user_id, message_text in user_push_dict.items():
        by_list = []
        keyboard = types.InlineKeyboardMarkup()

        for bt_text, bt_url in message_text["keyboard_keys"].items():
            button = types.InlineKeyboardButton(text=bt_text, url=bt_url)
            by_list.append(button)

        keyboard.add(*by_list)

        await bot.send_message(user_id, "".join(message_text["anime"]), reply_markup=keyboard)
        await asyncio.sleep(1)
        return 



# async def start_push_while():
#     futures = [bot.polling(none_stop=True, interval=0), find_new_anime_today()]
#     await asyncio.gather(*futures)

# if __name__ == '__main__':  
#     asyncio.run(find_new_anime_today())

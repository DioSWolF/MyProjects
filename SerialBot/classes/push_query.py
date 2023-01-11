#!/usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
from parse.push_user import AnimeToday
from database.mymodels import AnimeDB, AnimeTodayDB, PushUserDB, UserInfoDB, session_db
from config.bot_token import bot, server_time
from telebot.types import CallbackQuery
from telebot.async_telebot import types
from sqlalchemy.exc import InvalidRequestError


class QueryAnimeToday():
    session = session_db
    anime_today_db = AnimeTodayDB
    number_pagin = {}
    list_anime = []
    anime_id_list = []

    def __init__(self, search_key: str = None) -> None:
        self.search_key = search_key
        self.date_now: datetime = (datetime.now() + timedelta(hours=server_time)).date()
        

    def add_num_pagin(self, user_info: UserInfoDB) -> None:
        if user_info.user_id not in self.number_pagin:

            self.number_pagin[user_info.user_id] = 0
            

    def dump_num(self, call: CallbackQuery, user_info: UserInfoDB, anime_pagin_dict: dict|list) -> int:
        dict_num = self.number_pagin[user_info.user_id]

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
 

        self.number_pagin[user_info.user_id] = dict_num

        return self.number_pagin[user_info.user_id]
    

    def add_new_record(self, anime: AnimeToday) -> None:
        
        if (self.query_animeid(anime=anime)) and (anime.anime_id not in self.anime_id_list):
            
            db_anime = self.anime_today_db(anime_id=anime.anime_id, rus_name=anime.name.value, \
                                    eng_name=anime.eng_name.value, series_number=anime.series_number.value,\
                                    voice_acting=anime.voice_acting.value, anime_page=anime.page.value, \
                                    update_date=anime.date_now, site_name = anime.search_key) 
                                    
            self.anime_id_list.append(anime.anime_id)
            self.list_anime.insert(0, db_anime)


    def all_animeid_today(self) -> None:
        db_list = self.session.query(self.anime_today_db.anime_id).filter_by(site_name=self.search_key).all()  
        db_list = list([anime_id[0] for anime_id in db_list])
        self.db_list: list[str] = db_list[::-1]


    def all_records_today(self, user_info: UserInfoDB) -> list[AnimeToday]:
        db_list_all = self.session.query(self.anime_today_db).filter_by(site_name=user_info.chose_site).all()
        self.db_list_all: list[AnimeToday] = db_list_all[::-1]

        return self.db_list_all


    def query_animeid(self, anime: AnimeToday):
        find_anime_id = self.session.query(self.anime_today_db).filter_by(anime_id=anime.anime_id).first()

        if find_anime_id == None:
            return True

        return False


    def commit_new_records(self) -> None:
        try:
            if self.list_anime != []:
                self.session.add_all(self.list_anime)
            self.session.commit()
        except InvalidRequestError:
            self.session.commit()


    def clean_records(self) -> None:
        # await bot.send_message(chat_id=635261244, text=self.date_now)
        self.session.query(AnimeTodayDB).filter(AnimeTodayDB.update_date != self.date_now).delete()
        self.session.commit()


    def get_pagin_dict(self, num_list: int = 9) -> dict[int : [list[AnimeToday]]]:
        dict_anime = {}
        i = 1
        I = 0
        anim_list = []

        for anime in self.db_list_all:
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

        self.pagin_dict: dict[int : [list[AnimeToday]]] = dict_anime
        return self.pagin_dict


class PushAnimeToday():
    push_user_model = PushUserDB
    anime_today_model = AnimeTodayDB
    anime_model = AnimeDB
    session = session_db
    date_now: datetime = (datetime.now() + timedelta(hours=server_time)).date()
    user_list = None


    def create_push_record(self) -> None:
        self._del_old_push()
        self._get_all_anime_today()
        for anime in self.anime_today:
            check_push_rec = self._check_push_record(anime)

            if check_push_rec == None:
                self._get_user_list(anime)
                self._create_text_push(anime)
                
                if self.user_list != None:
                    for user_info in self.user_list:
                        new_record = self.push_user_model(user_id=user_info.user_id, anime_id=anime.anime_id, anime_name=anime.eng_name + " | " + anime.rus_name, \
                                                        update_date=self.date_now, anime_page=anime.anime_page, message_text=self.push_text)
                        self.session.add(new_record)
                        self.session.commit()


    def _check_push_record(self, anime: AnimeTodayDB) -> PushUserDB:
        check_push_recod = self.session.query(self.push_user_model).filter_by(anime_id=anime.anime_id).first()
        return check_push_recod


    def _create_text_push(self, anime: AnimeTodayDB) -> None:
        if anime.site_name == "animego":
            self.push_text = f"You have new series:\n{anime.eng_name} | {anime.rus_name} \nSeries: {anime.series_number}, Voice acting: {anime.voice_acting}\n\n"
        if anime.site_name == "anitube":
            self.push_text = f"You have new series:\n{anime.eng_name}\nEpisode: {anime.series_number}\n, Voice acting: {anime.voice_acting}\n\n"
        if anime.site_name == "hdrezka":
            self.push_text = f"You have new series:\n{anime.eng_name}\nEpisode: {anime.series_number}\n, Voice acting: {anime.voice_acting}\n\n"


    def _get_user_list(self, anime: AnimeTodayDB) -> None:
        anime_find: AnimeDB = self.session.query(self.anime_model).filter_by(eng_title=anime.eng_name, anime_site_link = anime.site_name).first()  

        if anime_find != None:
            self.user_list: list[UserInfoDB]|None = anime_find.user_info_list_t
        else:
            self.user_list = None


    def _get_all_anime_today(self) -> None:
        self.anime_today: list[AnimeTodayDB] = self.session.query(self.anime_today_model).all()


    def _del_old_push(self) -> None:
        self.session.query(self.push_user_model).filter(self.push_user_model.update_date!=self.date_now).delete()
        self.session.commit()


class SendPush():
    session = session_db
    push_user_model = PushUserDB
    bot_cls = bot


    def _get_push_list(self) -> None:
        self.push_list: list[PushUserDB] = self.session.query(self.push_user_model).filter_by(push_flag=False).all()


    def _create_button(self, push: PushUserDB) -> None:
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text=push.anime_name, url=push.anime_page)
        keyboard.add(button)
        self.keyboard = keyboard


    def _change_flag(self, push_rec: PushUserDB) -> None:
        self.session.query(self.push_user_model).filter_by(id=push_rec.id).update({self.push_user_model.push_flag : True}, synchronize_session=False)
        self.session.commit()
    
    
    async def send_push_user(self) -> None:
        self._get_push_list()
        for push in self.push_list:
            self._create_button(push)
            await self.bot_cls.send_message(push.user_id, push.message_text, reply_markup=self.keyboard)
            self._change_flag(push)


        



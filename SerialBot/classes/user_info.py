#!/usr/bin/env python
# -*- coding: utf-8 -*-


from config.bot_token import bot_id
from database.mymodels import session_db, UserInfoDB
from parse.user_info import IdUser, IdUserChat, UserFistName, UserLogin, UserLanguage, IsBot, UserPremium, InfoUser
from telebot.types import Message


class QueryUserInfo():
    session = session_db
    user_info_model = UserInfoDB


    def __init__(self, message: Message) -> None:
        self.message = message


    def _parse_user_info(self) -> None:

        user_id = IdUser(self.message).value
        chat_id = IdUserChat(self.message).value
        user_login = UserLogin(self.message).value
        user_name = UserFistName(self.message).value
        user_is_bot = IsBot(self.message).value
        user_lang = UserLanguage(self.message).value
        user_prem = UserPremium(self.message).value
        
        user_info = InfoUser(user_id, chat_id, user_login, user_name, user_is_bot, user_lang, user_prem)

        self.parse_user = user_info


    def _add_user_info(self) -> None:

        user_query = self.session.query(self.user_info_model).filter_by(user_id=self.parse_user.user_id).first()

        if user_query == None and self.parse_user.user_id != bot_id:

            self.user_info = self.user_info_model(user_id=self.parse_user.user_id, chat_id=self.parse_user.chat_id, user_login=self.parse_user.user_login, \
                                user_name=self.parse_user.user_name, is_bot=self.parse_user.is_bot, language_code=self.parse_user.language_code,\
                                is_premium=self.parse_user.is_premium)

            self.session.add(self.user_info)
            self.session.commit()


    def add_new_user(self) -> None:
        self._parse_user_info()
        self._add_user_info()
        


    def get_user(self) -> UserInfoDB:
        chat_id = IdUserChat(self.message).value
        self.user_info = self.session.query(self.user_info_model).filter_by(chat_id=chat_id).first()

        return self.user_info


    def change_user_site(self, new_site: str) -> None:
        self.session.query(self.user_info_model).filter_by(user_id=self.user_info.user_id).update({self.user_info_model.chose_site : new_site}, synchronize_session=False)
        self.session.commit()


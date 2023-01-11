#!/usr/bin/env python
# -*- coding: utf-8 -*-


from database.mymodels import UserInfoDB
from telebot.types import Message
from classes.singleton import Singleton
from config.bot_token import bot


class MessageDeleteId(Singleton):
    data = {}
    pagin_data = {}
    pagin_data_save = {}


    def add_message_id(self, user_info: UserInfoDB, message: Message) -> None:
        
        if user_info.user_id not in self.data:
            self.data[user_info.user_id] = [message]
        elif isinstance(message, list):
            self.data[user_info.user_id].extend(message)
        else:
            self.data[user_info.user_id].append(message)


    def message_list(self, user_info: UserInfoDB) -> list[Message]:
        return self.data[user_info.user_id]
        

    async def delete_message_list(self, user_info: UserInfoDB) -> None:
        if user_info.user_id in self.data:
            for mes_id in self.data[user_info.chat_id]:  

                try:
                    await bot.delete_message(chat_id=user_info.chat_id, message_id=mes_id.message_id)

                except:
                    pass
            self.data[user_info.chat_id] = []


    async def safe_message_delete(self, user_info: UserInfoDB, message: Message) -> None:
        try:
            await bot.delete_message(chat_id=user_info.chat_id, message_id=message.message_id)
        except:
            pass
    

    async def special_delete(self, user_info: UserInfoDB, start_num: int = 0, end_num: int = -1) -> None:
        if user_info.user_id in self.data:
            for mes_id in self.data[user_info.chat_id][start_num : end_num]:  
                try:
                    await bot.delete_message(chat_id=user_info.chat_id, message_id=mes_id.message_id)
                    index_mes = self.data[user_info.chat_id].index(mes_id)
                    self.data[user_info.chat_id].pop(index_mes)
                except:
                    pass


    def add_pagin_mes_id(self, user_info: UserInfoDB, message: Message) -> None:
        if user_info.user_id not in self.pagin_data:
            self.pagin_data[user_info.user_id] = [message]
        else:
            self.pagin_data[user_info.user_id].append(message)
    

    async def delete_pagin_mes_list(self, user_info: UserInfoDB, message) -> None:

        # try:
        #     for mes_id in self.pagin_data[user_info.chat_id]:  
            
        #         await bot.delete_message(chat_id=user_info.chat_id, message_id=mes_id.message_id)
        #         index_mes = self.pagin_data[user_info.chat_id].index(mes_id)
        #         self.pagin_data[user_info.chat_id].pop(index_mes)
        # except:
            await bot.delete_message(chat_id=user_info.chat_id, message_id=message.message_id)


    def add_save_pg_mes_id(self, user_info: UserInfoDB, message: Message) -> None:
            self.pagin_data_save[user_info.user_id] = message


    async def del_pg_save_mes(self, user_info: UserInfoDB) -> None:
        try:
            await bot.delete_message(chat_id=user_info.chat_id, message_id=self.pagin_data_save[user_info.chat_id].message_id)

            index = self.pagin_data[user_info.chat_id].index(self.pagin_data_save[user_info.chat_id])
            self.pagin_data[user_info.chat_id].pop(index)

        except:
            pass
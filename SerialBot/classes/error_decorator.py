#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telebot.asyncio_helper import ApiTelegramException
from telebot.types import CallbackQuery

from typing import Any
from database.mymodels import UserInfoDB, session_db


class ChangeSubscription():
    user_db_model = UserInfoDB
    session = session_db

    def __init__(self, func) -> None:
        self.func = func


    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        try:
            await self.func(*args, **kwds)
            self.subscript(*args)

        except ApiTelegramException as excep: 
            self.unsubscript(excep, *args)


    def unsubscript(self, excep: ApiTelegramException, call: CallbackQuery) -> None:
        if "bot was blocked by the user" in excep.description.lower():
            self.session.query(self.user_db_model).filter_by(user_id = call.from_user.id).update(
                            {self.user_db_model.status_subscription : False})

            self.session.commit()
            

    def subscript(self, call: CallbackQuery) -> None:
        user_info = self.session.query(self.user_db_model).filter_by(user_id = call.from_user.id).first()

        if user_info.status_subscription == False:

            self.session.query(self.user_db_model).filter_by(user_id = user_info.user_id).update(
                    {self.user_db_model.status_subscription : True})

            self.session.commit()
from sqlalchemy import VARCHAR, Text, create_engine, Column, Integer, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


engine = create_engine('sqlite:///sqlalchemy_example.db')
DBSession = sessionmaker(bind=engine)

session_db = DBSession()

Base = declarative_base()


class AnimeTodayDB(Base):
    __tablename__ = "anime_today_table"

    anime_id = Column(Text, primary_key=True)
    rus_name = Column(Text, nullable=False)
    eng_name = Column(Text, nullable=False)
    series_number = Column(Integer, nullable=False)
    voice_acting = Column(Text, nullable=False)
    anime_page = Column(Text, nullable=False)
    update_date = Column(Date, nullable=False)
    site_name = Column(Text, nullable=False)


class PushUserDB(Base):
    __tablename__ = "push_user_table"

    id =  Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    anime_id = Column(Text, nullable=False)
    push_flag = Column(Boolean, nullable=True, default=False)
    update_date = Column(Date, nullable=False)
    anime_page = Column(Text, nullable=False)
    message_text = Column(Text, nullable=False)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UserInfoDB(Base):
    __tablename__ = "user_info_table"

    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    user_login = Column(Text, nullable=True)
    user_name = Column(Text, nullable=False)
    is_bot = Column(Boolean, nullable=False)
    language_code = Column(VARCHAR(50), nullable=False)
    is_premium = Column(Text, nullable=True)
    status_subscription = Column(Boolean, default=True, nullable=False)

    anime_list_t = relationship("AnimeDB", secondary="user_to_anime_table", back_populates="user_info_list_t")

    find_anime_t = relationship("AnimeDB", secondary="pagin_user_anime", back_populates="find_user_info_t")


class AnimeDB(Base):
    __tablename__ = "anime_table"
    
    anime_id = Column(Integer, primary_key=True, autoincrement=True)
    eng_title = Column(Text, nullable=False)
    rus_title =  Column(Text, nullable=False)
    anime_page = Column(Text, nullable=False)
    image_name = Column(Text, nullable=True)
    image_page = Column(Text, nullable=True)
    image_path = Column(Text, nullable=False)
    anime_site_link = Column(Text, nullable=False)
    
    user_info_list_t = relationship("UserInfoDB", secondary="user_to_anime_table", back_populates="anime_list_t")

    find_user_info_t = relationship("UserInfoDB", secondary="pagin_user_anime", back_populates="find_anime_t")


class UserToAnimeDB(Base):
    __tablename__ = "user_to_anime_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("user_info_table.user_id"))
    anime_id = Column(Integer, ForeignKey("anime_table.anime_id"))


class FindAnimeBD(Base):
    __tablename__ = "pagin_user_anime"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_info_table.user_id"))
    anime_id = Column(Integer, ForeignKey("anime_table.anime_id"))


# Base.metadata.create_all(engine)
# Base.metadata.bind = engine
# session_db.commit()


# a = UserInfoDB(user_id=111111, chat_id=222222, user_login="dios", user_name="wolf", is_bot=False, language_code="ua")
# session_db.add(a)
# b = AnimeDB(eng_title="dios", rus_title="wolf", anime_page="qqqqq", image_name="wwwww", image_page="eeeeee", image_path="qweeeeeeeeee")
# session_db.add(b)
# session_db.commit()
# c = UserToAnimeDB(user_id=111111, anime_id=1)
# session_db.add(c)


# from sqlalchemy.orm import joinedload

# a = session_db.query(UserInfoDB).options(joinedload("find_anime_t")).filter_by(user_id=635261244).all()

# for i in a:
#     for c in i.find_anime_t:
#         print(c.anime_id)

# session_db.commit()
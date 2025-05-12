# import sqlite3
# from datetime import datetime
#
# class LoginManager:
#
#     @staticmethod
#     def create_table(curser:sqlite3.Cursor) -> bool:
#         curser.execute('''
#                        CREATE TABLE IF NOT EXISTS users (
#                                id INTEGER PRIMARY KEY AUTOINCREMENT,
#                                user_id INTEGER NOT NULL,
#                                user_name TEXT NOT NULL,
#                                mail TEXT NOT NULL,
#                                password TEXT NOT NULL,
#                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )
#                                ''')
#
#         print("users table created")
#
#         return True
#
#     @staticmethod
#     def len(self,curser:sqlite3.Cursor) ->int:
#         curser.execute('''
#                     SELECT seq FROM sqlite_sequence
#                     WHERE name = 'users';
#                 ''')
#
#         length = curser.fetchall()
#
#         print("The length of users is:", length[0])
#
#         conn.close()
#         return length[0]
#
#     @staticmethod
#     def login_check(curser:sqlite3.Cursor,user_name_or_mail:str,password:str) ->(bool,int | str):
#         if "@gmail" in user_name_or_mail:
#             curser.execute(
#                 '''
#                 SELECT user_id FROM users
#                 WHERE mail = ?
#                 AND password = ?
#                 ''', (user_name_or_mail, password)
#             )
#         else:
#             curser.execute(
#                 '''
#                 SELECT user_id FROM users
#                 WHERE user_name = ?
#                 AND password = ?
#                 ''', (user_name_or_mail, password)
#             )
#
#         user = curser.fetchall()
#
#         if user:
#             print("The user id:",user)
#             return True, user[0][0]
#         else:
#             return False, "שם משתמש או סיסמא אינם נכונים"
#
#     @staticmethod
#     def new_user(curser:sqlite3.Cursor,mail:str,password:str):
#
#         curser.execute(
#             '''
#             SELECT * FROM users
#             WHERE mail = ?
#             ''',
#             (mail,)
#         )
#
#         is_user_exists = curser.fetchall()
#
#         if is_user_exists:
#             print(is_user_exists)
#             if password != is_user_exists[0][3]:
#                 return False, "Password is incorrect"
#             return False, "User already exists"
#         else:
#             create_at = datetime.strftime(datetime.now(), "%d-%m-%Y %H:%M")
#             curser.execute(
#                 '''
#                 INSERT INTO users (user_id,mail,password,created_at)
#                 VALUES (?, ?, ?, ?)
#                 ''',
#                 (self._len, mail, password, create_at)
#             )
#             self._len += 1
#             print(f"New user added: {self._len - 1} {mail} {password} create at : {create_at}")
#
#         return True, str(self._len - 1)
#
#     @staticmethod
#     def remove_user(curser:sqlite3.Cursor,user_id:int):
#         curser.execute('''
#         DELETE FROM users
#         WHERE user_id = ?
#         ''',(user_id,))
#
#     @staticmethod
#     def change_password(curser:sqlite3.Cursor, user_id:int, previous_password:str, new_password:str) -> bool:
#         pass
import os.path

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from config.db import Base
from sqlalchemy.orm import Session
from config.db import engine

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    user_name = Column(String,nullable=False)
    mail = Column(String,nullable=False)
    password = Column(String,nullable=False)
    created_at = Column(DateTime,default=datetime.now)

class LoginManager:

    def __init__(self,db_session:Session):
        self.db_session = db_session

    def create_table(self):
        Users.metadata.create_all(bind=engine)
        print("users table created")

    def reset_table(self):
        Users.__table__.drop(engine)
        self.create_table()

    def login_check(self,user_name_or_mail:str,password:str):
        user = self.db_session.query(Users).filter(
            (Users.mail == user_name_or_mail) | (Users.user_name == user_name_or_mail)
        ).filter(Users.password == password).first()

        if user:
            print(f"User id: {user.id}")
            return True,user.id
        else:
            return False,"שם משתמש או סיסמא אינם נכונים"

    def new_user(self,mail:str,password:str,user_name:str = "unknown"):
        existing_user = self.db_session.query(Users).filter(Users.mail == mail).first()

        if existing_user:
            print("user already exists")
            return False,"User already exists"

        new_user = Users(mail=mail,password=password,user_name=user_name)
        self.db_session.add(new_user)
        self.db_session.commit()

        print(f"New user added: {new_user.mail}")

        return True, str(new_user.id)

    def remove_user(self,user_id:int):
        user = self.db_session.query(Users).filter(Users.id == user_id).first()
        if user:
            self.db_session.delete(user)
            self.db_session.commit()
            print(f"User {user_id} removed successfully")
            return True
        return False

    def change_password(self, user_id: int, previous_password: str, new_password: str):
        user = self.db_session.query(Users).filter(Users.id == user_id).first()
        if user and user.password == previous_password:
            user.password = new_password
            self.db_session.commit()
            print(f"Password for user {user_id} changed successfully")
            return True
        return False
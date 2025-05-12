# import sqlite3
#
# class ShoppingListManager:
#
#     def __init__(self,db_path:str = "task.db"):
#         self.db_path = db_path
#
#     def _connect(self) -> tuple:
#         conn = sqlite3.connect(self.db_path)
#         curser = conn.cursor()
#         return conn,curser
#
#     @staticmethod
#     def _create_table(curser:sqlite3.Cursor) -> bool:
#
#         curser.execute("DROP TABLE IF EXISTS shopping_list")
#         curser.execute('''
#                 CREATE TABLE IF NOT EXISTS shopping_list (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         user_id INTEGER NOT NULL,
#                         product TEXT NOT NULL,
#                         quantity INTEGER NOT NULL,
#                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                         completed_at TIMESTAMP,
#                         removed_at TIMESTAMP,
#                         is_removed BOOLEAN NOT NULL DEFAULT 0,
#                         is_active BOOLEAN NOT NULL DEFAULT 1)
#                         ''')
#
#         print("shopping list table created")
#         return True
#
#     @staticmethod
#     def insert_shopping_list_tasks(curser:sqlite3.Cursor,task_wrapper:dict):
#         try:
#             for product, quantity in task_wrapper["content"]:
#                 curser.execute(
#                     '''
#                     INSERT INTO shopping_list (user_id, product, quantity, created_at)
#                     VALUES (?, ?, ?, ?)
#                     ''', (task_wrapper["user_id"],
#                           product,
#                           quantity,
#                           task_wrapper["time"],
#                           )
#
#                 )
#
#             print(f"data saved: {task_wrapper}")
#             return True
#         except Exception as e:
#             print(e)
#             return False
#
#     @staticmethod
#     def get_shopping_tasks(curser:sqlite3.Cursor,user_id:int) -> list:
#         curser.execute(
#             '''
#             SELECT * FROM shopping_list
#             WHERE user_id = ?
#             AND is_removed = 0
#             ''', (user_id,)
#         )
#
#         tasks = curser.fetchall()
#
#         print(f"data received: {tasks}")
#
#         return tasks
#
#     @staticmethod
#     def complete_task(curser:sqlite3.Cursor,task_wrapper:dict) -> (bool,str):
#         if task_wrapper["is_active"] == 0:
#             curser.execute('''
#             UPDATE shopping_list
#             SET is_active = 0,
#             completed_at = ?
#             WHERE product = ?
#             AND is_active = 1
#             ''',(task_wrapper["completed_at"],task_wrapper["content"]["product"]))
#
#             print(f"task completed: {task_wrapper}")
#             return True,"mission complete"
#         else:
#             curser.execute('''
#             UPDATE shopping_list
#             SET is_active = 1,
#             completed_at = NULL
#             WHERE product = ?
#             AND is_active = 0
#             ''',  (task_wrapper["content"]["product"],))
#
#             print(f"task uncompleted: {task_wrapper}")
#             return True, "mission complete"
#
#     def remove_task(self,task_wrapper:dict) ->(bool,str):
#         conn,curser = self._connect()
#
#         curser.execute('''
#         UPDATE shopping_list
#         SET removed_at = ?,
#         is_removed = 1
#         WHERE product = ?
#         ''',(task_wrapper["removed_at"],task_wrapper["content"]["product"]))
#
#         print("task removed successfully")
#
#         conn.commit()
#         conn.close()
#
#         return True,"mission complete"
#
#     def clean_all_tasks(self):
#         conn,curser = self._connect()
#         curser.execute('''
#         DELETE FROM shopping_list
#         ''')
#         curser.execute('''
#         DELETE FROM sqlite_sequence
#         WHERE name = 'shopping_list'
#         ''')
#
#         print("all the tasks remove successfully")
#
#         conn.commit()
#         conn.close()
#
#         return True

from sqlalchemy import create_engine,Column,Integer,String,DateTime,Boolean
from sqlalchemy.orm import declarative_base,sessionmaker
from win32comext.shell.demos.servers.folder_view import tasks
from win32ctypes.pywin32.pywintypes import datetime
from datetime import datetime
from sqlalchemy.orm import Session
from config.db import engine

Base = declarative_base()


class ShoppingList(Base):

    __tablename__ = "shopping_list"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,nullable=False)
    product = Column(String,nullable=False)
    quantity = Column(Integer,nullable=False)
    created_at = Column(DateTime,default=datetime.now)
    completed_at = Column(DateTime,nullable=True)
    removed_at = Column(DateTime,nullable=True)
    is_removed = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)

class ShoppingDateBase:

    def __init__(self,db_session:Session):
        self.db_session = db_session

    @staticmethod
    def create_table():
        ShoppingList.metadata.create_all(engine)
        print("shopping list data base created")

    def reset_table(self):
        ShoppingList.__table__.drop(engine)
        print("shopping list table removed")
        self.create_table()

    def insert_shopping_list_tasks(self,task_wrapper:dict):
        for product,quantity in task_wrapper["content"]:

            existsing_product = self.db_session.query(ShoppingList).filter(
                (ShoppingList.user_id == task_wrapper["user_id"])
                & (ShoppingList.product == product)
                & (ShoppingList.is_removed == False)).first()

            if existsing_product:
                existsing_product.quantity += quantity

            else:
                new_task = ShoppingList(user_id=task_wrapper["user_id"],
                                        product=product,
                                        quantity=quantity)

                self.db_session.add(new_task)
            self.db_session.commit()

        print(f"data received: {task_wrapper}")
        return True

    def get_shopping_tasks(self,user_id:int):
        tasks = self.db_session.query(ShoppingList).filter((ShoppingList.user_id == user_id) & (ShoppingList.is_removed == False)).all()

        print(f"task received: {tasks}")

        tasks = [
            (
                task.id,
                task.user_id,
                task.product,
                task.quantity,
                task.is_active
            )
            for task in tasks
        ]

        return tasks

    def complete_task(self,task_wrapper:dict):

        if task_wrapper["is_active"]:
            task = (self.db_session.query(ShoppingList)
                    .filter((ShoppingList.user_id == task_wrapper["user_id"])
                            & (ShoppingList.product == task_wrapper["content"]["product"])
                            & (ShoppingList.is_removed == False))).first()

            task.is_active = 0
            task.completed_at = task_wrapper["completed_at"]
            print("task completed")
        else:
            task = (self.db_session.query(ShoppingList)
                    .filter((ShoppingList.user_id == task_wrapper["user_id"])
                            & (ShoppingList.product == task_wrapper["content"]["product"])
                            & (ShoppingList.is_removed == False))).first()

            task.is_active = 1
            task.completed_at = None
            print("task not completed")

        self.db_session.commit()
        return True,"task active change"

    def remove_task(self,task_wrapper:dict):
        task = (self.db_session.query(ShoppingList)
                .filter((ShoppingList.user_id == task_wrapper["user_id"])
                        & (ShoppingList.product == task_wrapper["content"]["product"])
                        & (ShoppingList.is_removed == False))).first()

        task.is_removed = 1
        task.removed_at = task_wrapper["removed_at"]

        self.db_session.commit()

        return True,"removed successfully"
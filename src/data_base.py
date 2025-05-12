import sqlite3
from datetime import datetime
from src.login_manager import LoginManager

class DataBase:

    def __init__(self,db_path:str='task.db'):
        self.login_manager = LoginManager()
        self.shopping_list_manager = ShoppingListManager()
        self.db_path = db_path

    def _connect(self) -> tuple[sqlite3.Connection,sqlite3.Cursor]:
        conn = sqlite3.connect(self.db_path)
        curser = conn.cursor()
        return conn,curser

    def create_table(self):
        conn,curser = self._connect()
        curser.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_type TEXT NOT NULL,
                task_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP
            )
        ''')

        print("database created")

        conn.commit()
        conn.close()

    def create_shopping_list_table(self):
        conn,curser = self._connect()

        self.shopping_list_manager._create_table(curser)

        conn.commit()
        conn.close()

    def user_login_check(self,mail:str,password:str) -> (bool,str | None):
        conn,curser = self._connect()
        is_exists,user_id = self.login_manager.login_check(curser,mail,password)
        conn.close()
        return is_exists,user_id

    def new_user(self,mail:str,password:str) -> (bool,str):
        conn, curser = self._connect()
        is_exists,user_id = self.login_manager.new_user(curser,mail,password)
        conn.close()
        return is_exists,user_id

    def delete_user(self,user_id:int) -> (bool,str):
        conn,curser = self._connect()

        try:
            self.login_manager.remove_user(curser,user_id)

            conn.commit()
            conn.close()
            return True,f"user: {user_id} remove successfully"
        except Exception as e:
            return False,str(e)

    def insert_shopping_list_task(self,task_wrapper:dict) -> bool:
        conn,curser = self._connect()
        self.shopping_list_manager.insert_shopping_list_tasks(curser,task_wrapper)
        conn.commit()
        conn.close()
        return True

    def get_user_task_by_type(self,user_id:int,task_type:str) -> list[tuple]:
        conn,curser = self._connect()
        tasks = []
        print(f"{user_id} : {task_type}")

        if "shopping" in task_type.lower():
            tasks = self.shopping_list_manager.get_shopping_tasks(curser,user_id)

        conn.close()
        return tasks

    def complete_task(self,task_type:str,task_wrapper:dict) ->bool:
        conn,curser = self._connect()

        is_exists,response = self.shopping_list_manager.complete_task(curser,task_wrapper)
        print(response)

        conn.commit()
        conn.close()

        return True
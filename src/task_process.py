import ast
from datetime import datetime
import json

class TaskProcess:

    def __init__(self,llm,file_handler,**kwargs):
        self.llm = llm
        self.file_handler = file_handler
        self.login_manager = kwargs.get("login_manager")
        self.shopping_manager = kwargs.get("shopping_manager")
        self.event_manager = kwargs.get("event_manager")

    def get_task_response(self,task:str,user_id:int) ->dict:
        task_type = self.llm.chat(task,self.file_handler.get_info("Task_Categorization_Prompt.txt"))
        task_content = []
        if "Shopping".lower() in task_type.lower():
            task_content = self._shopping_process(task)
            self.shopping_manager.insert_shopping_list_tasks(task_wrapper={"user_id" : user_id,"content" : task_content,"time" : datetime.strftime(datetime.now(),"%d-%m-%Y %H:%M:%S")})

        if "event".lower() in task_type.lower():
            task_content = self._event_process(task)
            self.event_manager.insert_event(task_wrapper={"user_id" : user_id,"content" : task_content})

        return {"type" : task_type,"content" : task_content}

    def _shopping_process(self,task:str):
        try:
            task_details = self.llm.chat(task,self.file_handler.get_info("files/shopping_prompt.txt"))
            task_list = ast.literal_eval(task_details)
            return task_list
        except SyntaxError:
            return "error"

    def _event_process(self,task:str):
        try:
            task_details = self.llm.chat(task,self.file_handler.get_info("files/event_prompt.txt"),400)
            print(f"{task_details}")
            task_details = json.loads(task_details)
            return task_details
        except:
            raise Exception("error")
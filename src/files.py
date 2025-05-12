from datetime import datetime

class FileHandler:

    def get_info(self,file_path:str) -> str:
        with open(file_path,'r') as f:
            try:
                text = f.read()
                text = self.change_time(text)
                return text
            except Exception as e:
                return "ERROR"

    def change_time(self,text:str) ->str:
        try:
            time = datetime.now().strftime("%d-%m-%Y")
            text = text.replace("{{time}}",time)
            return text
        except Exception as e:
            return "ERROR"
import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
class LLMClient:

    def __init__(self):
        self.client = Groq(api_key=os.getenv("LLM_API_KEY"))
        self.model = "llama3-70b-8192"

    def chat(self,text:str,prompt:str,max_tokens:int=50):

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=max_tokens,
            messages= [
                {"role" : "system", "content" : prompt},
                {"role": "user", "content": text},
            ]
        )

        return response.choices[0].message.content


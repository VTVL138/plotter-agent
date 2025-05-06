from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel

from models import config
import re
class ChatWithOllama(BaseModel):
    model_name: str = config["coding_model_name"]
    system_instructions: str = config["coding_model_instruction"]

    def call_LLM(self,prompt:str):
        response: ChatResponse = chat(model='codellama',
                                      messages=[{'role': 'system','content': self.system_instructions},
                                                {'role': 'user','content': prompt}])
        code_str = ChatWithOllama.clean_python_LLM_response(response["message"]["content"])
        return code_str
    
    @staticmethod
    def clean_python_LLM_response(text:str):
        return re.search(r"```python([\s\S]*?)\n```",text).group(1)
    

from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel

from models import config
import re
import logging

logger = logging.getLogger(__name__)
class ChatWithOllama(BaseModel):
    model_name: str = config["coding_model_name"]
    system_instructions: str = config["coding_model_instruction"]


    def call_LLM(self,prompt:str) -> str:
        response: ChatResponse = chat(model='codellama',
                                      messages=[{'role': 'system','content': self.system_instructions},
                                                {'role': 'user','content': prompt}])
        return response["message"]["content"]


    def call_LLM_python(self,prompt:str) -> str:
        response = self.call_LLM(prompt=prompt)
        print("Response:",response)
        try:
            code_str = ChatWithOllama.clean_python_LLM_response(text=response)
            return code_str
        
        except BaseException as e:
            logger.warning(f"Unexpected error while parsing generated python code string, error msg: {repr(e)}")
            return None
        
    
    @staticmethod
    def clean_python_LLM_response(text:str):
        if text.startswith("```python") and text.endswith("```"):
            return re.search(r"```python([\s\S]*?)```",text).group(1)
        elif text.startswith("```") and text.endswith("```"):
            return re.search(r"```([\s\S]*?)```",text).group(1)
        else:
            return text
    

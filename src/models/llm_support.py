from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel


from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from typing import Any, Dict, Iterator, List, Mapping, Optional
from langchain_core.outputs import GenerationChunk

from models import config
import re
import logging

logger = logging.getLogger(__name__)
class ChatWithOllama(BaseModel):
    model_name: str = config["coding_model_name"]


    def call_LLM(self,prompt:str) -> str:
        response: ChatResponse = chat(model='codellama',
                                      messages=[{'role': 'system','content': config["base_model_instruction"]},
                                                {'role': 'user','content': prompt}])
        return response["message"]["content"]


    def call_LLM_python(self,prompt:str) -> str:
        response: ChatResponse = chat(model='codellama',
                                      messages=[{'role': 'system','content': config["coding_model_instruction"]},
                                                {'role': 'user','content': prompt}])
        response = response["message"]["content"]
        try:
            code_str = ChatWithOllama.clean_python_LLM_response(text=response)
            return code_str
        
        except BaseException as e:
            logger.warning(f"Unexpected error while parsing generated python code string, error msg: {repr(e)}")
            return None
        
    def ask_for_bugfix(self, original_prompt: str, chat_history: List[str], source_code: str, error_msg: str):
        bugfix_prompt = config["bugfix_instruction"] + f"\n Original task: {original_prompt}\nchat history: {"\n\n".join(chat_history)}\nsource code: {source_code}\nerror message:{error_msg}"
        return self.call_LLM_python(bugfix_prompt)

    @staticmethod
    def clean_python_LLM_response(text:str):
        if text.startswith("```python") and text.endswith("```"):
            return re.search(r"```python([\s\S]*?)```",text).group(1)
        elif text.startswith("```") and text.endswith("```"):
            return re.search(r"```([\s\S]*?)```",text).group(1)
        else:
            return text
    


class CustomLLM(LLM):

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
                If stop tokens are not supported consider raising NotImplementedError.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string. Actual completions SHOULD NOT include the prompt.
        """
        # if stop is not None:
        #     raise ValueError("stop kwargs are not permitted.")
        return ChatWithOllama().call_LLM(prompt=prompt)

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the LLM on the given prompt.

        This method should be overridden by subclasses that support streaming.

        If not implemented, the default behavior of calls to stream will be to
        fallback to the non-streaming version of the model and return
        the output as a single chunk.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of these substrings.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            An iterator of GenerationChunks.
        """
        response = ChatWithOllama().call_LLM(prompt=prompt)
        for char in response:
            chunk = GenerationChunk(text=char)
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)

            yield chunk

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom Ollama, codellama with postprocess."


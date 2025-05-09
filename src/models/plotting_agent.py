from .llm_support import ChatWithOllama

from pydantic import BaseModel
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from typing import Any, Dict, Iterator, List, Mapping, Optional
import pandas as pd
from PIL import Image
import ast


import logging
logger = logging.getLogger(__name__)

class PlotterGraphState(TypedDict):
    original_instruction: str
    df: pd.DataFrame
    source_code: str
    chat_history: List[str]
    last_error_msg: str
    return_img: Optional[bytes]
    test_successful: bool

class PlotterAgent(BaseModel):


    def generate_source_code(self, state: PlotterGraphState) -> PlotterGraphState:
        code_str = ChatWithOllama().call_LLM_python(state["original_instruction"])
        return PlotterGraphState(original_instruction=state["original_instruction"],
                                 df=state["df"],
                                source_code=code_str,
                                chat_history=state["chat_history"] + [code_str],
                                last_error_msg=state["last_error_msg"],
                                return_img=state["return_img"],
                                test_successful=state["test_successful"])

    def check_source_syntax(self, state: PlotterGraphState) -> PlotterGraphState:
        try:
            ast.parse(state["source_code"])
            globals = {"df_data":state["df"]}
            locals = {}
            exec(state["source_code"],globals=globals,locals=locals)

            return PlotterGraphState(original_instruction=state["original_instruction"],
                                     df=state["df"],
                                    source_code=state["source_code"],
                                    chat_history=state["chat_history"],
                                    last_error_msg=state["last_error_msg"],
                                    return_img=locals["image_bytes"],
                                    test_successful=True)
        except Exception as e:
            logger.debug(f"Checking source code, error: {repr(e)}")
            return PlotterGraphState(original_instruction=state["original_instruction"],
                                     df=state["df"],
                                    source_code=state["source_code"],
                                    chat_history=state["chat_history"],
                                    last_error_msg=str(repr(e)),
                                    test_successful=False)

    def fix_source_code(self, state: PlotterGraphState) -> PlotterGraphState:
        new_code_str = ChatWithOllama().ask_for_bugfix(original_prompt=state["original_instruction"],
                                                    chat_history=state["chat_history"],
                                                    source_code=state["source_code"],
                                                    error_msg=state["last_error_msg"])
        
        
        return PlotterGraphState(original_instruction=state["original_instruction"],
                                 df=state["df"],
                                    source_code=new_code_str,
                                    chat_history=state["chat_history"] + [new_code_str],
                                    last_error_msg=state["last_error_msg"],
                                    return_img=state["return_img"],
                                    test_successful=state["test_successful"])


    def decide_code_is_good(self, state: PlotterGraphState):
        return "fix_source_code" if state["test_successful"] == False else "END"



    def create_agent(self):

        workflow = StateGraph(PlotterGraphState)

        workflow.add_node("generate_source_code", self.generate_source_code)
        workflow.add_node("check_source_syntax", self.check_source_syntax)
        workflow.add_node("fix_source_code", self.fix_source_code)

        # workflow.set_entry_point("generate_source_code")
        workflow.add_edge(START, "generate_source_code")
        workflow.add_edge('generate_source_code', 'check_source_syntax')
        workflow.add_edge('fix_source_code', 'check_source_syntax')

        workflow.add_conditional_edges(
            'check_source_syntax',
            self.decide_code_is_good,
            {
                "fix_source_code": "fix_source_code",
                "END": END
            }
        )
        return workflow.compile()


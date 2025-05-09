import os

def get_extension_from_filename(filename:str):
    return os.path.splitext(filename)[-1][1:]

def parse_plot_prompt(base_prompt:str,df_head_str:str,plot_instructions:str) -> str:
    return base_prompt + f"\nThe dataframe: {df_head_str}\n" + f"Instructions: {plot_instructions}\n"
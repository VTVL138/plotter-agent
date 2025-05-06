import os

def get_extension_from_filename(filename:str):
    return os.path.splitext(filename)[-1][1:]
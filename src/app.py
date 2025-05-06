from fastapi import FastAPI, UploadFile

import logging
import sys
import pandas as pd

from models.file_processor import DataFrameReader, CustomFile



logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/plot_from_file/")
async def plot_from_file(file: UploadFile):
    my_file = CustomFile().load_from_file(file)
    print("____",my_file.extension)
    df = DataFrameReader().load_dataframe(my_file)
    print("df:___",df)0
    return {"message": file.filename}


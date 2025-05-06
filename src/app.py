from fastapi import FastAPI, UploadFile, HTTPException

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

    my_file = CustomFile.load_from_file(file)
    if my_file.extension in ["csv","xls","xlsx"]:
        my_dataframe = DataFrameReader.load_dataframe(my_file)
    else:
        logger.error(f"Unsupported file extension: {my_file.extension}")    
        raise HTTPException(500,{"message": f"Unsupported file extension: {my_file.extension}"})
    

    return {"message": file.filename}


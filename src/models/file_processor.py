from pydantic import BaseModel
from tempfile import SpooledTemporaryFile
from typing import List
from fastapi import UploadFile


import pandas as pd

from .utils import get_extension_from_filename


class CustomFile(BaseModel):
    extension: str = None
    content: SpooledTemporaryFile = None

    @staticmethod
    def load_from_file(file:UploadFile):
        return CustomFile(extension=get_extension_from_filename(filename=file.filename),
                          content=file.file)

    class Config:
        arbitrary_types_allowed = True


class DataFrameReader(BaseModel):
    # dataframes: List[pd.DataFrame]
    dataframe: pd.DataFrame = None
    text: str = None

    class Config:
        arbitrary_types_allowed = True
    
    @staticmethod
    def load_dataframe(my_file: CustomFile):
        match my_file.extension:
            case "csv":
                df = pd.read_csv(my_file.content)
                return DataFrameReader(dataframe=df,text=str(df))
            case "xls":
                df = pd.read_excel(my_file.content)
                return DataFrameReader(dataframe=df,text=str(df))
            case "xlsx":
                df = pd.read_excel(my_file.content)
                return DataFrameReader(dataframe=df,text=str(df))
            
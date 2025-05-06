from pydantic import BaseModel
from tempfile import SpooledTemporaryFile
from typing import List
from fastapi import UploadFile


import pandas as pd

from .utils import get_extension_from_filename


class CustomFile(BaseModel):
    extension: str = None
    content: SpooledTemporaryFile = None

    def load_from_file(self, file:UploadFile):
        return CustomFile(extension=get_extension_from_filename(filename=file.filename),
                          content=file.file)

    class Config:
        arbitrary_types_allowed = True


class DataFrameReader(BaseModel):
    # dataframes: List[pd.DataFrame]
    dataframe: pd.DataFrame = None

    class Config:
        arbitrary_types_allowed = True
    
    def load_dataframe(self, my_file: CustomFile):
        match my_file.extension:
            case "csv":
                return DataFrameReader(dataframe=pd.read_csv(my_file.content))
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
import logging
import sys
import pandas as pd

from models.file_processor import DataFrameReader, CustomFile
from models.plotting_agent import PlotterAgent,PlotterGraphState
from models.utils import parse_plot_prompt
from models import config


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/plot_from_file/")
async def plot_from_file(file: UploadFile, plot_instructions: str):
    my_file = CustomFile.load_from_file(file)
    if my_file.extension in ["csv","xls","xlsx"]:
        my_dataframe = DataFrameReader.load_dataframe(my_file)
    else:
        logger.error(f"Unsupported file extension: {my_file.extension}")    
        raise HTTPException(500,{"message": f"Unsupported file extension: {my_file.extension}"})
    plotting_prompt = parse_plot_prompt(config["plotting_base_prompt"],str(my_dataframe.dataframe.head()),plot_instructions)

    print("______plot:",plotting_prompt)
    my_agent = PlotterAgent().create_agent()
    s = PlotterGraphState(original_instruction=plotting_prompt,
                          df=my_dataframe.dataframe,
                          source_code="",
                          chat_history=[""],
                          last_error_msg="",
                          return_img=None,
                          test_successful=False)

    result = my_agent.invoke(s,{"recursion_limit": 5})
    # img_byte_arr = io.BytesIO()
    # result["return_img"].save(img_byte_arr, format='PNG')
    print("_______return_image:",type(result["return_img"]))
    return StreamingResponse(result["return_img"], media_type="image/jpeg")


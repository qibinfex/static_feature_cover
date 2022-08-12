import os 

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import FileResponse

from settings import PORT
from settings import DEBUG
from settings import static
from logics import list_dic_2_file
from logics import statistics_fr_cover_data


app = FastAPI()


class QueryItem( BaseModel):
    query_id: str

@app.post("/statistics_fr_cover_data")
async def statistics_fr_cover(item:QueryItem):
    return_data = statistics_fr_cover_data(item.query_id)
    data = list(return_data.get('data').values())
    file_path = list_dic_2_file(item.query_id, data)
    return_data['file_path'] = file_path
    return return_data

@app.get("/get_file/{file_name}")
async def download_file(file_name):
    filt_path = os.path.join(static, file_name)
    return FileResponse(filt_path, filename=file_name)

if __name__ == "__main__":
    uvicorn.run('app:app', host="0.0.0.0", port=PORT, debug=DEBUG, reload=DEBUG)
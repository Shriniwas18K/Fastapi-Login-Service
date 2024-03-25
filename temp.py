from fastapi import File,FastAPI
from fastapi.responses import JSONResponse
import os
import uuid
app=FastAPI()
from typing import Annotated
UPLOAD_DIR = "uploaded_images"
@app.post("/uploadImage/{phn}/{unm}")
async def create_file(token:str,file: Annotated[bytes, File()],phn,unm):
    print(file)
    os.makedirs(UPLOAD_DIR+f'/{phn+unm}/', exist_ok=True)
    with open(UPLOAD_DIR+f'/{phn+unm}/'+str(uuid.uuid4())+'.png',"wb") as f:
        f.write(file)
    return JSONResponse(
        content={"image_path": UPLOAD_DIR+f'/{phn+unm}/'+str(uuid.uuid4())+'.png'}
    )
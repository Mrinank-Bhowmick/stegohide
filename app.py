import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from stegano import lsb
from fastapi.templating import Jinja2Templates
from fastapi import Request
from io import BytesIO
import os
from PIL import Image

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def hide_message(image_path, message):
    secret_image = lsb.hide(image_path, message)
    return secret_image.save(image_path)

def reveal_message(image_path):
    return lsb.reveal(image_path)

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/hide")
async def hide_text(request: Request, file: UploadFile = File(...), secret_msg: str = Form(...)):
    try:
        print("Received secret message:", secret_msg)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        data = await file.read()
        with open(temp_file.name, 'wb') as f:
            f.write(data)

        hide_message(temp_file.name, secret_msg)

        with open(temp_file.name, "rb") as img_file:
            hidden_image_bytes = img_file.read()

        return StreamingResponse(BytesIO(hidden_image_bytes), media_type="image/png", headers={"Content-Disposition": f"inline; filename=hidden_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reveal")
async def reveal_text(request: Request, file: UploadFile = File(...)):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        data = await file.read()
        with open(temp_file.name, 'wb') as f:
            f.write(data)

        hidden_message = reveal_message(temp_file.name)

        return {"message": "Message revealed successfully!", "hidden_message": hidden_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

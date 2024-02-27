from fastapi import FastAPI, WebSocket, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models.question_answer_paraphrase import EMBEDDINGS
import os

app = FastAPI()
template = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

model = EMBEDDINGS()


@app.get("/")
async def index(request: Request):
    return template.TemplateResponse("index.html", {"request": request, "title": "Chat embeddings"})

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        respuesta = model.search_paragraphs(data, filename)
        #respuesta=data
        await websocket.send_text(f"Result: {respuesta}")



@app.post("/file")
async def upload_file(file: UploadFile = File(...)):
    UPLOADS_DIRECTORY = "files"
    try:
        # Guardar el archivo en una ubicación específica
        file_path = os.path.join(UPLOADS_DIRECTORY, file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)  # Eliminar el archivo existente si ya existe

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        print(file.filename)
        global filename 
        filename = file.filename
        model.search_embeddings_content(file.filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"saved": True}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


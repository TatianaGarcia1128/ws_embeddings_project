from fastapi import FastAPI, WebSocket, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models.question_answer_paraphrase import EMBEDDINGS
import os

app = FastAPI()
template = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

model = EMBEDDINGS()


@app.get("/")
async def index(request: Request):
    return template.TemplateResponse("index.html", {"request": request, "title": "Chat embeddings"})

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('hola')
    while True:
        data = await websocket.receive_text()
        print(data)
        answers = model.search_paragraphs(data, filename)
        print(answers)
        # await websocket.send_text(f"Result: {answers}")
        # #respuesta=data
        for answer in answers:
            print(answer)
            await websocket.send_text(f"Result: {answer}")

        file_path = os.path.join("app/files",  filename)
        if os.path.exists(file_path):
            os.remove(file_path)  # Eliminar el archivo existente si ya existe


@app.post("/file")
async def upload_file(file: UploadFile = File(...)):
    UPLOADS_DIRECTORY = "app/files"
    try:
        # Guardar el archivo en una ubicación específica
        file_path = os.path.join(UPLOADS_DIRECTORY, file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)  # Eliminar el archivo existente si ya existe
    
        # Read the binary content
        content = await file.read()

        # Decode the content to UTF-8
        decoded_content = content.decode('utf-8', errors='ignore')  # You can handle errors as per your requirement

        with open(file_path, "w", encoding='utf-8') as f:
            f.write(decoded_content)

        print(file.filename)
        global filename 
        filename = file.filename
        model.search_embeddings_content(file.filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"saved": True}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)



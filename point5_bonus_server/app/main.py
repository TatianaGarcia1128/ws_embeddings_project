#import modules
from fastapi import FastAPI, WebSocket, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models.question_answer_paraphrase import EMBEDDINGS
import os

#Create FastAPI instance
app = FastAPI()

# Set up Jinja2 templates
template = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Create an instance of the EMBEDDINGS class
model = EMBEDDINGS()

# Define the root endpoint
@app.get("/")
async def index(request: Request):
    return template.TemplateResponse("index.html", {"request": request, "title": "Chat embeddings"})

# Define the WebSocket endpoint
@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    print('hola')
    while True:
        # Receive a question from the WebSocket
        question = await websocket.receive_text()
        print(question)
        # Search for paragraphs similar to the question
        answers = model.search_paragraphs(question, filename)
        print(answers)
        # Send the question and the answers back to the WebSocket
        await websocket.send_text(f"\nQuestion: {question}")
        for answer in answers:
            print(answer)
            await websocket.send_text(f"Result: {answer}")


# Define the file upload endpoint
@app.post("/file")
async def upload_file(file: UploadFile = File(...)):
    UPLOADS_DIRECTORY = "app/files"
    try:            
        #definition filepath
        file_path = os.path.join(UPLOADS_DIRECTORY, file.filename)

        #Delete existing file if it already exists
        if os.path.exists(file_path):
            os.remove(file_path)  
    
        # Read the binary content
        content = await file.read()

        # Decode the content to UTF-8
        decoded_content = content.decode('utf-8', errors='ignore')  # You can handle errors as per your requirement

        with open(file_path, "w", encoding='utf-8') as f:
            f.write(decoded_content)

        print(file.filename)
        global filename 
        filename = file.filename
        # Search for embeddings in the content of the file
        model.search_embeddings_content(file.filename)

    except Exception as e:
        # Raise an HTTP exception if an error occurs
        raise HTTPException(status_code=500, detail=str(e))

    # Return a JSON response indicating that the file was saved
    return JSONResponse(content={"saved": True}, status_code=200)

# Run the application if this file is the entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
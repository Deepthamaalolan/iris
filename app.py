from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os
import shutil
from processing import VideoProcessor

app = FastAPI()

# Directory where uploaded videos will be stored
UPLOAD_DIRECTORY = "./uploaded_videos"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@app.post("/upload-video/")
async def upload_video(video: UploadFile = File(...)):
    try:
        video_filename = os.path.join(UPLOAD_DIRECTORY, video.filename)
        with open(video_filename, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    finally:
        video.file.close()
    return {"filename": video.filename}

@app.get("/")
async def main():
    content = """
<body>
<form action="/upload-video/" enctype="multipart/form-data" method="post">
<input name="video" type="file" accept="video/*">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
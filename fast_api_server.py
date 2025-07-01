from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mood_music_player.detectors.image_emotion import detect_emotions_with_dominant_box
from mood_music_player.detectors.text_emotion import TextEmotionDetector
from pymongo import MongoClient
from fastapi.staticfiles import StaticFiles
import shutil
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load emotion detector
text_detector = TextEmotionDetector()


# Direct MongoDB Atlas connection (you can switch to env var later)
#client = MongoClient("mongodb+srv://hritikagore711:JGUUuVF8ytHd7l0a@cluster0.qoc2agk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient("mongodb://localhost:27017")  # For local MongoDB
db = client["moodmusic"]
songs_collection = db["songs"]

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------- MODELS --------------------
class TextInput(BaseModel):
    text: str

# -------------------- ROUTES --------------------

# Root route
@app.get("/")
async def root():
    return {"message": "Mood Music Player API is running."}

# Detect image-based emotion
@app.post("/detect-image")
async def detect_image(image: UploadFile = File(...)):
    try:
        os.makedirs("input_images", exist_ok=True)
        file_path = os.path.join("input_images", image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        mood, processed_path = detect_emotions_with_dominant_box(file_path)
        return {"mood": mood, "processed_image": processed_path}

    except Exception as e:
        print(f"❌ Image Detection Error: {e}")
        return {"error": "Failed to detect emotion from image."}

# Detect text-based emotion
@app.post("/detect-text")
async def detect_text(data: TextInput):
    try:
        mood = text_detector.predict_emotion(data.text)
        return {"mood": mood}
    except Exception as e:
        print(f"❌ Text Detection Error: {e}")
        return {"error": "Failed to detect emotion from text."}

# Get songs by mood
@app.get("/songs/{mood}")
async def get_songs_for_mood(mood: str):
    try:
        formatted_mood = mood.strip()
        songs = list(songs_collection.find({
            "emotion": {"$regex": f"^{formatted_mood}$", "$options": "i"}
        }))
        for song in songs:
            song.pop("_id", None)
        return {"songs": songs}
    except Exception as e:
        print(f"❌ Fetch Songs Error: {e}")
        return {"error": "Could not fetch songs."}

# Upload song and add to MongoDB
@app.post("/add-song")
async def add_song(
    title: str = Form(...),
    artist: str = Form(...),
    mood: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        os.makedirs("static/songs", exist_ok=True)
        file_path = os.path.join("static/songs", file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        song_entry = {
            "title": title,
            "artist": artist,
            "emotion": mood,
            "filePath": f"/static/songs/{file.filename}"
        }

        songs_collection.insert_one(song_entry)
        print(f"✅ Added song: {title} by {artist} [{mood}]")
        return {"message": "Song added successfully!"}
    except Exception as e:
        print(f"❌ Add Song Error: {e}")
        return {"error": f"Failed to add song. Reason: {str(e)}"}

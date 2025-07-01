from flask import Flask, request, jsonify
from mood_music_player.detectors.image_emotion import detect_emotions_with_dominant_box
from mood_music_player.detectors.text_emotion import TextEmotionDetector
from mood_music_player.player.music_player import MusicPlayer
from mood_music_player.config import CONFIG
import os

app = Flask(__name__)

text_detector = TextEmotionDetector()
music_player = MusicPlayer(CONFIG["DB_PATH"])

# Enable CORS
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# ✅ Route to detect emotion from image
@app.route("/detect-image", methods=["POST"])
def detect_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    os.makedirs("input_images", exist_ok=True)
    file_path = os.path.join("input_images", file.filename)
    file.save(file_path)

    try:
        mood, processed_img_path = detect_emotions_with_dominant_box(file_path)
        return jsonify({
            "mood": mood,
            "processed_image": processed_img_path  # Optional: return processed image path
        })
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return jsonify({"error": "Failed to detect emotion"}), 500

# ✅ Route to detect emotion from text
@app.route("/detect-text", methods=["POST"])
def detect_text():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    try:
        mood = text_detector.predict_emotion(data['text'])
        return jsonify({"mood": mood})
    except Exception as e:
        print(f"❌ Error processing text: {e}")
        return jsonify({"error": "Failed to detect emotion"}), 500

# ✅ Route to return songs based on mood
@app.route("/songs/<mood>", methods=["GET"])
def get_songs_for_mood(mood):
    try:
        songs = music_player.get_songs_by_mood(mood)
        return jsonify({"songs": songs})
    except Exception as e:
        print(f"❌ Error fetching songs: {e}")
        return jsonify({"error": "Could not fetch songs"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)

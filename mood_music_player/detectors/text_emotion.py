from transformers import pipeline

class TextEmotionDetector:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=False
        )
        self.emotion_map = {
            "joy": "happy",
            "sadness": "sad",
            "anger": "angry",
            "disgust": "disgust",
            "fear": "fear",
            "surprise": "surprise",
            "neutral": "neutral",
            "contempt": "contempt"
        }

    def predict_emotion(self, text):
        try:
            result = self.classifier(text)
            raw_emotion = result[0]['label'].lower()
            return self.emotion_map.get(raw_emotion, "neutral")
        except Exception as e:
            print(f"❌ Error detecting text emotion: {e}")
            return "neutral"

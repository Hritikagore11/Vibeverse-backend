import os
from config import CONFIG
from detectors.image_emotion import detect_emotions_with_dominant_box
from detectors.text_emotion import TextEmotionDetector
from player.music_player import MusicPlayer
from utils.input_questions import questions

def main():
    text_detector = TextEmotionDetector()
    music_player = MusicPlayer(CONFIG["DB_PATH"])

    print("\n🎧 Welcome to the Mood-Based Music Player 🎧")

    while True:
        mode = input("\nChoose input mode - 'image' or 'text' (or type 'exit' to quit): ").strip().lower()

        if mode == 'exit':
            print("\n👋 Exiting... Have a great day!")
            break

        elif mode == 'image':
            images = [img for img in os.listdir(CONFIG['IMAGE_FOLDER']) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not images:
                print("⚠️ No images found in input_images folder.")
                continue

            print("\n📸 Available images:")
            for idx, img in enumerate(images):
                print(f"{idx + 1}. {img}")

            try:
                selected = int(input("Enter number of image to use: ")) - 1
                if not (0 <= selected < len(images)):
                    print("⚠️ Invalid selection.")
                    continue

                image_path = os.path.join(CONFIG['IMAGE_FOLDER'], images[selected])
                emotion, output_img_path = detect_emotions_with_dominant_box(image_path)

                print(f"\n🎭 Detected Emotion from image: {emotion}")
                print(f"✅ Processed image saved at: {output_img_path}")

                confirm = input("Is this correct? (yes / no / exit): ").strip().lower()
                if confirm == 'yes':
                    music_player.play_music_for_emotion(emotion)
                elif confirm == 'exit':
                    break
                else:
                    print("🔁 Let's try again.")

            except Exception as e:
                print(f"❌ Error processing image: {e}")

        elif mode == 'text':
            print("\n🧠 Let's understand your mood better through a few quick questions.")
            responses = [input(f"{q}\n> ").strip() for q in questions]
            combined_text = " ".join(responses)

            try:
                emotion = text_detector.predict_emotion(combined_text)
                print(f"\n📝 Detected Emotion from text: {emotion}")

                confirm = input("Is this correct? (yes / no / exit): ").strip().lower()
                if confirm == 'yes':
                    music_player.play_music_for_emotion(emotion)
                elif confirm == 'exit':
                    break
                else:
                    print("🔁 Let's try again.")
            except Exception as e:
                print(f"❌ Error processing text: {e}")

        else:
            print("⚠️ Invalid input. Please choose 'image' or 'text'.")

if __name__ == "__main__":
    main()

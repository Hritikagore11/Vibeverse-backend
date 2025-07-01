import cv2
from deepface import DeepFace
import os
from datetime import datetime

def detect_emotions_with_dominant_box(image_path, save_dir="input_images"):
    
    #Detects emotions in a group photo using DeepFace, highlights the dominant face,
    #saves the image, and returns the dominant emotion.

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found or unreadable: {image_path}")

    # Analyze emotions in the image
    results = DeepFace.analyze(
        img_path=image_path,
        actions=['emotion'],
        enforce_detection=False,
        detector_backend="retinaface"
    )

    if isinstance(results, dict):
        results = [results]

    if not results:
        raise ValueError("No faces detected in the image.")

    # Identify dominant face based on largest bounding box area
    areas = [(res['region']['w'] * res['region']['h']) for res in results]
    dominant_idx = areas.index(max(areas))

    # Print detailed emotion scores for the dominant face
    print("\n Emotion scores for dominant face:")
    for emotion, score in results[dominant_idx]['emotion'].items():
        print(f"{emotion.capitalize():<10}: {score:.2f}")

    # Draw bounding boxes on all faces, green for dominant
    for idx, res in enumerate(results):
        x, y, w, h = res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']
        emotion = res['dominant_emotion']
        color = (0, 255, 0) if idx == dominant_idx else (255, 255, 255)
        thickness = 3 if idx == dominant_idx else 1
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
        cv2.putText(img, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Save output image
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(save_dir, f"processed_{timestamp}.jpg")

    success = cv2.imwrite(output_path, img)
    if not success:
        raise RuntimeError(f"Failed to save processed image at {output_path}")

    print(f"\n✅ Processed image saved at: {output_path}")
    dominant_emotion = results[dominant_idx]['dominant_emotion']
    return dominant_emotion, output_path


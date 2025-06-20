import cv2
import numpy as np
from deepface import DeepFace

# === SETTINGS ===
model_name = 'Facenet'
detector_backend = 'opencv'
enforce_detection = True  # make it False if faces aren't always detected
size = (512, 512)

# === PATHS TO YOUR TEST IMAGES ===
img1_path = "ahmedKamal3.png"
img2_path = "meky2.png"

def get_face_embedding(image_path):
    try:
        # Load image
        img = cv2.imread(image_path)

        # Resize to 512x512
        img_resized = cv2.resize(img, size)

        # Convert BGR to RGB (DeepFace expects RGB)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

        # Get embedding
        representations = DeepFace.represent(
            img_rgb,
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=enforce_detection
        )

        return representations[0]["embedding"]

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

# === MAIN LOGIC ===
if __name__ == "__main__":
    emb1 = get_face_embedding(img1_path)
    emb2 = get_face_embedding(img2_path)

    if emb1 is not None and emb2 is not None:
        dist = np.linalg.norm(np.array(emb1) - np.array(emb2))
        print(f"Distance between images: {dist:.4f}")
        if dist < 11.02:
            print("✅ Match (Same person)")
        else:
            print("❌ Not a match (Different people or bad image)")
    else:
        print("Failed to generate embeddings for one or both images.")

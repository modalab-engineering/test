import os

from transformers import CLIPModel, CLIPProcessor

from config import settings

MODEL_NAME = settings.MODEL_PATH
CACHE_DIR = settings.CACHE_DIR

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


print(f"Downloading model and processor for {MODEL_NAME}...")
model = CLIPModel.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
processor = CLIPProcessor.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
print("Download complete.")

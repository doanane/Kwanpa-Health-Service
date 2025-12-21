import os
from dotenv import load_dotenv

load_dotenv()

print("Testing environment variables:")
print(f"AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT: {os.getenv('AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT')}")
print(f"AZURE_CUSTOM_VISION_PREDICTION_KEY exists: {bool(os.getenv('AZURE_CUSTOM_VISION_PREDICTION_KEY'))}")
print(f"GEMINI_API exists: {bool(os.getenv('GEMINI_API'))}")
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LYRICA_API_KEY = os.getenv('LYRICA_API_KEY')

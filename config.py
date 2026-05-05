# ============================================================
# FILE 1: config.py (FIXED - API key moved to .env file)
# Your actual API key is now in .env file which is NOT
# uploaded to GitHub. This keeps your key safe.
# ============================================================

import os

# python-dotenv reads the .env file and loads variables
# Install it with: pip install python-dotenv
from dotenv import load_dotenv

# Load the .env file into environment variables
load_dotenv()

# Path to Tesseract OCR installation
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Read API key from .env file — never hardcode keys here
GEMINI_API_KEY = os.getenv("GROQ_API_KEY", "")

# Validate that key was loaded successfully
if not GEMINI_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env file")
    print("Please create .env file with: GROQ_API_KEY=your_key_here")

# Folder where you drop the daily newspaper PDFs every morning
INPUT_FOLDER = "./input_pdfs"

# Folder where final digest PDFs are saved after processing
OUTPUT_FOLDER = "./output_pdfs"

# Folder for temporary individual article slides
SLIDES_FOLDER = "./slides"

# Maximum articles to extract per PDF page
MAX_ARTICLES_PER_PAGE = 3

# Minimum characters for valid article
MIN_ARTICLE_LENGTH = 120
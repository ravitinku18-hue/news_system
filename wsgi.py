# ============================================================
# FILE: wsgi.py
# PURPOSE: Production server entry point
#          Use this instead of python app.py
#          Waitress is a production grade server for Windows
# ============================================================

from waitress import serve
from app import app

if __name__ == "__main__":
    print("Starting production server on http://0.0.0.0:5000")
    # threads=4 handles multiple users at same time
    serve(app, host="0.0.0.0", port=5000, threads=4)
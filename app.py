# ============================================================
# FILE 6: app.py
# PURPOSE: Runs the dashboard website using Flask
#          - Shows all articles as thumbnails
#          - Auto-scrolls every 4 seconds
#          - Allows downloading the digest PDFs
#          - Reads article data from the JSON index file
# RUN THIS: python app.py
# OPEN IN BROWSER: http://localhost:5000
# ============================================================

# Flask is a lightweight Python web framework
# It lets us create a website with just Python
from flask import (
    Flask,        # main app object
    render_template,  # loads HTML files from templates folder
    send_file,    # sends files for download
    jsonify       # converts Python dict to JSON response
)

# os helps with file path operations
import os

# glob finds files matching a pattern
import glob

# json reads our article index file
import json

# datetime helps get today's date
from datetime import datetime

# Import our folder settings
from config import OUTPUT_FOLDER

# Create the Flask application object
# __name__ tells Flask where to find template and static files
app = Flask(__name__)


@app.route("/")
def dashboard():
    """
    Main route: serves the dashboard homepage.
    When user visits http://localhost:5000 they see this page.
    Flask looks for dashboard.html inside the 'templates' folder.
    """
    return render_template("dashboard.html")


@app.route("/api/articles")
def get_articles():
    """
    API route: returns today's article data as JSON.
    The dashboard JavaScript calls this to get article thumbnails.
    URL: http://localhost:5000/api/articles
    """

    # Get today's date string to find today's index file
    today = datetime.now().strftime("%Y-%m-%d")

    # Build path to today's JSON index file
    index_path = os.path.join(OUTPUT_FOLDER, f"index_{today}.json")

    # Check if today's index file exists
    if os.path.exists(index_path):

        # Open and read the JSON file
        with open(index_path, encoding="utf-8") as f:
            data = json.load(f)

        # Combine law_and_order and political into one flat list
        all_articles = []
        for category, articles in data.items():
            all_articles.extend(articles)

        # Return as JSON response to the browser
        return jsonify(all_articles)

    # If no index file found, return empty list
    return jsonify([])


@app.route("/api/pdfs")
def get_pdfs():
    """
    API route: returns list of all generated PDF digests.
    Used by the dashboard to show download links.
    URL: http://localhost:5000/api/pdfs
    """

    files = []

    # Find all PDF files in output folder, sorted newest first
    pdf_pattern = os.path.join(OUTPUT_FOLDER, "*.pdf")
    for f in sorted(glob.glob(pdf_pattern), reverse=True):

        # Get just the filename without folder path
        name = os.path.basename(f)

        # Get file size in KB
        size = os.path.getsize(f)
        size_kb = f"{size // 1024} KB"

        # Get file modification date (when it was created)
        mod_time = os.path.getmtime(f)
        date_str = datetime.fromtimestamp(mod_time).strftime("%d %b %Y %I:%M %p")

        # Determine category from filename
        # LawOrder_2026-05-02.pdf → Law & Order
        if "LawOrder" in name:
            category = "Law & Order"
        else:
            category = "Political"

        # Add file info to list
        files.append({
            "name":     name,
            "size":     size_kb,
            "date":     date_str,
            "category": category
        })

    # Return file list as JSON
    return jsonify(files)


@app.route("/download/<filename>")
def download(filename):
    """
    Download route: sends a PDF file to the user's browser.
    URL: http://localhost:5000/download/LawOrder_2026-05-02.pdf
    as_attachment=True forces browser to download instead of open
    """

    # Build the full file path
    file_path = os.path.join(OUTPUT_FOLDER, filename)

    # Check if file exists before trying to send
    if not os.path.exists(file_path):
        return "File not found", 404

    # Send the file as a download
    return send_file(file_path, as_attachment=True)


# This block runs only when you execute app.py directly
if __name__ == "__main__":
    # debug=True auto-reloads when you change the code
    # host="0.0.0.0" makes it accessible on your local network
    # port=5000 means visit http://localhost:5000
    app.run(debug=True, host="0.0.0.0", port=5000)
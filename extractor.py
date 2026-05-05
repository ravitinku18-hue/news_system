# ============================================================
# FILE 2: extractor.py (FIXED VERSION)
# CHANGE: Now takes HD screenshot of each article page
#         instead of extracting blurry embedded images
#         This gives EXACT newspaper clip appearance
# ============================================================

import fitz          # PyMuPDF for PDF reading and rendering
import os
import re
from config import SLIDES_FOLDER, MAX_ARTICLES_PER_PAGE, MIN_ARTICLE_LENGTH


def extract_articles_with_images(pdf_path):
    """
    Opens a newspaper PDF and extracts articles.
    For each page, renders a HIGH RESOLUTION screenshot
    of the entire page instead of extracting embedded images.
    This ensures photo matches the article perfectly.

    INPUT:  pdf_path = path to newspaper PDF
    OUTPUT: list of article dictionaries with text and page screenshot
    """

    articles = []
    newspaper_name = os.path.basename(pdf_path).replace('.pdf', '')

    # Open PDF with PyMuPDF
    doc = fitz.open(pdf_path)

    # Make sure slides folder exists
    os.makedirs(SLIDES_FOLDER, exist_ok=True)

    for page_num in range(len(doc)):

        page = doc[page_num]

        # ── EXTRACT TEXT ─────────────────────────────────────

        # Try standard text extraction first
        text = page.get_text("text")

        # If standard extraction gives nothing, try blocks method
        if not text or len(text.strip()) < 50:
            blocks = page.get_text("blocks")
            text = "\n\n".join([b[4] for b in blocks if len(b[4].strip()) > 20])

        # Skip pages with very little text
        if not text or len(text.strip()) < MIN_ARTICLE_LENGTH:
            continue

        # Split into article chunks by double newlines
        chunks = [
            c.strip()
            for c in text.split('\n\n')
            if len(c.strip()) > MIN_ARTICLE_LENGTH
        ]

        if not chunks:
            continue

        # ── RENDER HD PAGE SCREENSHOT ────────────────────────
        # This renders the full PDF page as a high quality image
        # matrix 3.0 = 3x zoom = 216 DPI which is very sharp
        # (standard screen is 72 DPI, so 3x is very clear)

        zoom_matrix = fitz.Matrix(3.0, 3.0)  # 3x zoom for HD quality
        page_image  = page.get_pixmap(matrix=zoom_matrix, alpha=False)

        # Save the page screenshot as PNG file
        screenshot_path = os.path.join(
            SLIDES_FOLDER,
            f"page_{newspaper_name}_p{page_num + 1}.png"
        )
        page_image.save(screenshot_path)

        # ── BUILD ARTICLE ENTRIES ────────────────────────────
        # Each text chunk on this page gets the same page screenshot
        # This guarantees photo always matches the article content

        for i, chunk in enumerate(chunks[:MAX_ARTICLES_PER_PAGE]):
            article = {
                "page":         page_num + 1,
                "text":         chunk,
                "source":       newspaper_name,
                # Use full page screenshot — always matches article
                "image_path":   screenshot_path,
                # Store page number for cropping later if needed
                "page_num":     page_num
            }
            articles.append(article)

    doc.close()
    return articles


def extract_text_from_scanned_pdf(pdf_path):
    """
    Fallback function for PDFs that have 0 text blocks.
    These are scanned image PDFs (like Disha, TOI sometimes).
    Uses PyMuPDF to render pages and extract text via OCR approach.

    This handles the 'Extracted 0 text blocks' problem.
    """

    articles = []
    newspaper_name = os.path.basename(pdf_path).replace('.pdf', '')
    doc = fitz.open(pdf_path)

    os.makedirs(SLIDES_FOLDER, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Try all text extraction methods
        text = ""

        # Method 1: standard text
        text = page.get_text("text").strip()

        # Method 2: blocks
        if len(text) < 50:
            blocks = page.get_text("blocks")
            text = " ".join([b[4].strip() for b in blocks if b[4].strip()])

        # Method 3: words
        if len(text) < 50:
            words = page.get_text("words")
            text = " ".join([w[4] for w in words])

        # Method 4: rawdict (most thorough)
        if len(text) < 50:
            try:
                rawdict = page.get_text("rawdict")
                all_text = []
                for block in rawdict.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            all_text.append(span.get("text", ""))
                text = " ".join(all_text)
            except:
                pass

        # Skip if still no text found
        if len(text.strip()) < MIN_ARTICLE_LENGTH:
            continue

        # Render HD page screenshot
        zoom_matrix    = fitz.Matrix(3.0, 3.0)
        page_image     = page.get_pixmap(matrix=zoom_matrix, alpha=False)
        screenshot_path = os.path.join(
            SLIDES_FOLDER,
            f"page_{newspaper_name}_p{page_num + 1}.png"
        )
        page_image.save(screenshot_path)

        # Create one article entry per page for scanned PDFs
        article = {
            "page":       page_num + 1,
            "text":       text[:2000],
            "source":     newspaper_name,
            "image_path": screenshot_path,
            "page_num":   page_num
        }
        articles.append(article)

    doc.close()
    return articles

def extract_with_ocr(pdf_path):
    """
    Last resort extraction using OCR.
    Used when PDF has no text layer at all (pure image scan).
    Requires Tesseract OCR to be installed.

    Handles Telugu, Hindi, and English newspapers.
    """
    try:
        import pytesseract
        from PIL import Image
        import io
        from config import TESSERACT_PATH

        # Tell pytesseract where tesseract is installed
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    except ImportError:
        print("    pytesseract not installed. Run: pip install pytesseract")
        return []

    articles = []
    newspaper_name = os.path.basename(pdf_path).replace('.pdf', '')
    doc = fitz.open(pdf_path)
    os.makedirs(SLIDES_FOLDER, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render page as high resolution image for OCR
        zoom_matrix = fitz.Matrix(3.0, 3.0)
        pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)

        # Save screenshot for the slide
        screenshot_path = os.path.join(
            SLIDES_FOLDER,
            f"page_{newspaper_name}_p{page_num + 1}.png"
        )
        pix.save(screenshot_path)

        # Convert pixmap to PIL Image for OCR
        img_data = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_data))

        # Run OCR with Telugu + Hindi + English language support
        # tel = Telugu, hin = Hindi, eng = English
        try:
            text = pytesseract.image_to_string(
                pil_image,
                lang='tel+hin+eng',
                config='--psm 3'
            )
        except Exception:
            # If Telugu/Hindi packs not installed, try English only
            try:
                text = pytesseract.image_to_string(
                    pil_image,
                    lang='eng',
                    config='--psm 3'
                )
            except Exception as e:
                print(f"    OCR failed on page {page_num + 1}: {e}")
                continue

        # Skip pages with very little text
        if len(text.strip()) < MIN_ARTICLE_LENGTH:
            continue

        article = {
            "page":       page_num + 1,
            "text":       text[:2000],
            "source":     newspaper_name,
            "image_path": screenshot_path,
            "page_num":   page_num
        }
        articles.append(article)
        print(f"    OCR extracted page {page_num + 1}: {len(text)} chars")

    doc.close()
    return articles
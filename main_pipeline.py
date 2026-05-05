# ============================================================
# FILE 5: main_pipeline.py (FIXED - handles scanned PDFs)
# FIXES:
#   - Tries multiple extraction methods for scanned PDFs
#   - Falls back to scanned PDF extractor if 0 blocks found
#   - Handles Disha, TOI and other image-based PDFs
# ============================================================

import os
import glob
import json

from datetime import datetime
from extractor import (
    extract_articles_with_images,
    extract_text_from_scanned_pdf,
    extract_with_ocr
)
from classifier      import classify_and_translate
from slide_generator import create_article_slide, merge_slides_to_digest
from config          import INPUT_FOLDER, OUTPUT_FOLDER, SLIDES_FOLDER


def run_pipeline():
    """
    Main pipeline controller.
    Processes all PDFs in input folder and generates digest PDFs.
    """

    today = datetime.now().strftime("%Y-%m-%d")

    print("=" * 60)
    print(f"  NEWS PIPELINE STARTING — {today}")
    print("=" * 60)

    # Create all required folders
    for folder in [INPUT_FOLDER, OUTPUT_FOLDER, SLIDES_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # Find all PDF files in input folder
    pdf_files = glob.glob(os.path.join(INPUT_FOLDER, "*.pdf"))

    if not pdf_files:
        print(f"\n  No PDFs found in '{INPUT_FOLDER}'. Please add PDFs.")
        return

    print(f"\n  Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"    - {os.path.basename(pdf)}")

    # Storage for article slides and metadata
    law_slides = []
    pol_slides  = []
    article_index = {"law_and_order": [], "political": []}
    slide_counter = 0

    # ── PROCESS EACH PDF ──────────────────────────────────────

    for pdf_path in pdf_files:

        # STEP 1: Standard text extraction
        articles = extract_articles_with_images(pdf_path)
        print(f"  Standard extraction: {len(articles)} blocks found")

        # STEP 2: Try scanned PDF method
        if len(articles) == 0:
            print(f"  Trying scanned PDF extraction...")
            articles = extract_text_from_scanned_pdf(pdf_path)
            print(f"  Scanned extraction: {len(articles)} blocks found")

        # STEP 3: Try OCR as last resort
        if len(articles) == 0:
            print(f"  Trying OCR extraction (this takes 1-2 minutes)...")
            articles = extract_with_ocr(pdf_path)
            print(f"  OCR extraction: {len(articles)} blocks found")

        # STEP 4: If still 0, skip this PDF
        if len(articles) == 0:
            print(f"  SKIPPED: Cannot extract text from this PDF.")
            continue

        # ── CLASSIFY EACH ARTICLE ──────────────────────────────

        for i, art in enumerate(articles):

            print(f"\n  Article {i+1}/{len(articles)} — classifying...", end=" ")

            # Send to Groq AI for classification and translation
            result = classify_and_translate(art['text'], art['source'])

            # Skip if AI returned nothing
            if not result:
                print("SKIPPED (AI error)")
                continue

            # Skip if not about Telangana
            if not result.get('is_telangana'):
                print("SKIPPED (not Telangana)")
                continue

            # Skip if not law & order or political
            if result.get('category') == 'other':
                print(f"SKIPPED (category: other)")
                continue

            cat = result['category']
            headline = result.get('headline_english', 'No headline')
            print(f"OK [{cat.upper()}] {headline[:50]}")

            # ── CREATE ARTICLE SLIDE PDF ───────────────────────

            slide_counter += 1
            slide_filename = f"{cat}_{today}_{slide_counter:03d}.pdf"
            slide_path     = os.path.join(SLIDES_FOLDER, slide_filename)

            # Merge article and AI result data
            full_article = {**art, **result}

            # Generate the PDF slide
            create_article_slide(full_article, slide_path)

            # ── SAVE METADATA FOR DASHBOARD ───────────────────

            meta = {
                "headline":  result.get('headline_english', ''),
                "category":  cat,
                "source":    art['source'],
                "page":      art['page'],
                "language":  result.get('language', 'English'),
                "location":  result.get('location', 'Telangana'),
                "summary":   result.get('summary_english',
                             result.get('content_english', '')[:200]),
                "slide_pdf": slide_path,
                "image":     art.get('image_path'),
                "date":      today
            }

            article_index[cat].append(meta)

            if cat == 'law_and_order':
                law_slides.append(slide_path)
            else:
                pol_slides.append(slide_path)

    # ── GENERATE FINAL DIGEST PDFs ─────────────────────────────

    print(f"\n{'=' * 60}")
    print("  GENERATING FINAL DIGEST PDFs")
    print(f"{'=' * 60}")

    if law_slides:
        law_output = os.path.join(OUTPUT_FOLDER, f"LawOrder_{today}.pdf")
        merge_slides_to_digest(law_slides, "law_and_order", law_output)
    else:
        print("  No Law & Order articles found today.")

    if pol_slides:
        pol_output = os.path.join(OUTPUT_FOLDER, f"Political_{today}.pdf")
        merge_slides_to_digest(pol_slides, "political", pol_output)
    else:
        print("  No Political articles found today.")

    # Save article index JSON for dashboard
    index_path = os.path.join(OUTPUT_FOLDER, f"index_{today}.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(article_index, f, ensure_ascii=False, indent=2)

    print(f"\n  Index saved: {index_path}")
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Law & Order : {len(law_slides)} articles")
    print(f"  Political   : {len(pol_slides)} articles")
    print(f"  Output      : {OUTPUT_FOLDER}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    run_pipeline()
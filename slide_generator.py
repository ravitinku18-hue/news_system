# ============================================================
# FILE 4: slide_generator.py (COMPLETE FRESH VERSION)
# PURPOSE: Creates bilingual PDF slides for each article
#          Telugu/Hindi on LEFT, English on RIGHT
#          Matches DGP digest format exactly
# ============================================================

# reportlab library for creating PDF files from scratch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,   # main PDF document builder
    Paragraph,           # text block with styling
    Spacer,              # empty vertical space
    Image as RLImage,    # image block inside PDF
    HRFlowable,          # horizontal divider line
    Table,               # two column table for bilingual layout
    TableStyle           # styling rules for tables
)
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# datetime for getting today's date
from datetime import datetime

# os for file path operations
import os

# Import folder paths from config
from config import SLIDES_FOLDER, OUTPUT_FOLDER


# ============================================================
# FUNCTION 1: create_article_slide
# Creates one PDF slide for one article
# ============================================================

def create_article_slide(article_data, output_pdf_path):
    """
    Creates a single bilingual PDF slide for one article.

    For Telugu or Hindi articles:
      LEFT COLUMN  = original language content
      RIGHT COLUMN = English translation

    For English articles:
      SINGLE COLUMN = full English content

    INPUT:  article_data    = dictionary with all article fields
            output_pdf_path = file path where to save this slide
    OUTPUT: output_pdf_path string
    """

    # ── EXTRACT DATA FROM ARTICLE DICTIONARY ────────────────

    # Language of the original article
    lang = article_data.get('language', 'English')

    # Category: law_and_order or political
    category = article_data.get('category', 'political')

    # Name of the newspaper
    source = article_data.get('source', 'Unknown')

    # Page number in the newspaper
    page = article_data.get('page', '')

    # Path to newspaper photo image (may be None)
    image_path = article_data.get('image_path')

    # Today's date formatted as DD-MM-YYYY
    date_str = datetime.now().strftime("%d-%m-%Y")

    # ── SET COLORS BASED ON CATEGORY ────────────────────────

    if category == 'law_and_order':
        # Red theme for Law and Order
        accent_color = colors.HexColor('#C0392B')
        cat_label = "LAW & ORDER"
    else:
        # Dark blue theme for Political
        accent_color = colors.HexColor('#1A3A6B')
        cat_label = "POLITICAL"

    # ── CREATE PDF DOCUMENT ──────────────────────────────────

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        topMargin=1.2*cm,
        bottomMargin=1.2*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )

    # story is the list of elements added to PDF in order
    story = []

    # ── DEFINE TEXT STYLES ───────────────────────────────────

    # Style for category header line at top
    cat_style = ParagraphStyle(
        'cat',
        fontSize=9,
        textColor=accent_color,
        fontName='Helvetica-Bold',
        spaceAfter=2
    )

    # Style for date and source info line
    meta_style = ParagraphStyle(
        'meta',
        fontSize=8,
        textColor=colors.grey,
        fontName='Helvetica',
        spaceAfter=5
    )

    # Style for main English headline (large bold)
    headline_en_style = ParagraphStyle(
        'hl_en',
        fontSize=15,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=4,
        leading=20
    )

    # Style for original language headline (slightly smaller)
    headline_orig_style = ParagraphStyle(
        'hl_orig',
        fontSize=12,
        fontName='Helvetica',
        textColor=colors.HexColor('#444444'),
        spaceAfter=8,
        leading=18
    )

    # Style for column header labels (Telugu, English)
    col_label_style = ParagraphStyle(
        'col_label',
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_CENTER
    )

    # Style for original language body text
    orig_body_style = ParagraphStyle(
        'orig_body',
        fontSize=10,
        leading=16,
        fontName='Helvetica',
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_JUSTIFY,
        spaceAfter=4
    )

    # Style for English body text
    eng_body_style = ParagraphStyle(
        'eng_body',
        fontSize=10,
        leading=16,
        fontName='Helvetica',
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_JUSTIFY,
        spaceAfter=4
    )

    # Style for single column English only articles
    single_body_style = ParagraphStyle(
        'single_body',
        fontSize=11,
        leading=18,
        fontName='Helvetica',
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    # Style for footer text at bottom
    footer_style = ParagraphStyle(
        'footer',
        fontSize=7,
        textColor=colors.grey,
        fontName='Helvetica',
        alignment=TA_CENTER
    )

    # ── BUILD SLIDE CONTENT ──────────────────────────────────

    # 1. Category header line (red or blue text)
    story.append(
        Paragraph(
            f"TELANGANA POLICE — {cat_label} NEWS DIGEST",
            cat_style
        )
    )

    # 2. Date, source, page number line
    story.append(
        Paragraph(
            f"Date: {date_str} &nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Source: {source} &nbsp;&nbsp;|&nbsp;&nbsp; Page {page}",
            meta_style
        )
    )

    # 3. Thick colored horizontal divider line
    story.append(
        HRFlowable(width="100%", thickness=2, color=accent_color)
    )
    story.append(Spacer(1, 0.3*cm))

    # 4. English headline (always shown at top)
    story.append(
        Paragraph(
            article_data.get('headline_english', 'No Headline'),
            headline_en_style
        )
    )

    # 5. Original language headline (only for Telugu or Hindi)
    if lang != 'English':
        story.append(
            Paragraph(
                article_data.get('headline_original', ''),
                headline_orig_style
            )
        )

    # 6. Thin grey separator line below headlines
    story.append(
        HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey)
    )
    story.append(Spacer(1, 0.3*cm))

    # 7. Newspaper photo if available and file exists on disk
    if image_path and os.path.exists(image_path):
        try:
            # Add photo centered with fixed width and height
            story.append(
                RLImage(image_path, width=12*cm, height=6*cm)
            )
            story.append(Spacer(1, 0.3*cm))
            story.append(
                HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey)
            )
            story.append(Spacer(1, 0.2*cm))
        except Exception as e:
            # Skip image if it fails to load
            print(f"    Image skipped: {e}")

    # 8. BILINGUAL CONTENT SECTION
    if lang == 'English':

        # ── ENGLISH ONLY: single full width column ───────────
        story.append(
            Paragraph(
                article_data.get('content_english', ''),
                single_body_style
            )
        )

    else:

        # ── BILINGUAL: two columns side by side ──────────────
        # Get the content texts from article data
        orig_text = article_data.get('content_original', '')
        eng_text  = article_data.get('content_english', '')

        # ── CREATE COLUMN HEADER LABELS ──────────────────────

        # Left column label showing original language name
        # Uses accent color background (red or blue)
        orig_label_cell = Table(
            [[Paragraph(f"{lang}", col_label_style)]],
            colWidths=[8.5*cm]
        )
        orig_label_cell.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), accent_color),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ]))

        # Right column label showing English
        # Uses dark grey background
        eng_label_cell = Table(
            [[Paragraph("English", col_label_style)]],
            colWidths=[8.5*cm]
        )
        eng_label_cell.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ]))

        # ── CREATE HEADER ROW WITH BOTH LABELS SIDE BY SIDE ─
        header_row = Table(
            [[orig_label_cell, eng_label_cell]],
            colWidths=[8.5*cm, 8.5*cm]
        )
        header_row.setStyle(TableStyle([
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        # Add header row to slide
        story.append(header_row)

        # ── CREATE TWO COLUMN CONTENT TABLE ──────────────────
        content_table = Table(
            [[
                # Left cell: original language text
                Paragraph(orig_text, orig_body_style),

                # Right cell: English translation
                Paragraph(eng_text, eng_body_style)
            ]],
            colWidths=[8.5*cm, 8.5*cm]
        )

        content_table.setStyle(TableStyle([
            # Align all text to top of cell
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),

            # Padding inside each cell
            ('LEFTPADDING',   (0, 0), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),

            # Vertical divider line between columns
            ('LINEAFTER',     (0, 0), (0, -1), 1, colors.HexColor('#cccccc')),

            # Light grey background for original language column
            ('BACKGROUND',    (0, 0), (0, -1), colors.HexColor('#fafafa')),

            # White background for English column
            ('BACKGROUND',    (1, 0), (1, -1), colors.white),

            # Thin border around the whole table
            ('BOX',           (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))

        # Add content table to slide
        story.append(content_table)

    # 9. Footer section
    story.append(Spacer(1, 0.4*cm))
    story.append(
        HRFlowable(width="100%", thickness=1, color=accent_color)
    )
    story.append(
        Paragraph(
            "CONFIDENTIAL — For DGP Office Only &nbsp;|&nbsp; Alpha Stanzasoft",
            footer_style
        )
    )

    # Build and save the PDF file to disk
    doc.build(story)

    # Return path so caller knows where file was saved
    return output_pdf_path


# ============================================================
# FUNCTION 2: create_cover_page
# Creates the front cover page of the digest
# ============================================================

def create_cover_page(category, article_count):
    """
    Creates the cover page matching your DGP digest sample format.

    INPUT:  category      = law_and_order or political
            article_count = number of articles in this digest
    OUTPUT: file path of the saved cover page PDF
    """

    # Save cover page temporarily in slides folder
    cover_path = os.path.join(SLIDES_FOLDER, f"cover_{category}.pdf")

    # Create the cover PDF document
    doc = SimpleDocTemplate(
        cover_path,
        pagesize=A4,
        topMargin=4*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )

    # Format today's date
    date_str = datetime.now().strftime("%d-%m-%Y")

    # Set label and color based on category
    cat_label = "Law & Order" if category == "law_and_order" else "Political"
    accent = (
        colors.HexColor('#C0392B')   # red for law and order
        if category == 'law_and_order'
        else colors.HexColor('#1A3A6B')  # blue for political
    )

    # Build cover page content list
    story = [

        Spacer(1, 2*cm),

        # Main title
        Paragraph(
            "TELANGANA STATE POLICE",
            ParagraphStyle(
                'ct',
                fontSize=24,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#1a1a2e'),
                alignment=TA_CENTER,
                spaceAfter=6
            )
        ),

        # Subtitle
        Paragraph(
            "TODAY'S NEWS DIGEST",
            ParagraphStyle(
                'cs',
                fontSize=16,
                fontName='Helvetica',
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=10
            )
        ),

        # Thick colored divider line
        HRFlowable(width="70%", thickness=3, color=accent),
        Spacer(1, 0.5*cm),

        # Category name
        Paragraph(
            f"--- {cat_label} ---",
            ParagraphStyle(
                'cc',
                fontSize=20,
                fontName='Helvetica-Bold',
                textColor=accent,
                alignment=TA_CENTER,
                spaceAfter=20
            )
        ),

        # Date line
        Paragraph(
            f"Date: {date_str}",
            ParagraphStyle(
                'cd',
                fontSize=13,
                fontName='Helvetica',
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=4
            )
        ),

        # Classification line
        Paragraph(
            "Classification: CONFIDENTIAL",
            ParagraphStyle(
                'cl',
                fontSize=13,
                fontName='Helvetica',
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=4
            )
        ),

        # Article count line
        Paragraph(
            f"Total Articles: {article_count}",
            ParagraphStyle(
                'ca',
                fontSize=13,
                fontName='Helvetica',
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=4
            )
        ),

        Spacer(1, 2*cm),

        # Confidential warning in red
        Paragraph(
            "CONFIDENTIAL — For DGP Office Only",
            ParagraphStyle(
                'cf',
                fontSize=11,
                fontName='Helvetica-Bold',
                textColor=colors.red,
                alignment=TA_CENTER,
                spaceAfter=6
            )
        ),

        # Powered by line
        Paragraph(
            "Automated News Digest — Powered by Alpha Stanzasoft",
            ParagraphStyle(
                'cp',
                fontSize=9,
                fontName='Helvetica',
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ),
    ]

    # Build and save the cover page
    doc.build(story)

    return cover_path


# ============================================================
# FUNCTION 3: merge_slides_to_digest
# Combines all article slides into one final PDF
# ============================================================

def merge_slides_to_digest(slide_paths, category, output_path):
    """
    Merges all individual article slide PDFs into one digest PDF.
    Adds the cover page at the very beginning.

    INPUT:  slide_paths = list of article PDF file paths
            category    = law_and_order or political
            output_path = where to save the final merged PDF
    """

    # Import PyPDF2 for merging multiple PDFs into one
    from PyPDF2 import PdfMerger

    # Create merger object
    merger = PdfMerger()

    # First create and add the cover page
    cover_path = create_cover_page(category, len(slide_paths))
    merger.append(cover_path)

    # Add each article slide PDF one by one
    for slide_path in slide_paths:

        # Only add the file if it actually exists on disk
        if os.path.exists(slide_path):
            merger.append(slide_path)
        else:
            print(f"    Warning: slide not found: {slide_path}")

    # Write the final combined PDF to the output path
    merger.write(output_path)

    # Close merger to free memory
    merger.close()

    print(f"  Digest saved: {output_path} ({len(slide_paths)} articles)")
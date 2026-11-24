
from pathlib import Path
import shutil
import re
import pymupdf
import pytesseract
from PIL import Image


SENSITIVE_MARKER = "WALLED_SENSITIVE"

tesseract_path = (
    shutil.which("tesseract")
    or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = tesseract_path


def contains_sensitive_ocr(text):
    normalized_text = re.sub(r"\s*_\s*", "_", text)
    return SENSITIVE_MARKER in normalized_text


def inspect_text_file(file_path):
    try:
        content = Path(file_path).read_text(
            encoding="utf-8-sig"
        )

        return SENSITIVE_MARKER in content

    except Exception as error:
        print(f"[Guard] TXT inspection failed: {error}")
        return None


def inspect_pdf_file(file_path):
    try:
        with pymupdf.open(file_path) as document:

            for page in document:

                # Direct text extraction
                text = page.get_text()

                if SENSITIVE_MARKER in text:
                    return True

                # OCR for scanned pages or embedded images
                if not text.strip() or page.get_images():

                    pixmap = page.get_pixmap(
                        dpi=200,
                        colorspace=pymupdf.csRGB,
                        alpha=False
                    )

                    image = Image.frombytes(
                        "RGB",
                        (pixmap.width, pixmap.height),
                        pixmap.samples
                    )

                    extracted_text = pytesseract.image_to_string(
                        image,
                        timeout=30
                    )

                    if contains_sensitive_ocr(extracted_text):
                        return True

        return False

    except Exception as error:
        print(f"[Guard] PDF inspection failed: {error}")
        return None


def inspect_image_file(file_path):
    try:
        with Image.open(file_path) as image:

            text = pytesseract.image_to_string(
                image,
                timeout=30
            )

            return contains_sensitive_ocr(text)

    except Exception as error:
        print(f"[Guard] Image inspection failed: {error}")
        return None


def inspect_file(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        return inspect_text_file(file_path)

    if extension == ".pdf":
        return inspect_pdf_file(file_path)

    if extension in (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".webp"
    ):
        return inspect_image_file(file_path)

    print(f"[Guard] Unsupported file type: {extension}")

    return None

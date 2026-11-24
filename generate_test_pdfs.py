
from pathlib import Path
import pymupdf

Path("tests").mkdir(exist_ok=True)


def create_pdf(file_path, text):
    with pymupdf.open() as document:
        page = document.new_page()

        page.insert_text(
            (72, 72),
            text,
            fontsize=14
        )

        document.save(file_path)

    print(f"Created: {file_path}")


create_pdf(
    "tests/safe.pdf",
    "This is a normal PDF document."
)

create_pdf(
    "tests/sensitive.pdf",
    "This document contains WALLED_SENSITIVE."
)

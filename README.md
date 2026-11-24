# Sensitive Upload Guard

A standalone Windows desktop application built using Python and PySide6 to detect sensitive content in ChatGPT and Perplexity before submission through supported input methods.

This project was developed as part of the Walled AI technical screening assignment.

## Features

- Detects the `WALLED_SENSITIVE` keyword in text prompts, TXT files, PDFs and images.
- Displays a native confirmation dialog with Continue and Cancel options when sensitive content is detected.
- Allows safe content without confirmation.
- Changes AI-generated response text color to green.
- Restricts drag-and-drop and clipboard file uploads to prevent common inspection bypasses.
- Works without browser extensions or plugins.

## Tech Stack

- Python
- PySide6 and Qt WebEngine
- JavaScript
- QWebChannel
- PyMuPDF
- Tesseract OCR
- Pillow

## Project Structure

| File | Description |
|---|---|
| `main.py` | Desktop application and browser setup |
| `approval_bridge.py` | Native confirmation dialog |
| `file_inspector.py` | Text, PDF and image inspection |
| `response_styler.py` | AI response color customization |
| `upload_guard.py` | Drag-and-drop and clipboard restrictions |

## Setup and Installation

Clone the repository:

```bash
git clone https://github.com/Jahra-MD/SensitiveUploadGuardDesktop.git
cd SensitiveUploadGuardDesktop
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Install Tesseract OCR:

```powershell
winget install --id UB-Mannheim.TesseractOCR -e
```

## Run the Application

```bash
python main.py
```

The application opens a desktop window with separate tabs for ChatGPT and Perplexity.

## How It Works

Text prompts are checked using JavaScript before supported submission events. QWebChannel connects the browser with Python to display the native confirmation dialog.

Files selected through the attachment button are inspected locally using text extraction or OCR. If sensitive content is detected, the user can continue or cancel the upload.

AI response colors are updated using JavaScript and MutationObserver.

## Testing

Try submitting a normal prompt and a prompt containing `WALLED_SENSITIVE`.

Similarly, upload TXT, PDF and image files with and without the sensitive keyword. Verify the Continue and Cancel actions on both websites.

## Limitations

- Protection is limited to the embedded browser.
- Prompt detection depends on website DOM structures and supported submission events.
- OCR accuracy depends on image quality.
- Drag-and-drop and clipboard file uploads are blocked instead of inspected.
- Network-level inspection is not implemented.

## Demo

Demo video link: To be added.

## Author

Jahra Mohammed

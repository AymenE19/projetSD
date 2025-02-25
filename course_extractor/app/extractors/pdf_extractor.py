import os
import requests
import fitz  # PyMuPDF

def download_pdf(url, output_dir="temp_downloads"):
    """Download a PDF from a URL and save it to a temporary directory."""
    os.makedirs(output_dir, exist_ok=True)
    file_name = os.path.basename(url)
    file_path = os.path.join(output_dir, file_name)

    try:
        # Stream the PDF to disk in chunks (avoids loading the entire file into RAM)
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)

        print(f"PDF temporarily downloaded: {file_path}")
        return file_path

    except Exception as e:
        print(f"Download failed: {e}")
        return None


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file and delete the file afterward."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        print("Text extracted successfully.")
        return text

    except Exception as e:
        print(f"Extraction failed: {e}")
        return None

    finally:
        # Clean up: Delete the PDF after extraction to save disk space
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"Deleted temporary PDF: {pdf_path}")

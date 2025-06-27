import os
import base64
import logging
from mistralai import Mistral
from dotenv import load_dotenv
import re

load_dotenv()
logger = logging.getLogger(__name__)

EXTENSIONS = (".pdf", ".docx", ".pptx")
SKIP_PREFIXES = ("~$", ".")


def encode_pdf(pdf_path: str) -> str | None:
    """Encode a PDF file to a Base64 string."""
    try:
        with open(pdf_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
    except Exception as e:
        logger.error(f"Error encoding {pdf_path}: {e}")
    return None


def parse_pdf(pdf_path: str) -> dict | None:
    b64 = encode_pdf(pdf_path)
    if b64 is None:
        return None

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        logger.error("Missing MISTRAL_API_KEY in environment")
        return None

    client = Mistral(api_key=api_key)
    try:
        return client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{b64}",
            },
            include_image_base64=True,
        )
    except Exception as e:
        logger.error(f"OCR processing failed for {pdf_path}: {e}")
        return None


def parse_pdfs_in_folder(folder_path: str) -> dict[str, dict]:
    results: dict[str, dict] = {}
    all_files = os.listdir(folder_path)
    for x in all_files:
        print(x)
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith(EXTENSIONS):
            continue
        if any(fname.startswith(p) for p in SKIP_PREFIXES):
            print(f"Skipping temporary/hidden file: {fname}")
            continue
        full_path = os.path.join(folder_path, fname)
        results[fname] = parse_pdf(full_path)
    return results


if __name__ == "__main__":
    folder = "/Users/weihao/Library/CloudStorage/GoogleDrive-weihao.gu1994@gmail.com/.shortcut-targets-by-id/1-sEEs61X3q7AG8MV6y6wlX637KLOnMs4/all_docs/953"
    responses = parse_pdfs_in_folder(folder)
    for fname, resp in responses.items():
        print(f"{fname} → {resp}\n")

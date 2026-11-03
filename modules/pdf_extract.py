
import pymupdf
import easyocr
import numpy as np

from PIL import Image
from io import BytesIO


# Initialize OCR reader only when required
reader = None


def get_ocr_reader():
    global reader

    if reader is None:
        print("Initializing EasyOCR...")
        reader = easyocr.Reader(['en'], gpu=False)

    return reader


def extract_pdf_text(pdf_file, on_ocr_detected=None):

    # Open PDF
    if isinstance(pdf_file, str):
        pdf = pymupdf.open(pdf_file)
    else:
        pdf = pymupdf.open(
            stream=pdf_file.getvalue(),
            filetype="pdf"
        )

    extracted_text = ""
    ocr_warning_shown = False

    try:
        print(f"\nTotal pages: {len(pdf)}")

        # Process each page
        for page_number, page in enumerate(pdf, start=1):

            print(f"\nProcessing page {page_number}...")

            # STEP 1: Try normal text extraction
            text = page.get_text("text").strip()

            # STEP 2: Check whether OCR is required
            if len(text) < 30:

                print("Scanned/Image-based page detected.")

                # Show Streamlit warning only once
                if not ocr_warning_shown:

                    if on_ocr_detected:
                        on_ocr_detected()

                    ocr_warning_shown = True

                print("Applying EasyOCR...")

                # Convert PDF page into image
                pix = page.get_pixmap(dpi=250)

                image = Image.open(
                    BytesIO(pix.tobytes("png"))
                ).convert("RGB")

                # Convert image into NumPy array
                image_array = np.array(image)

                # STEP 3: Extract text using EasyOCR
                ocr_reader = get_ocr_reader()

                results = ocr_reader.readtext(
                    image_array,
                    detail=0,
                    paragraph=True
                )

                text = "\n".join(results)

                print("OCR extraction completed.")

            else:
                print("Normal PDF text extracted successfully.")

            # STEP 4: Store extracted page text
            extracted_text += (
                f"\n--- Page {page_number} ---\n"
                f"{text}\n"
            )

    finally:
        pdf.close()

    return extracted_text



if __name__ == "__main__":

    pdf_path = "resume.pdf"

    print("\n========== PDF EXTRACTION STARTED ==========")

    result = extract_pdf_text(pdf_path)

    print("\n========== EXTRACTED TEXT ==========")
    print(result)

    print("\n========== EXTRACTION SUMMARY ==========")
    print("Total characters:", len(result))
    print("Extraction completed!")

from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """
    Reads a PDF file and extracts its text.
    """

    try:
        reader = PdfReader(file_path)

        extracted_text = ""

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if text:
                extracted_text += f"\n--- Page {page_number} ---\n"
                extracted_text += text

        if not extracted_text.strip():
            return "No readable text was found in this PDF."

        return extracted_text

    except Exception as error:
        return f"Error reading PDF: {error}"
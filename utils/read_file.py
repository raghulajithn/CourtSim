from io import BytesIO
import fitz  # PyMuPDF
from docx import Document


def extract_text_from_file(filename: str, file: BytesIO) -> str:
    filename = filename.lower()
    content = file.read()

    if filename.endswith(".pdf"):
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text or "[No text found in PDF]"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    elif filename.endswith(".txt"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return "Cannot decode TXT file as UTF-8."

    elif filename.endswith(".docx"):
        try:
            doc = Document(BytesIO(content))
            paragraphs = [para.text for para in doc.paragraphs]
            return "\n".join(paragraphs) or "[No text found in DOCX]"
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    else:
        return "Unsupported file type. Please upload PDF, TXT, or DOCX."

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from langchain.schema import Document


def extract_text_from_pdf(file_path: str) -> list[str]:
    doc = fitz.open(file_path)
    chunks = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            chunks.extend(text.strip().split("\n\n"))
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def extract_images_from_pdf(file_path: str) -> list[Image.Image]:
    images = []
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images


def ocr_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)


def multimodal_ingestion(file_path: str) -> list[Document]:
    documents = []

    # Testo PDF
    text_chunks = extract_text_from_pdf(file_path)
    for chunk in text_chunks:
        documents.append(Document(page_content=chunk, metadata={"source": "pdf_text"}))

    # Immagini + OCR
    images = extract_images_from_pdf(file_path)
    for img in images:
        ocr_result = ocr_image(img)
        if ocr_result.strip():
            documents.append(
                Document(
                    page_content=ocr_result.strip(),
                    metadata={"source": "pdf_image_ocr"},
                )
            )

    return documents

from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import json
import io
import base64
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import os



from pydantic import BaseModel, Field
from typing import List

class InvoiceDetails(BaseModel):
    seller_company_name: str = Field(description='Name of the seller company')
    receiver_company: str = Field(description='Name of the receiver company')
    description: List[str] = Field(description='List of product descriptions')
    incoterms: str = Field(description='International commercial terms (Incoterms) for shipping')
    delivery_terms: str = Field(description='Terms of delivery for the invoice')
    invoice_date: str = Field(description='Date of the invoice in YYYY-MM-DD format')
    invoice_number: str = Field(description='Unique identifier for the invoice')
    net_amount: float = Field(description='Net amount before taxes')
    vat_amount: List[float] = Field(description='List of VAT amounts for each item')
    vat_rate: List[float] = Field(description='List of VAT rates for each item as percentages')
    total_amount: float = Field(description='Total amount including VAT')


def structured_extract(text: str) -> dict:
    client = OpenAI()
    messages = [
      {"role": "system", "content": "Extract the Invoice information."},
      {"role": "user", "content": text},
    ]
    
    response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages = messages,
    response_format=InvoiceDetails,
    )

    return_json = json.loads(response.choices[0].message.content)

    return return_json




def image_to_text(images: Image.Image):

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # pytesseract.pytesseract.tesseract_cmd = r"D:\AI tool\Tesseract-OCR\tesseract.exe"
    print('Start -- Extracting text from image...')
    img_bytes = io.BytesIO()
    images.save(img_bytes, format='PNG')  
    text = pytesseract.image_to_string(Image.open(img_bytes))
    print('End -- Extracting text from image\n\n')
    return text


def pdf_to_image(pdf_files: list, dpi: int= 300):
    '''
    Convert a list of uploaded PDF or JPG files into images.

    Args: 
        pdf_files: A list of Streamlit UploadedFile objects, 
                          which can be PDF or JPG files.
        dpi: The desired resolution for converting PDF pages 
                             to images, in dots per inch. Default is 300.

    Raises:
        ValueError: If the input file type is not supported (not PDF or JPG).

    Returns:
        list of list of PIL.Image.Image: A list containing lists of PIL Image 
                                         objects for each input PDF file.
                                         For each PDF file, there is a list of images, 
                                         one for each page. 
    '''

    pdf_images = []
    for pdf_file in pdf_files:
        if pdf_file.type == "image/jpeg":
            img = Image.open(pdf_file)
            pdf_images.append([img])
            
        elif pdf_file.type == "application/pdf":
            pdf_bytes = pdf_file.read()  # Read the uploaded file as bytes
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                zoom = dpi / 72  # 72 is the default DPI of the PDF
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            pdf_images.append(images)

        else:
            print(f'The input files type is unacceptable {pdf_file.type}')
    return pdf_images
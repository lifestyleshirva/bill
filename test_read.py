import pdfplumber

pdf_path = r"D:\bill\BILL.pdf"

with pdfplumber.open(pdf_path) as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""

print("----- Extracted Text Start -----")
print(text)
print("----- Extracted Text End -----")

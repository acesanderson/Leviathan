import PyPDF2

filename = "/Users/bianders/Downloads/comptia-state-of-the-tech-workforce-2024.pdf"

def convert_pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Example usage
pdf_file = filename
text_content = convert_pdf_to_text(pdf_file)

with open('comptia.txt', 'w') as file:
    file.write(text_content)


import PyPDF2
import sys

def extract_pdf_text(filename):
    try:
        with open(filename, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
        return text
    except Exception as e:
        return f'Error reading {filename}: {str(e)}'

# Extract text from all PDFs
for pdf in ['HLD.pdf', 'LDL.pdf', 'PRM.pdf']:
    print(f'=== {pdf} ===')
    text = extract_pdf_text(pdf)
    print(text[:3000])  # First 3000 characters
    print('\n' + '='*80 + '\n')

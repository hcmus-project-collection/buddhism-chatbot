from pathlib import Path

from docling.document_converter import DocumentConverter

base_path = "docling/pdfs"
all_pdf_files = Path(base_path).glob("*.pdf")

for pdf_file in all_pdf_files:
    converter = DocumentConverter()
    result = converter.convert(pdf_file)
    print(result.document.export_to_markdown())

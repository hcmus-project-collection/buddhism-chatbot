from pathlib import Path

from docling.document_converter import DocumentConverter

base_path = "docling/pdfs"
all_pdf_files = Path(base_path).glob("*.pdf")

for pdf_file in all_pdf_files:
    converter = DocumentConverter()
    result = converter.convert(pdf_file)
    markdown_content = result.document.export_to_markdown()
    output_path = pdf_file.with_suffix('.md')
    with Path(output_path).open("w", encoding="utf-8") as f:
        f.write(markdown_content)

from docling.document_converter import DocumentConverter
from pathlib import Path

exam_dir     = Path(__file__).parent.parent.parent / "Exams" / "english" / "AL"
pdf_file     = exam_dir / "LC002ALP100EV_2024.pdf"

source =  pdf_file 
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"

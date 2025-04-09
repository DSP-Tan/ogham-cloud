import fitz  

def extract_7th_page(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    if len(doc) < 7:
        print("The PDF has fewer than 7 pages.")
        return
    
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=6, to_page=6)  # 7th page (0-based index)
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()
    print(f"Extracted 7th page saved as {output_pdf}")

# Example usage
input_pdf = "LC002ALP100EV_2024.pdf"
output_pdf = "page7.pdf"
extract_7th_page(input_pdf, output_pdf)
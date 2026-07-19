import os
from pypdf import PdfReader

def extract_text_from_pdf():
    pdf_path = os.path.join("docs", "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf")
    output_path = os.path.join("docs", "extracted_pdf_text.txt")
    
    if not os.path.exists(pdf_path):
        print(f"Error: No se encontró el archivo PDF en {pdf_path}")
        return False
        
    print(f"Leyendo el archivo PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Total de páginas: {total_pages}")
    
    extracted_text = []
    for i, page in enumerate(reader.pages):
        page_num = i + 1
        text = page.extract_text()
        extracted_text.append(f"--- PÁGINA {page_num} ---\n")
        extracted_text.append(text)
        extracted_text.append("\n\n")
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(extracted_text)
        
    print(f"Texto extraído guardado exitosamente en: {output_path}")
    return True

if __name__ == "__main__":
    extract_text_from_pdf()

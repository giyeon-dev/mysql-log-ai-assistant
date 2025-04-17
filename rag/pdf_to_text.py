# pdf_to_text.py
import pdfplumber  # type: ignore

def extract_text_from_pdf(pdf_path: str, output_txt_path: str):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    with open(output_txt_path, "w") as f:
        f.write(full_text)

    print(f"✅ Text extracted and saved to: {output_txt_path}")


# 예시 실행
if __name__ == "__main__":
    extract_text_from_pdf("MYSQL8.4_tuning_guide.pdf", "MYSQL8.4_tuning_guide.txt")

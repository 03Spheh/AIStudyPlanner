from app.pdf_reader import extract_text_from_pdf


pdf_path = input("Enter the full path of your PDF: ")

text = extract_text_from_pdf(pdf_path)

print("\n==============================")
print("EXTRACTED PDF TEXT")
print("==============================")

print(text[:5000])
import os
from docx import Document


def convert_docx_to_txt(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        if file.endswith(".docx"):
            input_file = os.path.join(input_dir, file)
            output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.txt")

            try:
                doc = Document(input_file)
                with open(output_file, 'w', encoding='utf-8') as txt_file:
                    for para in doc.paragraphs:
                        txt_file.write(para.text + "\n")
                print(f"Converted: {file} → {os.path.basename(output_file)}")
            except Exception as e:
                print(f"Failed to convert {file}: {e}")


if __name__ == "__main__":
    input_dir = os.getcwd()  # Set input to the current working directory
    output_dir = os.path.join(os.getcwd(), "output_txt")  # Save to "output_txt" in the same directory

    convert_docx_to_txt(input_dir, output_dir)

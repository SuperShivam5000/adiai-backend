import base64
import tempfile
import textract
import os

def extract_text_from_base64(b64data_with_filename: str) -> str:
    """Decode base64 file (with *filename suffix), extract text using textract."""
    tmp_file_path = None
    try:
        if '*' not in b64data_with_filename:
            raise ValueError("Missing filename in base64 string. Format should be: base64*filename.ext")

        b64data, filename = b64data_with_filename.rsplit('*', 1)
        ext = os.path.splitext(filename)[1] or ".bin"

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(base64.b64decode(b64data))
            tmp_file_path = tmp_file.name
            print(tmp_file_path)

        text = textract.process(tmp_file_path).decode('utf-8', errors='ignore')
        return f"[File: {filename}]\n{text.strip()}"

    except Exception as e:
        print(f"Failed to extract text: {e}")
        return f"[File: {filename}]\n<Failed to extract text>"

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception as e:
                print(f"Failed to delete temp file: {e}")

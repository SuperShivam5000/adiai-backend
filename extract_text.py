import base64
import tempfile
import textract
import os

def extract_text_from_base64(b64data: str) -> str:
    """Decode base64 file, extract text using textract, then delete."""
    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(base64.b64decode(b64data))
            tmp_file_path = tmp_file.name

        text = textract.process(tmp_file_path)
        return text.decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"Failed to extract text: {e}")
        return ""

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception as e:
                print(f"Failed to delete temp file: {e}")

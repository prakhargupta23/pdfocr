from flask import Flask, request, jsonify
import base64
import tempfile
import os
import ocrmypdf
from pypdf import PdfReader

app = Flask(__name__)

def process_pdf_base64(pdf_base64: str) -> str:
    try:
        print("[DEBUG] Received PDF data (first 100 chars):", pdf_base64[:100])
        
        if not pdf_base64:
            print("[ERROR] Empty input received")
            return "Empty input received"

        # # Clean base64 string if it has data URL prefix
        # if pdf_base64.startswith('data:application/pdf;base64,'):
        #     pdf_base64 = pdf_base64.split(',')[1]

        # Decode Base64
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
        except Exception as e:
            print(f"[ERROR] Base64 decoding failed: {str(e)}")
            return f"Base64 decoding failed: {str(e)}"

        # Create temp input file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
                temp_input.write(pdf_bytes)
                input_path = temp_input.name
            print(f"[DEBUG] Temporary input file created at: {input_path}")
        except Exception as e:
            print(f"[ERROR] Temp file creation failed: {str(e)}")
            return f"Temp file creation failed: {str(e)}"

        # Define output path
        output_path = os.path.join(tempfile.gettempdir(), 'outputocr.pdf')
        print(f"[DEBUG] Output will be saved to: {output_path}")

        # Perform OCR
        try:
            ocrmypdf.ocr(input_path, output_path, deskew=True, force_ocr=True)
            print("[DEBUG] OCR completed successfully")
        except Exception as e:
            print(f"[ERROR] OCR processing failed hello2: {str(e)}")
            if os.path.exists(input_path):
                os.unlink(input_path)
            return f"OCR processing failed hello: {str(e)}"

        # Extract text
        extracted_text = ""
        try:
            reader = PdfReader(output_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
            print("[DEBUG] Text extraction completed")
        except Exception as e:
            print(f"[ERROR] Text extraction failed: {str(e)}")
            return f"Text extraction failed: {str(e)}"
        finally:
            # Clean up
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

        return extracted_text.strip()

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        # Clean up if paths exist
        if 'input_path' in locals() and os.path.exists(input_path):
            os.unlink(input_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.unlink(output_path)
        return f"An unexpected error occurred: {str(e)}"

@app.route('/ocr', methods=['POST'])
def ocr_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        print("[DEBUG] Received request data:", data.keys())
        
        pdf_base64 = data.get("pdfBase64", "")
        if not pdf_base64:
            return jsonify({"error": "Missing pdfBase64 field"}), 400

        extracted_text = process_pdf_base64(pdf_base64)
        
        if extracted_text.startswith("Error"):
            return jsonify({"error": extracted_text}), 500
            
        return jsonify({
            "text": extracted_text,
            "status": "success"
        })

    except Exception as e:
        print(f"[ERROR] Server error: {str(e)}")
        return jsonify({
            "error": f"Server error: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

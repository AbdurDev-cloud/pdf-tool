from flask import Flask, request, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        if file:
            # Save uploaded file
            input_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(input_path)

            # Example: Convert PDF to text using Poppler
            output_path = os.path.join('outputs', f"{os.path.splitext(file.filename)[0]}.txt")
            os.makedirs('outputs', exist_ok=True)
            subprocess.run(['pdf2txt.py', '-o', output_path, input_path], check=True)

            return send_file(output_path, as_attachment=True)

    return '''
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload and Convert">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
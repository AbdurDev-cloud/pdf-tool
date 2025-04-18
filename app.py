from flask import Flask, request, send_file, render_template
import subprocess
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        if file:
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(input_path)

            operation = request.form.get('operation', 'text')  # Default to text conversion
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{os.path.splitext(file.filename)[0]}.{operation}")

            os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
            if operation == 'text':
                subprocess.run(['pdftotext.exe', '-layout', input_path, output_path], check=True)
            elif operation == 'image':  # Placeholder for PDF to image (using Ghostscript)
                subprocess.run(['gswin64c.exe', '-sDEVICE=png16m', '-r300', '-o', output_path, input_path], check=True)

            return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
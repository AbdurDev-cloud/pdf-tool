from flask import Flask, request, send_file, render_template
import subprocess
import os
import zipfile

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

            operation = request.form.get('operation', 'text')
            base_name = os.path.splitext(file.filename)[0]
            if operation == 'text':
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.txt")
                subprocess.run(['pdftotext.exe', '-layout', input_path, output_path], check=True)
                return send_file(output_path, as_attachment=True)
            elif operation == 'image':
                output_pattern = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}-%d.png")
                subprocess.run([
                    'gswin64c.exe',
                    '-sDEVICE=png16m',
                    '-r300',
                    '-sOutputFile=' + output_pattern,
                    '-dBATCH',  # Run in batch mode
                    '-dNOPAUSE',  # Prevent pausing between pages
                    input_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Create a zip file of all generated images
                zip_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_images.zip")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i in range(1, 10):  # Adjust range based on max pages if known
                        page_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}-{i}.png")
                        if os.path.exists(page_path):
                            zipf.write(page_path, os.path.basename(page_path))

                return send_file(zip_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
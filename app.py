from flask import Flask, request, send_file, render_template, make_response
import subprocess
import os
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return "No files uploaded", 400
        for file in files:
            if file.filename:
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(input_path)

        operation = request.form.get('operation', 'text')
        base_name = 'merged_output' if operation == 'merge' else os.path.splitext(files[0].filename)[0]
        if operation == 'text':
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.txt")
            subprocess.run(['pdftotext.exe', '-layout', input_path, output_path], check=True)
            return send_file(output_path, as_attachment=True, download_name=f"{base_name}.txt")
        elif operation == 'image':
            output_pattern = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}-%d.png")
            subprocess.run([
                'gswin64c.exe',
                '-sDEVICE=png16m',
                '-r300',
                '-sOutputFile=' + output_pattern,
                '-dBATCH',
                '-dNOPAUSE',
                input_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            zip_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_images.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i in range(1, 10):  # Adjust range if needed
                    page_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}-{i}.png")
                    if os.path.exists(page_path):
                        zipf.write(page_path, os.path.basename(page_path))
            return send_file(zip_path, as_attachment=True, download_name=f"{base_name}_images.zip")
        elif operation == 'merge':
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.pdf")
            input_files = [os.path.join(app.config['UPLOAD_FOLDER'], f.filename) for f in files if f.filename]
            subprocess.run(['gswin64c.exe', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite', '-sOutputFile=' + output_path] + input_files, check=True)
            return send_file(output_path, as_attachment=True, download_name=f"{base_name}.pdf")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
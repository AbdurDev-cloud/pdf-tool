from flask import Flask, request, send_file, render_template, make_response
import subprocess
import os
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Home route (default page)
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', operation=None)

# Individual operation routes
@app.route('/text', methods=['GET', 'POST'])
def text():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return "No files uploaded", 400
        for file in files:
            if file.filename:
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(input_path)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{os.path.splitext(files[0].filename)[0]}.txt")
        subprocess.run(['pdftotext.exe', '-layout', input_path, output_path], check=True)
        return send_file(output_path, as_attachment=True, download_name=f"{os.path.splitext(files[0].filename)[0]}.txt")
    return render_template('index.html', operation='text')

@app.route('/image', methods=['GET', 'POST'])
def image():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return "No files uploaded", 400
        for file in files:
            if file.filename:
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(input_path)
        base_name = os.path.splitext(files[0].filename)[0]
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
    return render_template('index.html', operation='image')

@app.route('/merge', methods=['GET', 'POST'])
def merge():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return "No files uploaded", 400
        for file in files:
            if file.filename:
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(input_path)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged_output.pdf')
        input_files = [os.path.join(app.config['UPLOAD_FOLDER'], f.filename) for f in files if f.filename]
        subprocess.run(['gswin64c.exe', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite', '-sOutputFile=' + output_path] + input_files, check=True)
        return send_file(output_path, as_attachment=True, download_name='merged_output.pdf')
    return render_template('index.html', operation='merge')

@app.route('/split', methods=['GET', 'POST'])
def split():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return "No files uploaded", 400
        for file in files:
            if file.filename:
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(input_path)
        base_name = os.path.splitext(files[0].filename)[0]
        output_pattern = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_page%d.pdf")
        subprocess.run([
            'gswin64c.exe',
            '-sDEVICE=pdfwrite',
            '-dBATCH',
            '-dNOPAUSE',
            '-sOutputFile=' + output_pattern,
            input_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_split.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i in range(1, 10):  # Adjust range if needed
                page_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_page{i}.pdf")
                if os.path.exists(page_path):
                    zipf.write(page_path, os.path.basename(page_path))
        return send_file(zip_path, as_attachment=True, download_name=f"{base_name}_split.zip")
    return render_template('index.html', operation='split')

@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return "No files uploaded", 400
        for file in files:
            if file.filename:
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(input_path)
        base_name = os.path.splitext(files[0].filename)[0]
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_compressed.pdf")
        subprocess.run([
            'gswin64c.exe',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/screen',
            '-dColorImageDownsampleType=/Bicubic',
            '-dColorImageResolution=72',
            '-dDownsampleColorImages=true',
            '-sOutputFile=' + output_path,
            input_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return send_file(output_path, as_attachment=True, download_name=f"{base_name}_compressed.pdf")
    return render_template('index.html', operation='compress')

if __name__ == '__main__':
    app.run(debug=True)
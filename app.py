from flask import Flask, render_template, request, send_from_directory
from io import BytesIO
from zipfile import ZipFile
import os
from PIL import Image
import PyPDF2

app = Flask(__name__)

@app.route('/')
def index():
    operation = request.args.get('operation')
    return render_template('index.html', operation=operation)

@app.route('/text')
def text():
    return render_template('index.html', operation='text')

@app.route('/image')
def image():
    return render_template('index.html', operation='image')

@app.route('/merge')
def merge():
    return render_template('index.html', operation='merge')

@app.route('/split')
def split():
    return render_template('index.html', operation='split')

@app.route('/compress')
def compress():
    return render_template('index.html', operation='compress')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/', methods=['POST'])
def process():
    if 'file' not in request.files:
        return "No file part", 400
    files = request.files.getlist('file')
    operation = request.form['operation']

    if not files or files[0].filename == '':
        return "No selected file", 400

    output = None
    if operation == 'text':
        pdf_reader = PyPDF2.PdfReader(files[0])
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        output = text.encode()
    elif operation == 'image':
        pdf_reader = PyPDF2.PdfReader(files[0])
        images = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].get_object()
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                        data = xObject[obj].get_data()
                        if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                            mode = "RGB"
                        else:
                            mode = "P"
                        img = Image.frombytes(mode, size, data)
                        images.append(img)
        buffer = BytesIO()
        with ZipFile(buffer, 'w') as zipf:
            for i, img in enumerate(images):
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')
                zipf.writestr(f'image_{i}.png', img_byte_arr.getvalue())
        output = buffer.getvalue()
    elif operation == 'merge':
        pdf_writer = PyPDF2.PdfWriter()
        for file in files:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        buffer = BytesIO()
        pdf_writer.write(buffer)
        output = buffer.getvalue()
    elif operation == 'split':
        pdf_reader = PyPDF2.PdfReader(files[0])
        buffer = BytesIO()
        with ZipFile(buffer, 'w') as zipf:
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer = PyPDF2.PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_num])
                pdf_output = BytesIO()
                pdf_writer.write(pdf_output)
                zipf.writestr(f'page_{page_num + 1}.pdf', pdf_output.getvalue())
        output = buffer.getvalue()
    elif operation == 'compress':
        pdf_reader = PyPDF2.PdfReader(files[0])
        pdf_writer = PyPDF2.PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        buffer = BytesIO()
        pdf_writer.write(buffer)
        output = buffer.getvalue()  # Note: PyPDF2 doesn't optimize compression; consider PyMuPDF for better results

    if output:
        return output, 200, {'Content-Type': 'application/octet-stream', 'Content-Disposition': f'attachment; filename=output.{operation == "text" and "txt" or "zip"}'}
    return "Operation not supported", 400

if __name__ == '__main__':
    app.run(debug=True)
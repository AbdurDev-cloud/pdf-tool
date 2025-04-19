from flask import Flask, render_template, request, send_from_directory
import os

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
    # Add your file processing logic here (e.g., convert to text, images, etc.)
    # For now, return a dummy response
    return "Processing complete", 200

if __name__ == '__main__':
    app.run(debug=True)
from Modules.GCLogParser import *
from flask import Flask, jsonify, request
from flask_cors import CORS
from os.path import join, dirname

PATH = dirname(__file__)
SAVE_FLDR = 'SavedFiles'

app = Flask(__name__)
cors = CORS(app) # allow only requests from http://localhost:3000
app.config["CORS_ORIGINS"] = ["http://localhost:5000"]

# Define a simple endpoint to test the API
@app.route('/')
def hello_world():
    return 'Flask API is up and running!'

# Define an endpoint to upload a .log file
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file is None or file.filename is None:
        return jsonify({'error': 'No file uploaded'}), 400

    # Make sure the file is a .log file
    if file.filename.split('.')[-1] != 'log':
        return jsonify({'error': 'Invalid file type, please upload a .log file'}), 400
    
    # Save the file to the server
    filepath = join(PATH, SAVE_FLDR, file.filename)
    file.save(filepath)
    parser = GCLogParser(filepath)
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'data': parser.totalTimeConcurrentCycle()}), 200

if __name__ == '__main__':
    app.run(debug=True)

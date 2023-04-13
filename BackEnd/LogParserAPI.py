from Modules.GCLogParser import *
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from os import mkdir
from os.path import join, dirname, exists

PATH = dirname(__file__)
SAVE_FLDR = 'SavedFiles'

app = Flask(__name__)
cors = CORS(app) # allow only requests from http://localhost:3000

# Define a simple endpoint to test the API
@app.route('/')
def hello_world():
    app.logger.debug('Hello World!')
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
    parser.stackBarChart(show=False, file_path=filepath.split('.log')[0])
    parser.timeline(show=False, file_path=filepath.split('.log')[0])
    payload = {
        'filename': file.filename,
        'totalTime': parser.totalTime(),
        'totalTimeConcurrentCycle': parser.totalTimeConcurrentCycle(),
        'totalTimePauseYoung': parser.totalTimePauseYoung(),
        'avgTime': parser.avgTime(),
        'minPauseTime': parser.minPauseTime(),
        'maxPauseTime': parser.maxPauseTime(),
        'stackBarChart': 'http://localhost:5000/static/' + file.filename.split('.log')[0] + '-stackBarChart.png',
        'timeline': 'http://localhost:5000/static/' + file.filename.split('.log')[0] + '-timeline.png'
    }
    return jsonify(payload), 200

@app.route('/static/<filename>')
def send_static(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.config["CORS_ORIGINS"] = ["http://localhost:5000"]
    app.config['UPLOAD_FOLDER'] = join(PATH, SAVE_FLDR)
    if not exists(app.config['UPLOAD_FOLDER']):
        mkdir(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

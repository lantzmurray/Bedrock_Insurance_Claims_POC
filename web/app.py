from flask import Flask, request, jsonify, send_file
import json
import boto3
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

# Import our existing modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.config import CLAIM_BUCKET, CLAIMS_PREFIX, OUTPUTS_PREFIX
from src.app import process_claim_document
from src.models import BedrockModelInvoker

app = Flask(__name__)
s3_client = boto3.client('s3')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Upload to S3
        s3_filename = f"{CLAIMS_PREFIX}{filename}"
        try:
            s3_client.upload_file(
                filepath,
                CLAIM_BUCKET,
                s3_filename,
                ExtraArgs={'ContentType': 'text/plain'}
            )
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                's3_key': s3_filename,
                'bucket': CLAIM_BUCKET
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_document():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Filename required'}), 400
    
    filename = data['filename']
    s3_key = f"{CLAIMS_PREFIX}{filename}"
    
    try:
        # Process the claim document using our existing logic
        result = process_claim_document(s3_key)
        
        # Add timestamp to result
        result['processed_at'] = datetime.now().isoformat()
        result['filename'] = filename
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/outputs', methods=['GET'])
def get_outputs():
    try:
        # List all objects in the outputs folder
        response = s3_client.list_objects_v2(
            Bucket=CLAIM_BUCKET,
            Prefix=OUTPUTS_PREFIX
        )
        
        outputs = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # Get the object to retrieve metadata
                obj_response = s3_client.head_object(
                    Bucket=CLAIM_BUCKET,
                    Key=obj['Key']
                )
                
                outputs.append({
                    'key': obj['Key'],
                    'filename': obj['Key'].replace(OUTPUTS_PREFIX, ''),
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj.get('ETag', '')
                })
        
        return jsonify(outputs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:key>')
def download_output(key):
    try:
        # Generate presigned URL for download
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': CLAIM_BUCKET, 'Key': key},
            ExpiresIn=3600  # 1 hour expiry
        )
        return jsonify({'download_url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/outputs/<path:key>')
def view_output(key):
    try:
        # Get the object from S3
        response = s3_client.get_object(
            Bucket=CLAIM_BUCKET,
            Key=key
        )
        
        # Return the file content
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
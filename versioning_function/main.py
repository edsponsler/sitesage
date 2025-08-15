
import os
from flask import Flask, jsonify
from google.cloud import storage

app = Flask(__name__)

# Get GCS bucket from environment variable
BUCKET_NAME = os.environ.get('GCS_BUCKET')
if not BUCKET_NAME:
    raise ValueError("GCS_BUCKET environment variable not set.")

@app.route('/version', methods=['GET'])
def get_version():
    """Returns the latest version of the index file."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.get_blob("campgrounds.index")

    if not blob:
        return jsonify({"error": "Index file not found."}), 404

    return jsonify({"version": blob.generation})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

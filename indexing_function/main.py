
import os
import faiss
from google.cloud import firestore
from google.cloud import storage
from sentence_transformers import SentenceTransformer

# Initialize Firestore client
db = firestore.Client()

# Initialize Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_campgrounds():
    """Fetches all campground data from the 'campgrounds' collection in Firestore."""
    campgrounds_ref = db.collection('campgrounds')
    docs = campgrounds_ref.stream()
    campgrounds = [doc.to_dict() for doc in docs]
    return campgrounds

def generate_embeddings(campgrounds):
    """Generates vector embeddings for a list of campgrounds."""
    # Create a single string for each campground for embedding
    campground_texts = [
        f"{c.get('name', '')}: {c.get('description', '')}" for c in campgrounds
    ]
    embeddings = model.encode(campground_texts)
    return embeddings

def create_faiss_index(embeddings):
    """Creates a FAISS index from a list of embeddings."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Get GCS bucket from environment variable
BUCKET_NAME = os.environ.get('GCS_BUCKET')
if not BUCKET_NAME:
    raise ValueError("GCS_BUCKET environment variable not set.")

def upload_to_gcs(local_file_path, destination_blob_name):
    """Uploads a file to the GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    print(f"File {local_file_path} uploaded to {destination_blob_name}.")

if __name__ == '__main__':
    campgrounds = get_campgrounds()
    print(f"Successfully fetched {len(campgrounds)} campgrounds.")
    embeddings = generate_embeddings(campgrounds)
    print(f"Successfully generated {len(embeddings)} embeddings.")
    index = create_faiss_index(embeddings)
    print(f"Successfully created FAISS index with {index.ntotal} vectors.")
    local_index_file = "campgrounds.index"
    faiss.write_index(index, local_index_file)
    print(f"Successfully wrote FAISS index to {local_index_file}")
    upload_to_gcs(local_index_file, local_index_file)

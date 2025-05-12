from flask import Flask, jsonify, request
import pymongo
import boto3
import logging
import sys
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os
import base64
import mimetypes

# Configure logging
def setup_logger():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logger = logging.getLogger("atlas_federation")
    logger.setLevel(numeric_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
database_name = os.getenv("MONGODB_DATABASE")
collection_name = os.getenv("MONGODB_COLLECTION")
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")

# Initialize logger
logger = setup_logger()

# Initialize Flask app
app = Flask(__name__)

# Configure Flask logging
app.logger.handlers = []
for handler in logger.handlers:
    app.logger.addHandler(handler)

# MongoDB connection
mongo_client = pymongo.MongoClient(mongo_uri)
db = mongo_client[database_name]
collection = db[collection_name]

# S3 connection
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

def get_mime_type(file_name):
    """Determine mime type based on file extension"""
    return mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

def download_from_s3(bucket, key):
    """Download a file from S3 and return its content"""
    logger.debug(f"Downloading file from S3: {bucket}/{key}")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()
        content_type = response.get('ContentType', get_mime_type(key))
        
        # Convert binary data to base64 for embedding in JSON
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        logger.debug(f"Successfully downloaded file: {bucket}/{key} ({len(file_content)} bytes)")
        
        return {
            'content': encoded_content,
            'content_type': content_type,
            'size': len(file_content),
            'last_modified': response.get('LastModified', '').isoformat() if response.get('LastModified') else None
        }
    except Exception as e:
        logger.error(f"Error downloading from S3: {bucket}/{key} - {str(e)}")
        return None

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document_with_file(document_id):
    """Retrieve a document from MongoDB and its associated S3 file"""
    logger.info(f"Retrieving document with ID: {document_id}")
    try:
        # Convert string ID to ObjectId
        from bson.objectid import ObjectId
        object_id = ObjectId(document_id)
        
        # Find document in MongoDB
        document = collection.find_one({"_id": object_id})
        
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return jsonify({"error": "Document not found"}), 404
        
        # Check if the document has a file reference
        if "file_reference" in document:
            # Extract S3 file details
            bucket = document["file_reference"]["bucket"]
            key = document["file_reference"]["key"]
            
            # Get file content from S3
            file_data = download_from_s3(bucket, key)
            
            if file_data:
                # Convert MongoDB document to dict and add file data
                doc_dict = {k: str(v) if isinstance(v, ObjectId) else v for k, v in document.items()}
                doc_dict["file_data"] = file_data
                
                logger.info(f"Successfully retrieved document and file: {document_id}")
                return jsonify(doc_dict)
            else:
                # Still return document if file can't be retrieved
                doc_dict = {k: str(v) if isinstance(v, ObjectId) else v for k, v in document.items()}
                doc_dict["file_error"] = "Could not retrieve associated file"
                logger.warning(f"Retrieved document but could not get associated file: {document_id}")
                return jsonify(doc_dict)
        else:
            # Document doesn't have a file, just return the document
            doc_dict = {k: str(v) if isinstance(v, ObjectId) else v for k, v in document.items()}
            logger.info(f"Retrieved document without file reference: {document_id}")
            return jsonify(doc_dict)
    
    except Exception as e:
        logger.error(f"Error retrieving document: {document_id} - {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_all_documents():
    """Retrieve all documents from MongoDB (without S3 files)"""
    logger.info("Retrieving all documents")
    try:
        documents = list(collection.find())
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        logger.info(f"Successfully retrieved {len(documents)} documents")
        return jsonify(documents)
    
    except Exception as e:
        logger.error(f"Error retrieving all documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/file', methods=['GET'])
def get_document_file_only(document_id):
    """Retrieve only the file associated with a document"""
    logger.info(f"Retrieving file for document: {document_id}")
    try:
        # Convert string ID to ObjectId
        from bson.objectid import ObjectId
        object_id = ObjectId(document_id)
        
        # Find document in MongoDB
        document = collection.find_one({"_id": object_id})
        
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return jsonify({"error": "Document not found"}), 404
        
        # Check if the document has a file reference
        if "file_reference" in document:
            # Extract S3 file details
            bucket = document["file_reference"]["bucket"]
            key = document["file_reference"]["key"]
            
            # Get file content from S3
            file_data = download_from_s3(bucket, key)
            
            if file_data:
                logger.info(f"Successfully retrieved file for document: {document_id}")
                return jsonify(file_data)
            else:
                logger.error(f"Could not retrieve file for document: {document_id}")
                return jsonify({"error": "Could not retrieve file"}), 500
        else:
            logger.warning(f"Document has no associated file: {document_id}")
            return jsonify({"error": "Document does not have an associated file"}), 404
    
    except Exception as e:
        logger.error(f"Error retrieving file for document: {document_id} - {str(e)}")
        return jsonify({"error": str(e)}), 500

# Helper route for testing/debugging
@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Performing health check")
    try:
        # Test MongoDB connection
        mongo_client.admin.command('ping')
        mongo_status = "Connected"
        logger.debug("MongoDB connection successful")
    except Exception as e:
        mongo_status = "Failed"
        logger.error(f"MongoDB connection failed: {str(e)}")
    
    try:
        # Test S3 connection (list buckets)
        s3_client.list_buckets()
        s3_status = "Connected"
        logger.debug("S3 connection successful")
    except Exception as e:
        s3_status = "Failed"
        logger.error(f"S3 connection failed: {str(e)}")
    
    return jsonify({
        "status": "healthy",
        "mongodb": mongo_status,
        "s3": s3_status
    })

if __name__ == '__main__':
    logger.info("Starting Atlas Application Federation API server")
    app.run(debug=True)
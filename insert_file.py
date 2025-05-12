import pymongo
import boto3
import uuid
import logging
import sys
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

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
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Load env variables
load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
database_name = os.getenv("MONGODB_DATABASE")
collection_name = os.getenv("MONGODB_COLLECTION")
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
aws_bucket_name = os.getenv("AWS_BUCKET_NAME")

# Initialize logger
logger = setup_logger()

# MongoDB connection - https://www.mongodb.com/docs/atlas/driver-connection/
mongo_client = pymongo.MongoClient(mongo_uri)
db = mongo_client[database_name]
collection = db[collection_name]

try:
    mongo_client.admin.command('ping')
    logger.info("Successfully connected to MongoDB Atlas")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# S3 connection
s3_client = boto3.client(
    's3',
    aws_access_key_id = aws_access_key,
    aws_secret_access_key = aws_secret_key
)

def upload_file_to_s3(file_path, bucket_name, object_name=None):
    """Upload a file to an S3 bucket and return its reference"""
    if object_name is None:
        object_name = str(uuid.uuid4()) + '_' + file_path.split('/')[-1]
    
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        # Make the file publicly accessible (optional)
        s3_client.put_object_acl(
            ACL='public-read',
            Bucket=bucket_name,
            Key=object_name
        )
        
        # Get the URL
        location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        region = 'us-east-1' if location is None else location
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_name}"
        
        return {
            "bucket": bucket_name,
            "key": object_name,
            "url": url
        }
    except NoCredentialsError:
        logger.error("AWS credentials not available")
        return None
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        return None

def store_document_with_s3_reference(document_data, file_path, bucket_name):
    """Store a document in MongoDB with a reference to an S3 file"""
    logger.info(f"Storing document with reference to file: {file_path}")
    
    # Upload file to S3
    s3_reference = upload_file_to_s3(file_path, bucket_name)
    
    if s3_reference:
        # Add the S3 reference to the document
        document_data["file_reference"] = s3_reference
        logger.debug(f"S3 reference created: {s3_reference}")
        
        # Insert into MongoDB
        try:
            result = collection.insert_one(document_data)
            logger.info(f"Document stored in MongoDB with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to store document in MongoDB: {e}")
            return None
    else:
        logger.error(f"Failed to upload file to S3: {file_path}")
        return None

if __name__ == "__main__":
    logger.info("Starting Atlas Application Federation file insertion")
    
    # Example document data
    document_data = {
        "title": "Cat Picture",
        "description": "A sample cat image",
        "created_at": datetime.now()
    }
    
    # Store document with S3 reference
    result_id = store_document_with_s3_reference(document_data, "sample-pictures/cat.jpg", aws_bucket_name)
    
    if result_id:
        logger.info(f"Successfully processed file with document ID: {result_id}")
    else:
        logger.error("Failed to process file")
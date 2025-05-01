import pymongo
import boto3
import uuid
from botocore.exceptions import NoCredentialsError

# MongoDB connection - https://www.mongodb.com/docs/atlas/driver-connection/
mongo_client = pymongo.MongoClient("mongodb://username:password@hostname:port/")
db = mongo_client["your_database"]
collection = db["your_collection"]

# S3 connection
s3_client = boto3.client(
    's3',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
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
        print("Credentials not available")
        return None

def store_document_with_s3_reference(document_data, file_path, bucket_name):
    """Store a document in MongoDB with a reference to an S3 file"""
    # Upload file to S3
    s3_reference = upload_file_to_s3(file_path, bucket_name)
    
    if s3_reference:
        # Add the S3 reference to the document
        document_data["file_reference"] = s3_reference
        
        # Insert into MongoDB
        result = collection.insert_one(document_data)
        return result.inserted_id
    
    return None

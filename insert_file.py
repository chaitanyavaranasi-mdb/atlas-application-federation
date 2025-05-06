import pymongo
import boto3
import uuid
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

#load env and mark variables
load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
database_name = os.getenv("MONGODB_DATABASE")
collection_name = os.getenv("MONGODB_COLLECTION")
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
aws_bucket_name = os.getenv("AWS_BUCKET_NAME")

# MongoDB connection - https://www.mongodb.com/docs/atlas/driver-connection/
mongo_client = pymongo.MongoClient(mongo_uri)
db = mongo_client[database_name]
collection = db[collection_name]

try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

print(aws_secret_key)
print(aws_access_key)
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

store_document_with_s3_reference({}, "sample-pictures/cat.jpg", aws_bucket_name)
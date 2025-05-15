# Atlas Application Federation

A robust solution for integrating MongoDB with external storage services (AWS S3) to overcome document size limitations and optimize storage costs.

## 📋 Overview

This project demonstrates a powerful pattern for handling large files in MongoDB applications by:

1. Storing large binary files in AWS S3
2. Maintaining references to these files in MongoDB documents
3. Implementing application federation to provide a unified data access layer

## 🔑 Key Benefits

- **Overcome MongoDB's 16MB document size limit** for large binary objects
- **Reduce storage costs** by leveraging S3's cost-effective storage tiers
- **Improve database performance** by keeping MongoDB collections lean
- **Scale independently** for document data and binary assets
- **Simplify client applications** through a unified API that abstracts storage details

## 🏗️ Architecture

The solution consists of two main components:

1. **S3 Storage Integration** (`insert_file.py`): Uploads files to S3 and stores references in MongoDB
2. **Application Federation API** (`federate_file.py`): A Flask API that unifies access to both MongoDB data and S3 files

### How it Works

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │         │             │         │             │
│   Client    │ ───────►│  Flask API  │ ───────►│  MongoDB    │
│  Application│         │(Federation) │         │             │
│             │         │             │         └──────┬──────┘
└─────────────┘         └─────────────┘                │
                               │                        │
                               │                        │
                               ▼                        │
                        ┌─────────────┐                 │
                        │             │                 │
                        │   AWS S3    │◄────────────────┘
                        │             │    Reference
                        └─────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- MongoDB Atlas account (or local MongoDB instance)
- AWS account with S3 access

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/atlas-application-federation.git
cd atlas-application-federation
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root
```
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION=your_collection_name
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_BUCKET_NAME=your_s3_bucket_name
LOG_LEVEL=INFO
```

## 🔧 Usage

### 1. Uploading Files to S3 and Storing References in MongoDB

Run the `insert_file.py` script to upload a file to S3 and store its reference in MongoDB:

```bash
python insert_file.py
```

This script:
- Uploads the file to S3
- Generates a unique ID for the file
- Makes the file publicly accessible (optional)
- Creates a MongoDB document with a reference to the S3 file

Example document structure:
```json
{
  "_id": ObjectId("60a2c3e4c5fd4b001a123456"),
  "title": "Cat Picture",
  "description": "A sample cat image",
  "created_at": ISODate("2025-05-01T10:30:45.123Z"),
  "file_reference": {
    "bucket": "my-company-docs",
    "key": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_cat.jpg",
    "url": "https://my-company-docs.s3.us-east-1.amazonaws.com/8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_cat.jpg"
  }
}
```

### 2. Running the Federation API

Start the Flask API to provide unified access to MongoDB documents and S3 files:

```bash
python federate_file.py
```

The API will be available at `http://localhost:5000`

## 🌐 API Endpoints

### Get a Document with its File
```
GET /api/documents/{document_id}
```
Returns a document from MongoDB with its S3 file embedded as base64.

Example response:
```json
{
  "_id": "60a2c3e4c5fd4b001a123456",
  "title": "Cat Picture",
  "description": "A sample cat image",
  "created_at": "2025-05-01T10:30:45.123Z",
  "file_reference": {
    "bucket": "my-company-docs",
    "key": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_cat.jpg",
    "url": "https://my-company-docs.s3.us-east-1.amazonaws.com/8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_cat.jpg"
  },
  "file_data": {
    "content": "base64_encoded_content_here",
    "content_type": "image/jpeg",
    "size": 1048576,
    "last_modified": "2025-05-01T10:35:22.123Z"
  }
}
```

### Get All Documents
```
GET /api/documents
```
Returns all documents from MongoDB (without S3 files).

### Get Document File Only
```
GET /api/documents/{document_id}/file
```
Returns only the file associated with a document.

Example response:
```json
{
  "content": "base64_encoded_content_here",
  "content_type": "image/jpeg",
  "size": 1048576,
  "last_modified": "2025-05-01T10:35:22.123Z"
}
```

### Health Check
```
GET /health
```
Returns the health status of MongoDB and S3 connections.

Example response:
```json
{
  "status": "healthy",
  "mongodb": "Connected",
  "s3": "Connected"
}
```

## 📝 Implementation Details

### S3 Integration (`insert_file.py`)

The `insert_file.py` script handles:
- Connecting to MongoDB and S3
- Uploading files to S3 with unique names
- Setting appropriate S3 permissions
- Creating MongoDB documents with S3 references
- Comprehensive logging

### Federation API (`federate_file.py`)

The `federate_file.py` implements:
- RESTful API endpoints with Flask
- Document retrieval from MongoDB
- File downloading from S3
- Base64 encoding for JSON embedding
- Error handling and status codes
- Comprehensive logging

## 🔍 Logging

Both components use a consistent logging approach:

- Configurable log level via the `LOG_LEVEL` environment variable
- Structured log format with timestamps and log levels
- Context-specific log messages for all operations
- Proper error handling with detailed error logging

Example log output:
```
[2025-05-09 10:15:22] [atlas_federation] [INFO] Starting Atlas Application Federation API server
[2025-05-09 10:15:30] [atlas_federation] [INFO] Retrieving document with ID: 60a2c3e4c5fd4b001a123456
[2025-05-09 10:15:30] [atlas_federation] [DEBUG] Downloading file from S3: my-company-docs/8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_cat.jpg
[2025-05-09 10:15:31] [atlas_federation] [INFO] Successfully retrieved document and file: 60a2c3e4c5fd4b001a123456
```

## 🔧 Configuration

Configuration is managed through environment variables (via `.env` file):

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:password@cluster.mongodb.net/` |
| `MONGODB_DATABASE` | MongoDB database name | `myapp` |
| `MONGODB_COLLECTION` | MongoDB collection name | `documents` |
| `AWS_ACCESS_KEY` | AWS access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_KEY` | AWS secret access key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_BUCKET_NAME` | S3 bucket name | `my-company-docs` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🧩 Extension Ideas

- **Add authentication** to the API endpoints
- **Implement caching** for frequently accessed files
- **Support additional storage backends** beyond S3 (GCS, Azure Blob Storage)
- **Add file processing capabilities** (thumbnails, transcoding, etc.)
- **Implement file versioning** for document management use cases
- **Incorporate Resume Tokens** for managing long running archival jobs
  
## 🔒 Security Considerations

- **Authentication**: Implement a proper authentication mechanism for API access
- **S3 Security**: Use private S3 buckets and signed URLs for sensitive content
- **Data Validation**: Validate all inputs, particularly document IDs and file paths
- **Rate Limiting**: Implement rate limiting to prevent abuse

## ⛙ MongoDB Atlas Data Federation

Atlas Data Federation is a powerful query engine provided by MongoDB that allows users to query, transform, and move data seamlessly across different sources, such as Atlas clusters, cloud storage services (e.g., AWS S3, Azure Blob Storage, Google Cloud Storage), and HTTP endpoints, without requiring complex integrations or data movement. It creates "federated database instances" that map virtual collections to underlying data sources, enabling developers to access data as if it were stored in the same place and format. This solution is ideal for use cases like data engineering, archival, operational analytics, and reshaping data, offering features like provenance metadata, flexible read preferences, and aggregation pipelines to enrich datasets. 

To get started with Atlas Data Federation, create a federated database instance through the Atlas UI or API, link data stores such as your Atlas cluster or cloud storage buckets, and use the MongoDB Query Language or Atlas SQL to query and transform your data. For step-by-step guidance, visit the MongoDB documentation and explore tutorials to leverage its full capabilities.

## 📚 Additional Resources

- [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/index.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Atlas Data Federation - Learning Byte - Learn](https://learn.mongodb.com/learn/course/atlas-data-federation/learning-byte/learn)
- [Atlas Data Federation Overview](https://mongodb.com/docs/atlas/data-federation/overview/)
- [Querying the MongoDB Atlas Price Book with Atlas Data Federation](https://www.mongodb.com/developer/products/atlas/querying-price-book-data-federation)

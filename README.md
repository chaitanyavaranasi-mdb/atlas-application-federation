# Atlas Application Federation
Implement federation application-side with MongoDB Atlas and S3

Hey there, fellow devs! 

Today, I'm diving into a powerful MongoDB pattern that's been a game-changer for my data-heavy applications. I'll show you how to reference external storage (specifically AWS S3) from MongoDB documents and implement application federation to retrieve both MongoDB and S3 data in a unified payload.
Why Separate Blob Storage from MongoDB?
Before we jump into code, let's understand why this matters. While MongoDB is fantastic for document storage, it has some limitations when dealing with large binary objects:
MongoDB has a document size limit of 16MB, which can be restrictive for storing large files like PDFs, videos, or high-res images.

The primary advantages of using external storage like S3 include:
Cost efficiency - S3 storage is significantly cheaper per GB than MongoDB storage
Scalability - S3 can handle virtually unlimited storage needs
Performance - Offloading large binary data prevents MongoDB from becoming bloated
CDN integration - S3 works seamlessly with content delivery networks for faster global access

Approach 1: Simple S3 References in MongoDB
The most straightforward approach is to store references to S3 objects in your MongoDB documents. This is ideal when you need basic blob storage with minimal integration. For additional data governance, I recommend hashing to ensure object immutability.
Here's how we implement it in Python in **`insert_file.py`**

The sample document would look something like this. Take note and look at the file array structure of references. 
```
{
  "_id": ObjectId("60a2c3e4c5fd4b001a123456"),
  "title": "Important Report",
  "author": "Jane Doe",
  "created_at": ISODate("2025-05-01T10:30:45.123Z"),
  "file_reference": {
    "bucket": "my-company-docs",
    "key": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_report.pdf",
    "url": "https://my-company-docs.s3.us-east-1.amazonaws.com/8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d_report.pdf"
  }
}
``` 

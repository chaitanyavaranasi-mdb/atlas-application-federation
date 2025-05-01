# Atlas Application Federation

Hey there, fellow devs! 

Today, I'm diving into a powerful MongoDB pattern that's been a game-changer for my data-heavy applications. I'll show you how to reference external storage (specifically AWS S3) from MongoDB documents and implement application federation to retrieve both MongoDB and S3 data in a unified payload.
Why Separate Blob Storage from MongoDB?
Before we jump into code, let's understand why this matters. While MongoDB is fantastic for document storage, it has some limitations when dealing with large binary objects:
MongoDB has a document size limit of 16MB, which can be restrictive for storing large files like PDFs, videos, or high-res images.

The primary advantages of using external storage like S3 include:  

1. Cost efficiency - S3 storage is significantly cheaper per GB  
2. Scalability - S3 can handle virtually unlimited storage needs  
3. Performance - Offloading large binary data prevents MongoDB from becoming bloated  
4. CDN integration - S3 works seamlessly with content delivery networks for faster global access  

## Use Case 1:  Simple S3 References in MongoDB
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
---
## Use Case 2:  Application Federation for Unified Data Access
What if we need to retrieve both MongoDB data and associated S3 objects in a single operation? This is where application federation comes in, allowing us to abstract away the storage details from the client.
Here's how we implement it in Python's FLASK API . Code in **`federate_file.py`**

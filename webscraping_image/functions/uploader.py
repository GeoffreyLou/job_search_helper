import boto3

def aws_bucket_upload(filename, 
                      bucket_name,
                      s3_file,
                      aws_access_key_id, 
                      aws_secret_access_key, 
                      region):
    """
    Load Pandas DataFrame to a AWS S3 Bucket.

    Parameters : 
    - dataframe: Pandas DataFrame to upload.
    - bucket_name: Name of the AWS S3 Bucket.
    - s3_file: Name of the file after upload on S3 Bucket.
    - aws_access_key_id: AWS access key.
    - aws_secret_access_key: AWS secret access key.
    - region: The region where the S3 bucket is.
    """
    
    try: 
        
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
            )
        
        s3.upload_file(
            filename,
            bucket_name,
            s3_file
            )
        
    except Exception as e:
        print(f"Failed to upload file on S3 : {e}")
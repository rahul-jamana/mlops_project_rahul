import boto3


def get_s3_client():
    return boto3.client("s3")


def upload_file(local_path, bucket, s3_key):
    s3 = get_s3_client()
    s3.upload_file(local_path, bucket, s3_key)
    print(f"Uploaded {local_path} to s3://{bucket}/{s3_key}")


def download_file(bucket, s3_key, local_path):
    s3 = get_s3_client()
    s3.download_file(bucket, s3_key, local_path)
    print(f"Downloaded {s3_key} to {local_path}")

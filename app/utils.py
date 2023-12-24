import os
import shutil
import boto3
TMP_DIR = "./temp"
os.makedirs(TMP_DIR, exist_ok=True)


def save_file(file):
    file_path = f"{TMP_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX")

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def upload_to_s3(file):
    key = os.path.join(S3_PREFIX, file.filename)
    s3.upload_fileobj(file.file, BUCKET_NAME, key)
    return BUCKET_NAME, key

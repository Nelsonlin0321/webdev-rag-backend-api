import os
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import boto3
import botocore
import dotenv
import uvicorn
from datetime import datetime

dotenv.load_dotenv()

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX")


s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

PREFIX = "/api"

@app.post("{PREFIX}/upload") 
async def upload_file(file: UploadFile = File(...)): 
    try:
        key = os.path.join(S3_PREFIX,file.filename)
        s3.upload_fileobj(file.file, BUCKET_NAME, key)
        return {"message": "File uploaded successfully","bucket":BUCKET_NAME,"key":key} 
    except botocore.exceptions.ClientError as e:
        return {"message": "File upload failed", "error": str(e)}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
start_time = datetime.utcnow()
start_time = start_time.strftime(DATE_FORMAT)

@app.get(f"{PREFIX}/health-check")
async def health_check():
    response = f"The server is up since {start_time}"
    return {"message": response, "start_uct_time": start_time}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
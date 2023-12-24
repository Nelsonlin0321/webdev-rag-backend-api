import os
from fastapi import FastAPI, File, UploadFile
import boto3
import botocore
import dotenv
import uvicorn
dotenv.load_dotenv()

app = FastAPI()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX")


s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

@app.post("/api/upload") 
async def upload_file(file: UploadFile = File(...)): 
    try:
        key = os.path.join(S3_PREFIX,file.filename)
        s3.upload_fileobj(file.file, BUCKET_NAME, key)
        return {"message": "File uploaded successfully","bucket":BUCKET_NAME,"key":key} 
    except botocore.exceptions.ClientError as e:
        return {"message": "File upload failed", "error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
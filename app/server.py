"""Server with endpoints"""
import os
from datetime import datetime
import botocore
import dotenv
import utils
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from processor import PDFToSentenceEmbedding
from mongodb_engine import MongoDB

dotenv.load_dotenv()

embedding_generator = PDFToSentenceEmbedding()
mongo_db_engine = MongoDB()

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


PREFIX = "/api"


@app.post(f"{PREFIX}/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """_summary_

    Args:
        file (UploadFile, optional): _description_. Defaults to File(...).

    Returns:
        _type_: _description_
    """
    try:
        if not mongo_db_engine.file_exist(file_name=file.filename):
            save_file_path = utils.save_file(file=file)
            doc_meta_list = embedding_generator(save_file_path)
            mongo_db_engine.insert_embedding(doc_meta_list)
            mongo_db_engine.insert_document(file_name=file.filename)
            os.remove(save_file_path)

            return {"message":
                    f"The file: {file.filename} has been successfully ingested and processed!"}

    except botocore.exceptions.ClientError as e:
        return {"message": "File upload failed", "error": str(e)}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
start_time = datetime.utcnow()
start_time = start_time.strftime(DATE_FORMAT)


@app.get(f"{PREFIX}/health-check")
async def health_check():
    """_summary_

    Returns:
        _type_: _description_
    """
    response = f"The server is up since {start_time}"
    return {"message": response, "start_uct_time": start_time}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

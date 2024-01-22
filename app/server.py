import os
from datetime import datetime
from uuid import uuid4
from openai import OpenAI
import dotenv
import uvicorn
import boto3
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# pylint:disable=relative-beyond-top-level
from .processor import PDFToSentenceEmbedding
from .mongodb_engine import MongoDB
from .payload import PayLoad
# pylint:disable=no-name-in-module
from . import utils

dotenv.load_dotenv()

embedding_generator = PDFToSentenceEmbedding()
mongo_db_engine = MongoDB()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # for OpenAI API calls

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

s3 = boto3.client('s3')


def upload_file_to_s3(file_path, object_name):
    """
    Uploads a file to an S3 bucket.

    Args:
        file_path (str): The local file path of the file to upload.
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The desired object name/key in the S3 bucket.
    """
    try:
        s3.upload_file(file_path, "cloudfront-aws-bucket",
                       os.path.join("rag-documents", object_name))
    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(
            f"Error uploading file '{file_path}' to S3 bucket {str(e)}")


@app.post(f"{PREFIX}/ingest")
async def ingest_file(file: UploadFile = File(...)):
    try:
        if not mongo_db_engine.file_exist(file_name=file.filename):
            save_file_path = utils.save_file(file=file)
            upload_file_to_s3(save_file_path, file.filename)
            doc_meta_list = embedding_generator(save_file_path)
            mongo_db_engine.insert_embedding(doc_meta_list)
            mongo_db_engine.insert_document(file_name=file.filename)
            os.remove(save_file_path)

            return {"message":
                    f"The file: {file.filename} has been successfully ingested and processed!"}

        return {"message":
                f"The file: {file.filename} has been ingested and processed before!"}

    # pylint: disable=broad-exception-caught
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def retrieve(question: str, file_name: str):
    query_vector = embedding_generator.model.encode(question).tolist()
    results = mongo_db_engine.vector_search(
        query_vector=query_vector, file_name=file_name)
    return results


@app.post(f"{PREFIX}/retrieval_generate")
async def retrieval_generate(pay_load: PayLoad):
    # try:
    if pay_load.context:
        context = pay_load.context
    else:
        context = pay_load.question

    query_vector = embedding_generator.model.encode(
        context).tolist()

    retrieved_results = mongo_db_engine.hybrid_search(
        query_vector=query_vector, query=context,
        file_name=pay_load.file_name, limit=5)

    prompt = utils.generate_prompt(retrieved_results)

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo-16k',
        messages=[
            {'role': 'system',
                'content': prompt,
             },
            {"role": "user",
                "content": pay_load.question},
            {"role": "user",
                "content":
                "The answer should follow below template: Answer: {Answer} Page Number->{page_number}."}
        ],
        temperature=0,
        stream=False
    )
    answer = completion.choices[0].message.content

    page_number = utils.get_pag_number(answer)

    return {
        "context": pay_load.context,
        "question": pay_load.question,
        "file_name": pay_load.file_name,
        "answer": answer,
        "page_number": page_number,
        "uuid": str(uuid4())}

    # pylint: disable=broad-exception-caught
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e)) from e


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
start_time = datetime.utcnow()
start_time = start_time.strftime(DATE_FORMAT)


@app.get(f"{PREFIX}/health_check")
async def health_check():
    """_summary_

    Returns:
        _type_: _description_
    """
    response = f"The server is up since {start_time}"
    return {"message": response, "start_uct_time": start_time}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

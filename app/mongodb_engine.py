"""Mongodb Client"""
import os
from typing import List, Dict
import dotenv
from pymongo import MongoClient
dotenv.load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    # pylint: disable=broad-exception-raised
    raise Exception("MONGODB_URL is not defined")

DB_NAME = "RAG"
EMBEDDING_COLLECTION = "DocumentEmbedding"
DOCUMENT_COLLECTION = "Document"


class MongoDB():
    """_summary_
    """

    def __init__(self) -> None:
        self.client = MongoClient(MONGODB_URL)
        self.db_name = DB_NAME
        self.db = self.client[self.db_name]

    def file_exist(self, file_name: str) -> bool:
        """_summary_

        Args:
            file_name (str): _description_

        Returns:
            bool: _description_
        """
        collection = self.db[DOCUMENT_COLLECTION]
        results = collection.find_one({"fileName": file_name})
        return results is not None

    def insert_document(self, file_name: str):
        """_summary_

        Args:
            file_name (str): _description_
        """
        # if not self.file_exist(file_name):
        collection = self.db[DOCUMENT_COLLECTION]
        collection.insert_one(
            {'fileName': file_name})

    def insert_embedding(self, doc_meta_list) -> List:
        """_summary_

        Args:
            doc_meta_list (_type_): _description_
            collection_name (str, optional): _description_. Defaults to "DocumentEmbedding".

        Returns:
            List: _description_
        """

        # if not self.file_exist(file_name):
        collection = self.db[EMBEDDING_COLLECTION]
        collection.insert_many(doc_meta_list)

    def vector_search(self, query_vector: List[float], file_name: str) -> List[Dict]:
        """_summary_

        Args:
            query_vector (List[float]): _description_

        Returns:
            List[Dict]: _description_
        """

        results = self.db[EMBEDDING_COLLECTION].aggregate([
            {

                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 5,
                    "limit": 5,

                    "filter": {"fileName": {"$eq": file_name}}
                }

            },
            {

                '$project': {
                    'embedding': 0,
                    "_id": 0,
                    "score": {"$meta": "vectorSearchScore"},
                }

            }

        ])

        return list(results)

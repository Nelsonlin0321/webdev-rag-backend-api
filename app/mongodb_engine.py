"""Mongodb Client"""
import os
from typing import Dict, List

import dotenv
import pandas as pd
from pymongo import MongoClient

dotenv.load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    # pylint: disable=broad-exception-raised
    raise Exception("MONGODB_URL is not defined")

DB_NAME = "RAG"
EMBEDDING_COLLECTION = "DocumentEmbedding"
DOCUMENT_COLLECTION = "Document"


def normalized_score(df):
    max_score = max(df['score'])
    min_score = min(df['score'])
    df['normalized_score'] = df['score'].apply(
        lambda x: (x-min_score)/(max_score-min_score))
    return df


def combine_vector_keyword_search(vector_search_results, keyword_search_results, limit: int = 5):

    df_keyword_search = pd.DataFrame(keyword_search_results)
    df_vector_search = pd.DataFrame(vector_search_results)

    both_hit_indices = set(df_vector_search[['textIdx']].merge(
        df_keyword_search[['textIdx']])['textIdx'])

    rest_size = limit - len(both_hit_indices)

    df_vector_search = normalized_score(df_vector_search)
    df_keyword_search = normalized_score(df_keyword_search)

    df_hybrid_search = pd.concat([df_keyword_search, df_vector_search])

    df_hybrid_search_1 = df_keyword_search[df_keyword_search['textIdx'].isin(
        both_hit_indices)].copy()

    df_hybrid_search_1['both_hit'] = True
    df_hybrid_search_2 = df_hybrid_search[~df_hybrid_search['textIdx'].isin(
        both_hit_indices)].copy()

    df_hybrid_search_2 = df_hybrid_search_2.sort_values(
        by='normalized_score', ascending=False).head(rest_size)
    df_hybrid_search_2['both_hit'] = False

    df_hybrid_search = pd.concat([df_hybrid_search_1, df_hybrid_search_2])

    results = df_hybrid_search.to_dict(orient='records')

    return results


class MongoDB():
    """_summary_
    """

    def __init__(self) -> None:
        self.client = MongoClient(MONGODB_URL)
        self.db_name = DB_NAME
        self.db = self.client[self.db_name]

    def file_exist(self, file_name: str) -> bool:
        collection = self.db[DOCUMENT_COLLECTION]
        results = collection.find_one({"fileName": file_name})
        return results is not None

    def insert_document(self, file_name: str):
        # if not self.file_exist(file_name):
        collection = self.db[DOCUMENT_COLLECTION]
        collection.insert_one(
            {'fileName': file_name})

    def insert_embedding(self, doc_meta_list) -> List:
        # if not self.file_exist(file_name):
        collection = self.db[EMBEDDING_COLLECTION]
        collection.insert_many(doc_meta_list)

    def vector_search(self, query_vector: List[float],
                      file_name: str, limit: int = 5) -> List[Dict]:

        results = self.db[EMBEDDING_COLLECTION].aggregate([
            {

                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit,
                    "limit": limit,

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

    def keyword_search(self, query: str, file_name: str, limit: int = 5) -> List[Dict]:

        search_query = [
            {
                '$search': {
                    'index': 'default',
                    'compound': {
                        'must': [
                            {
                                'text': {
                                    'query': query,
                                    'path': 'text'
                                }
                            }
                        ],
                        'filter': [
                            {
                                'text': {
                                    'query': file_name,
                                    'path': 'fileName'
                                }
                            }
                        ]
                    }
                }
            }, {
                '$match': {
                    'fileName': file_name
                }
            }, {
                '$addFields': {
                    'score': {
                        '$meta': 'searchScore'
                    }
                }
            }, {
                '$project': {
                    'embedding': 0
                }
            }, {
                '$limit': limit
            }
        ]

        results = self.db[EMBEDDING_COLLECTION].aggregate(search_query)

        return list(results)

    def hybrid_search(self, query_vector: List[float], query: str,
                      file_name: str, limit: int = 5) -> List[Dict]:

        vector_search_results = self.vector_search(query_vector=query_vector,
                                                   file_name=file_name, limit=limit)

        keyword_search_results = self.keyword_search(query=query,
                                                     file_name=file_name,
                                                     limit=limit)

        hybrid_search_results = combine_vector_keyword_search(
            vector_search_results, keyword_search_results, limit=limit)

        return hybrid_search_results

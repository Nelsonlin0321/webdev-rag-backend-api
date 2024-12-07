"""PDT to sentence embedding"""
import os
from typing import List
import requests
from llama_index.core import SimpleDirectoryReader

class PDFToSentenceEmbedding():
    """_summary_
    """

    def __init__(self):
        """_summary_
        """
        self.api_url = "https://api-inference.huggingface.co/models/BAAI/bge-small-en-v1.5"
        self.hf_token = os.environ['HF_TOKEN']

    def load_document(self, file_path):
        """_summary_

        Args:
            file_path (_type_): _description_

        Returns:
            _type_: _description_
        """
        documents = SimpleDirectoryReader(
            input_files=[file_path]
        ).load_data()

        return documents

    def generate_embedding(self, file_path):
        """_summary_

        Args:
            file_path (_type_): _description_

        Returns:
            _type_: _description_
        """
        documents = self.load_document(file_path)
        texts = [doc.text for doc in documents]
        embeddings = self.get_embeddings(texts)
        document_meta_list = [{"fileName": doc.metadata['file_name'],
                               "textIdx": idx,
                               "pageLabel": doc.metadata['page_label'],
                               "text": doc.text,
                               "embedding": embeddings[idx],
                               } for idx, doc in enumerate(documents)]
        return document_meta_list

    def __call__(self, file_path):
        document_meta_list = self.generate_embedding(file_path)
        return document_meta_list

    def get_embeddings(self,texts:List[str]):

        headers = {"Authorization": f"Bearer {self.hf_token}"}

        def query(payload):
            response = requests.post(self.api_url, headers=headers, json=payload,timeout=360)
            return response.json()
        output = query({
            "inputs": texts,
        })
        return output

"""PDT to sentence embedding"""
from sentence_transformers import SentenceTransformer
from llama_index import SimpleDirectoryReader


class PDFToSentenceEmbedding():
    """_summary_
    """

    def __init__(self):
        """_summary_
        """
        self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')

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
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        document_meta_list = [{"fileName": doc.metadata['file_name'],
                               "textIdx": idx,
                               "pageLabel": doc.metadata['page_label'],
                               "text": doc.text,
                               "embedding": embeddings[idx].tolist(),
                               } for idx, doc in enumerate(documents)]
        return document_meta_list

    def __call__(self, file_path):
        document_meta_list = self.generate_embedding(file_path)
        return document_meta_list

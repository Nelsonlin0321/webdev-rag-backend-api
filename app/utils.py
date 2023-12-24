import os
import shutil

TMP_DIR = "./temp"
os.makedirs(TMP_DIR, exist_ok=True)


def save_file(file):
    file_path = f"{TMP_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


def generate_prompt(retrieved_results):
    """_summary_

    Args:
        retrieved_results (_type_): _description_

    Returns:
        _type_: _description_
    """
    # pylint:disable=line-too-long
    num_retrieved = len(retrieved_results)
    retrieved_documents = "\n".join([
        f"{idx+1}. Retrieved sentences: {retrieval['text']}" for idx, retrieval in enumerate(retrieved_results)])
    prompt = f"Given the top {num_retrieved} retrieved document sentences, please generate a concise and accurate answer to the following question: \n {retrieved_documents}"
    return prompt

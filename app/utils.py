import os
import shutil
import json
import re

TMP_DIR = "./temp"
os.makedirs(TMP_DIR, exist_ok=True)


def save_file(file):
    file_path = f"{TMP_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


# def generate_prompt(retrieved_results):
#     """_summary_

#     Args:
#         retrieved_results (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     # pylint:disable=line-too-long
#     num_retrieved = len(retrieved_results)
#     retrieved_documents = "\n".join([
#         f"{idx+1}. Retrieved sentences: {retrieval['text']}" for idx, retrieval in enumerate(retrieved_results)])
#     prompt = f"Given the top {num_retrieved} retrieved document sentences, please generate a concise and accurate answer to the following question: \n {retrieved_documents}"
#     return prompt


def generate_prompt(retrieved_results):

    context_dict = [{"sentence": item['text'], "page number": item['pageLabel']}
                    for item in retrieved_results]

    context_json = json.dumps(context_dict)

    prompt = "Given retrieved document content with page number in json format, please generate a concise and accurate answer to the following question with a page number to indicate where the evidence is. " + \
        f"\n Retrieved document content: {context_json}"
    return prompt


def get_pag_number(string):

    page_number = 1
    pattern = "Page Number->(\d+)"
    # Find all matches of the pattern in the string
    founds = re.findall(pattern, string)

    if founds:
        try:
            page_number = int(founds[0])
        except IndexError:
            pass

    return page_number

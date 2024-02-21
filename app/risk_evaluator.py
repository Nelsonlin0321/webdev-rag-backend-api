from app.processor import PDFToSentenceEmbedding
from app.mongodb_engine import MongoDB
from app import utils
from openai import OpenAI
from tqdm import tqdm

import os
import json
import dotenv
dotenv.load_dotenv()


class RiskEvaluator():
    def __init__(self, file_name) -> None:
        self.embedding_generator = PDFToSentenceEmbedding()
        self.mongo_db_engine = MongoDB()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.file_name = file_name

    def get_answer(self, context, question):
        query_vector = self.embedding_generator.model.encode(
            context).tolist()

        retrieved_results = self.mongo_db_engine.hybrid_search(
            query_vector=query_vector, query=context,
            file_name=self.file_name, limit=5)

        prompt = utils.generate_prompt(retrieved_results)

        completion = self.client.chat.completions.create(
            model='gpt-3.5-turbo-16k',
            messages=[
                {'role': 'system',
                    'content': prompt,
                 },
                {"role": "user",
                    "content": question},
                {"role": "user",
                    "content":
                    """The answer should follow below json format: 
                    {"answer":"{YES OR NO}",
                    "page_number":"{page_number}",
                    "reason":"{reason}"}}"""
                 }
            ],
            temperature=0,
            stream=False
        )

        answer = completion.choices[0].message.content

        answer_dict = json.loads(answer)

        answer_dict['question'] = question

        return answer_dict

    def evaluate_risk(self, criteria_list, risk_level_definition):

        criteria_fulfillment_list = []
        for criteria in tqdm(criteria_list):
            answer_dict = self.get_answer(**criteria)
            criteria_fulfillment_list.append(answer_dict)

        criteria_fulfillment_list_json = json.dumps(criteria_fulfillment_list)

        completion = self.client.chat.completions.create(
            model='gpt-3.5-turbo-16k',
            messages=[
                {"role": "user",
                 "content":
                 f"""
                    RISK DEFINITION: 
                    {risk_level_definition}

                    FULFILLED CRITERIA IN JSON Format:
                    {criteria_fulfillment_list_json}
                    """ + """please return risk level by following this json format {"risk_level":"{risk_level}"}"}"""},
            ],
            temperature=0,
            stream=False
        )

        answer = completion.choices[0].message.content

        return criteria_fulfillment_list_json, json.loads(answer)

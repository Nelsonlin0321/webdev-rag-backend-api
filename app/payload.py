from pydantic import BaseModel


class PayLoad(BaseModel):
    question: str
    file_name: str

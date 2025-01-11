from pydantic import BaseModel


# Our Pydantic classes
class Answer_List(BaseModel):
    answer: list[str]

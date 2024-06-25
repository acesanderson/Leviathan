# from text_summarization import summarize_medium_text

# with open('GSR_2024.txt','r') as f:
#     coursera = f.read()

# summarize_medium_text(coursera)


# from Chain import Chain, Model, Parser, Prompt

# model = Model('gpt')
# prompt = Prompt("List ten mammals.")
# parser = Parser('list')
# chain = Chain(prompt, model, parser)
# response = chain.run()
# print(response.content)


from Chain import api_keys
import instructor
from pydantic import BaseModel
from openai import OpenAI
from typing import List
openai_api_key = api_keys['OPENAI_API_KEY']

# Define your desired output structure
class List_Answer(BaseModel):
    answer: List[str]

# Patch the OpenAI client
client = instructor.from_openai(OpenAI())

# Extract structured data from natural language
user_info = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=List_Answer,
    messages=[{"role": "user", "content": "Make a list of ten mammals."}],
)


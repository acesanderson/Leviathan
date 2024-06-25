I've been building my own framework to manage LLM calls. called Chain. Here's the code:

==============

==============

Read through the code and explain to me what the Parser class is for and how it works. Also, how do the other classes interact with it?


Here's an example of how I use a module called Instructor to parse LLM input.
It's a very powerful library that is very reliable, and I like it better than my Parser class.

```python
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
```


"""
This implements Chain of Density (COD) classes summarizing texts.
"""

from pydantic import BaseModel
from Chain import Chain, Model, Prompt, Parser 	# type: ignore

# Our config
chain_of_density_summary_length_in_words = 250
model_choice = "claude-3-haiku-20240307"
sample_text = "examples/zitron.txt"

# Our Pydantic classes
class Iteration(BaseModel):
	Missing_Entities: str
	Denser_Summary: str

class Chain_of_Density(BaseModel):
	COD: list[Iteration]

# Our prompt
chain_of_density_prompt_string = """
Here is an article: {{ARTICLE}}

You will generate increasingly concise, entity-dense summaries of the above Article.

Repeat the following 2 steps 5 times.

Step 1. Identify 1-3 informative Entities ("," delimited) from the Article which are missing from the previously generated summary.
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the Missing Entities.

A Missing Entity is:
- Relevant: to the main story.
- Specific: descriptive yet concise (5 words or fewer).
- Novel: not in the previous summary.
- Faithful: present in the Article.
- Anywhere: located anywhere in the Article.

Guidelines:
- The first summary should be long (~""" + str(chain_of_density_summary_length_in_words) + """  words) yet highly non-specific, 
containing little information beyond the entities marked as missing. Use overly verbose language and fillers
(e.g., "this article discusses") to reach ~""" + str(chain_of_density_summary_length_in_words) + """ words.
- Make every word count: re-write the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the Article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.

Remember, use the exact same number of words for each summary (around """ + str(chain_of_density_summary_length_in_words) + """ words).

Answer in JSON. The JSON should be a list (length 5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary".
""".strip()

# Our functions

def get_sample_text():
	"""
	Get a sample text to use for testing.
	"""
	with open(sample_text, 'r') as f:
		text = f.read()
	text = ' '.join(text.split(' ')[:1000])
	return text

def chain_of_density(text: str) -> str:
	"""
	Use Chain of Density prompt to summarize a text.
	The prompt returns a list of json objects; the second to last seems to have the best mix of named entities to words.
	"""
	prompt = Prompt(chain_of_density_prompt_string)
	model = Model(model_choice)
	parser = Parser(Chain_of_Density)
	chain = Chain(prompt, model, parser)
	summary = chain.run(input_variables = {'ARTICLE':text}, verbose=False)
	summary = summary.content.COD[-2].Denser_Summary		# this seems complicated because we have a type within a type; this is a List of Iterations.
	# return the content of the response, which is a list of dicts; grab the second to last one, and grab the value for Denser_Summary.
	return summary

if __name__ == "__main__":
	text = get_sample_text()
	summary = chain_of_density(text)
	print(summary)

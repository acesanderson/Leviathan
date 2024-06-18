"""
RESULTS: output of this process is shit. But I think there's something here that can be used for summarizing books.

This is a text summarization script that will do the following:
- detect, from length of text (and topic) the ideal summarization method
 - if short text, use Chain of Density prompt
 - if medium, chunk + perform extractive summarization + map/reduce
 - if long, a much more complex summarization method, including the use of embeddings.

Taking inspiration from here:
https://sourajit16-02-93.medium.com/text-summarization-unleashed-novice-to-maestro-with-llms-and-instant-code-solutions-8d26747689c4
"""
from Chain import Chain, Model, Prompt, Parser
from nltk.tokenize import word_tokenize			# for tokenizing texts

# Customizable settings
model_choice = "mistral:latest"
chain_of_density_summary_length_in_words = 100 # set to 80 by default according to original paper.
text_sizes = {
	'short': 1500,
	'medium': 10000,
	'long': 10001
}
ideal_chunk_size_by_words = 1000

# Our prompts
# == this needs to be set to longer character count
chain_of_density_prompt_string = f"""
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
- The first summary should be long (4-5 sentences, ~""" + str(chain_of_density_summary_length_in_words) + """ words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this article discusses") to reach ~80 words.
- Make every word count: re-write the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the Article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.

Remember, use the exact same number of words for each summary.

Answer in JSON. The JSON should be a list (length 5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary".
""".strip()

keyword_extract_prompt_string = """
You are an efficient key word detector. Your task is to extract only all the important key words and phrases without any duplicates from the below chunk of text.

Text: {{text_chunk}}

Think "step by step" to identify and all the important key words and pharses only and output should be comma seperated. Only return the list of keywords, nothing more.
""".strip()

summarize_chunk_prompt_string = """
You are an expert text summarizer. Given the below text content and the important key words, write a concise but information loaded summary.

Text Content: {{text_chunk}}

Important Keywords: {{key_words}}

Think "step by step" how to utilize both the important keywords and text content to create a great concise summary.
""".strip()

reduce_prompt_string = """
The following is set of summaries:

{% for summary in summaries %}
##################### 
{{summary}}
##################### 
{% endfor %}

Take these and distill them into one final, consolidated summary.
""".strip()

# Some test texts for testing purposes
def generate_test_texts():
	"""
	Generate some different versions of our example text.
	"""
	with open('/home/bianders/Brian_Code/Leviathan/tests/article.txt', 'r') as f:
		text = f.read()
	tokenized_text = tokenize_text(text)
	short = tokenized_text[:text_sizes['short']]
	medium = tokenized_text[:text_sizes['medium']]
	long = tokenized_text[:]
	result = list(map(detokenize, [short, medium, long]))
	return result

# First, tokenize, classify, and route texts for summarization.
def tokenize_text(text: str) -> list[str]:
	"""
	Splits the text into chunks of specified word count using NLTK for tokenization.
	Uses NLTK library work_tokenize
	"""
	# Tokenize the text into words
	words = word_tokenize(text)
	# Create chunks of the specified size
	return words

def detokenize(words: list[str]) -> str:
	"""
	De-chunk text.
	"""
	return ' '.join(words)

def chunk_text_by_words(text: str, chunk_size: int = ideal_chunk_size_by_words) -> list[str]:
	tokens = tokenize_text(text)
	# Chunk into a list of lists of strings
	chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]
	# Detokenize into summarizable smaller texts.
	chunks = list(map(detokenize, chunks))
	return chunks

def categorize_text_length(text: str): # tokenize for length for this purpose
	"""
	Return short, medium, or long.
	"""
	tokenized_text = word_tokenize(text)
	if len(tokenized_text) < text_sizes['short']:
		return "short"
	elif len(tokenized_text) < text_sizes['medium']:
		return "medium"
	else:
		return "long"

def chain_of_density(text: str) -> str:
	"""
	Use Chain of Density prompt to summarize a text.
	"""
	print("\tSummarizing text...")
	prompt = Prompt(chain_of_density_prompt_string)
	model = Model(model_choice)
	chain = Chain(prompt, model)
	summary = chain.run({'ARTICLE':text}, verbose=False)
	return summary.content

def extract_keywords(text_chunk: str) -> list[str]:
	"""
	Returns a list of important keywords from the given text chunk.
	"""
	print("\tExtracting keywords...")
	prompt = Prompt(keyword_extract_prompt_string)
	model = Model(model_choice)
	parser = Parser('list')
	chain = Chain(prompt, model, parser)
	keywords = chain.run({'text_chunk':text_chunk}, verbose=False)
	return keywords

def summarize_chunk_with_keywords(text_chunk: str, keywords: list[str]) -> str:
	"""
	Returns extractive summary on a text chunk using the given keywords.
	"""
	print("\tSummarizing chunk...")
	prompt = Prompt(summarize_chunk_prompt_string)
	model = Model(model_choice)
	chain = Chain(prompt, model)
	chunk_summary = chain.run({'text_chunk':text_chunk, 'key_words':keywords}, verbose=False)
	return chunk_summary

def map_chain(text_chunks: list[str]) -> dict:
	"""
	Takes a list of text chunks, performs extractive summarization on each, and returns a dict, with chunks as keys and summaries as values.
	"""
	summary_map = {}
	for index, chunk in enumerate(text_chunks):
		print(f"Summarizing chunk {index+1} of {len(text_chunks)}...")
		keywords = extract_keywords(chunk)
		summary_map[chunk] = summarize_chunk_with_keywords(chunk, keywords)
	return summary_map

def reduce_chain(summary_map: dict) -> str:
	"""
	Combines the summaries from the chunks into a single summary.
	"""
	prompt = Prompt(reduce_prompt_string)
	model = Model(model_choice)
	chain = Chain(prompt, model)
	summary = chain.run({'summaries':summary_map.values()}, verbose=False)
	return summary

def summarize_short_text(text: str) -> str:
	"""
	Use Chain of Density prompt to summarize a short text.
	"""
	summary = ""
	summary = chain_of_density(text)
	return summary

def summarize_medium_text(text: str) -> str:
	"""
	Wrapper function.
	Summarizes a medium-length text using chunking, extractive summarization, and map/reduce.
	"""
	text_chunks = chunk_text_by_words(text)
	summary_map = map_chain(text_chunks)
	final_summary = reduce_chain(summary_map)
	if final_summary == None:
		print("No short summary generated")
	return final_summary.content

def summarize_long_text(text:str) -> str:
	"""
	Summarizes a long text using embeddings.
	"""
	summary = ""
	return summary

def main() -> str:
	"""
	Tset function using an example article chopped to varying lengths.
	"""	
	short, medium, long = generate_test_texts()
	short_summary = summarize_short_text(short)
	medium_summary = summarize_medium_text(medium)
	long_sunmary = summarize_long_text(long)
	print("Short summary:\n====================\n" + short_summary)
	print("Medium summary:\n====================\n" + medium_summary)
	print("Long summary:\n====================\n" + long_sunmary)
	return short_summary, medium_summary, long_sunmary

if __name__ == '__main__':
	main()

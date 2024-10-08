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
from Chain import Chain, Model, Prompt, Parser 	# type: ignore
from nltk.tokenize import word_tokenize			# for tokenizing texts
from pydantic import BaseModel, conlist

# Define our classes for Parser
class Answer_List(BaseModel):
	answer: list[str]

class Iteration(BaseModel):
	Missing_Entities: str
	Denser_Summary: str

class Chain_of_Density(BaseModel):
	COD: list[Iteration]

# Customizable settings
def get_config():
	# Define your variables here
	model_choice = "gpt"
	chain_of_density_summary_length_in_words = 250
	text_sizes = {
		'short': 1500,
		'medium': 10000,
		'long': 10001
	}
	ideal_chunk_size_by_words = 1000
	# Get the local variables at this point
	num_clusters = 11
	test_text_path = 'tests/article.txt'
	test_book_path = 'tests/NLTK.txt'
	local_vars = locals()
	# You can now return the local_vars as your config dictionary
	return local_vars

config_dict = get_config()

# Our prompts
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
- The first summary should be long (~""" + str(config_dict['chain_of_density_summary_length_in_words']) + """  words) yet highly non-specific, 
containing little information beyond the entities marked as missing. Use overly verbose language and fillers
(e.g., "this article discusses") to reach ~""" + str(config_dict['chain_of_density_summary_length_in_words']) + """ words.
- Make every word count: re-write the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the Article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.

Remember, use the exact same number of words for each summary (around """ + str(config_dict['chain_of_density_summary_length_in_words']) + """ words).

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
	Generate some different versions of our example text for short, medium, and long summarization tasks.
	"""
	with open(config_dict['test_text_path'], 'r') as f:
		text = f.read()
	tokenized_text = tokenize_text(text)
	short = tokenized_text[:config_dict['text_sizes']['short']]
	medium = tokenized_text[:config_dict['text_sizes']['medium']]
	long = tokenized_text[:]
	result = list(map(detokenize, [short, medium, long]))
	return result

def generate_test_book():
	"""
	Generate a test book.
	"""
	with open(config_dict['test_book_path'], 'r') as f:
		book = f.read()
	return book

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

def chunk_text_by_words(text: str, chunk_size: int = config_dict['ideal_chunk_size_by_words']) -> list[str]:
	"""
	Takes a string (and optional chunk size), tokenizes + splits, and returns a set of chunks for the text.
	"""
	tokens = tokenize_text(text)
	# Chunk into a list of lists of strings
	chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]
	# Detokenize into summarizable smaller texts.
	chunks = list(map(detokenize, chunks))
	print(f"Split text in {len(chunks)} chunks.")
	return chunks

def categorize_text_length(text: str): # tokenize for length for this purpose
	"""
	Return short, medium, or long.
	"""
	tokenized_text = word_tokenize(text)
	if len(tokenized_text) < config_dict['text_sizes']['short']:
		return "short"
	elif len(tokenized_text) < config_dict['text_sizes']['medium']:
		return "medium"
	else:
		return "long"

# now our summarization functions

def chain_of_density(text: str) -> str:
	"""
	Use Chain of Density prompt to summarize a text.
	The prompt returns a list of json objects; the second to last seems to have the best mix of named entities to words.
	"""
	print("Summarizing text...")
	prompt = Prompt(chain_of_density_prompt_string)
	model = Model(config_dict['model_choice'])
	parser = Parser(Chain_of_Density)
	chain = Chain(prompt, model, parser)
	summary = chain.run({'ARTICLE':text}, verbose=False)
	summary = summary.content.COD[-2].Denser_Summary		# this seems complicated because we have a type within a type; this is a List of Iterations.
	# return the content of the response, which is a list of dicts; grab the second to last one, and grab the value for Denser_Summary.
	return summary

def extract_keywords(text_chunks: list[str]) -> list[tuple[str,str]]:
	"""
	Refactored to use async.
	Takes a list of text chunks, and returns a list of tuples, with the chunk and its keywords.
	"""
	print("Extracting keywords...")
	extract_keywords_prompts = []
	prompt = Prompt(keyword_extract_prompt_string)
	model = Model('gpt3')
	for chunk in text_chunks:
		extract_keywords_prompt = prompt.render({'text_chunk':chunk})
		extract_keywords_prompts.append(extract_keywords_prompt)
	print("running async: generating keywords for chunks")
	keywords_list = model.run_async(prompts = extract_keywords_prompts, pydantic_model = Answer_List, verbose = True)
	assert len(keywords_list) == len(text_chunks)
	chunks_with_keywords = list(zip(text_chunks, keywords_list))
	return chunks_with_keywords

def summarize_chunks_with_keywords(chunks_with_keywords: list[tuple[str]], run_async = False) -> list[str]:
	"""
	This routes to either the async or sync version of the function.
	"""
	if run_async:
		return summarize_chunks_with_keywords_async(chunks_with_keywords)
	else:
		return summarize_chunks_with_keywords_sync(chunks_with_keywords)

def summarize_chunks_with_keywords_sync(chunks_with_keywords: list[tuple[str]]) -> list[str]:
	"""
	Returns extractive summary on a text chunk using the given keywords.
	This is the synchronous version of the function.
	"""
	prompt = Prompt(summarize_chunk_prompt_string)
	model = Model('gpt3')
	summarized_chunks = []
	for chunk, keywords in chunks_with_keywords:
		chain = Chain(prompt, model)
		summary = chain.run({'text_chunk':chunk, 'key_words':keywords}, verbose=False)
		summarized_chunks.append(summary.content)
	return summarized_chunks

def summarize_chunks_with_keywords_async(chunks_with_keywords: list[tuple[str]]) -> list[str]:
	"""
	Returns extractive summary on a text chunk using the given keywords.
	"""
	summarize_chunks_prompts = []
	prompt = Prompt(summarize_chunk_prompt_string)
	model = Model('gpt3')
	for chunk, keywords in chunks_with_keywords:
		summarize_chunk_prompt = prompt.render({'text_chunk':chunk, 'key_words':keywords})
		summarize_chunks_prompts.append(summarize_chunk_prompt)
	print("running async: summarizing chunks")
	summarized_chunks = model.run_async(prompts = summarize_chunks_prompts, verbose = True)
	return summarized_chunks

def map_chain(text_chunks: list[str]) -> list[str]:
	"""
	Takes a list of text chunks, performs extractive summarization on each, and returns a dict, with chunks as keys and summaries as values.
	"""
	print("Summarizing chunks...")
	chunks_with_keywords = extract_keywords(text_chunks)
	# assuming 30 is a limit for async; can change this after experimentation.
	if len(chunks_with_keywords) < 31:
		summarized_chunks = summarize_chunks_with_keywords(chunks_with_keywords, run_async = True)
	else:
		summarized_chunks = summarize_chunks_with_keywords(chunks_with_keywords, run_async = False)
	return summarized_chunks

def reduce_chain(summarized_chunks: list[str]) -> str:
	"""
	Combines the summaries from the chunks into a single summary.
	"""
	print("Summarizing the summaries.")
	prompt = Prompt(reduce_prompt_string)
	model = Model(config_dict['model_choice'])
	chain = Chain(prompt, model)
	summary = chain.run({'summaries':summarized_chunks}, verbose=False)
	return summary

# our wrapper functions for the three text sizes

def summarize_short_text(text: str) -> str:
	"""
	Use Chain of Density prompt to summarize a short text.
	"""
	summary = chain_of_density(text)
	return summary

def summarize_medium_text(text: str) -> str:
	"""
	Wrapper function.
	Summarizes a medium-length text using chunking, extractive summarization, and map/reduce.
	"""
	text_chunks = chunk_text_by_words(text)
	summarized_chunks = map_chain(text_chunks)
	final_summary = reduce_chain(summarized_chunks)
	if final_summary == None:
		print("No medium summary generated")
	return final_summary.content

def summarize_long_text(text:str) -> str:
	"""
	Summarizes a long text using embeddings.
	Creating this in another file.
	"""
	# text_chunks = chunk_text_by_words(text)
	# db = get_embeddings(text_chunks)
	# clusters = cluster_embeddings(db)
	# exemplar_clusters = pick_best_embeddings(clusters)
	# summary_map = map_chain(exemplar_clusters)
	# final_summary = reduce_chain(summary_map)
	# if final_summary == None:
	# 	print("No long summary generated.")
	# return final_summary.content

def main() -> str:
	"""
	Test function using an example article chopped to varying lengths.
	"""	
	short, medium, long = generate_test_texts()
	short_summary = summarize_short_text(short)
	medium_summary = summarize_medium_text(medium)
	# long_summary = summarize_long_text(long)
	print("Short summary:\n====================\n" + short_summary)
	print("Medium summary:\n====================\n" + medium_summary)
	# print("Long summary:\n====================\n" + long_sunmary)
	# return short_summary, medium_summary, long_sunmary

if __name__ == '__main__':
	main()


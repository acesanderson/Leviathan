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
from Chain import Chain, Model, Prompt

with open('article.txt', 'r') as f:
	article_text = f.read()

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

def chunk_text(text: str, size: int = 1500) -> list[str]:
	"""
	Splits the given text into chunks of the specified size.
	
	Args:
	text (str): The text to be chunked.
	size (int): The size of each chunk.
	
	Returns:
	list of str: A list containing the chunks of text.
	"""
	return [text[i:i+size] for i in range(0, len(text), size)]

def extract_keywords(text_chunk: str) -> list[str]:
	"""
	Returns a list of important keywords from the given text chunk.
	"""
	print("\tExtracting keywords...")
	prompt = Prompt(keyword_extract_prompt_string)
	model = Model('mistral:latest')
	chain = Chain(prompt, model)
	keywords = chain.run({'text_chunk':text_chunk}, verbose=False)
	return keywords

def summarize_chunk_with_keywords(text_chunk: str, keywords: list[str]) -> str:
	"""
	Returns extractive summary on a text chunk using the given keywords.
	"""
	print("\tSummarizing chunk...")
	prompt = Prompt(summarize_chunk_prompt_string)
	model = Model('mistral:latest')
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
	model = Model('mistral:latest')
	chain = Chain(prompt, model)
	summary = chain.run({'summaries':summary_map.values()}, verbose=False)
	return summary

def summarize_medium_text(text: str) -> str:
	"""
	Wrapper function.
	Summarizes a medium-length text using chunking, extractive summarization, and map/reduce.
	"""
	text_chunks = chunk_text(text)
	summary_map = map_chain(text_chunks)
	final_summary = reduce_chain(summary_map)
	return final_summary

if __name__ == '__main__':
	summary = summarize_medium_text(article_text)
	print(summary)

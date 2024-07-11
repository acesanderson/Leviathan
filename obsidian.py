
"""
This will be a command line utility I can use to add things to my obsidian vault.

Importable functions:
- import_summary

Ingests the following data:
- youtube url -> transcript (Morphy/YouTube)
- article url -> article text (Morphy/extracted_articles)

This uses gpt-4o by default, so it's not free. Switch to an ollama model if you want to use it for free.

Next up: automatically grab html (or PDF) versions of arxiv papers and summarize them.

EVENTUALLY this will use a more sophisticated set of summarization techniques that are currently being worked out in text_summarization.py.
"""

from download_article import download_article                   # type: ignore
from download_youtube_transcript import download_transcript     # type: ignore
from Chain import Chain, Model, Prompt, Parser                  # type: ignore
import sys
import os
import argparse
from typing import Union, Tuple
from pydantic import BaseModel
from datetime import datetime

# Define our variables
# -----------------------------------------------------

# get OBSIDIAN_PATH from environment variable
obsidian_path = os.environ.get('OBSIDIAN_PATH')
# switch this if on different comp
summarized_urls = obsidian_path + '/Summarized_URLs.md'
# example url for testing
# url = 'https://www.androidauthority.com/rabbit-r1-is-an-android-app-3438805'

# Our pydantic models for parsing
# -----------------------------------------------------

# for our default summarization prompt
class Summary(BaseModel):
	title: str
	summary: str

# for our YouTube -> Article chain
class YouTube_Article(BaseModel):
	title: str
	article: str

# Define our prompts
# -----------------------------------------------------

default_prompt_string = """
Summarize the key points from the following article or youtube transcript. Structure the summary with clear headings and subheadings.
Distill the main ideas concisely, but include key details and takeaways. Use direct quotes sparingly, only to highlight the most insightful or impactful statements.
Aim for a summary that is around 500-1,000 words in length.

Structure the summary as follows:

**Main Topic 1**
- Key point
- Key point

**Main Topic 2**
- Key point
- Key point

*Conclusion**
Summarize overarching takeaways and conclusions
What are the main lessons or insights that someone should take away from this text?

YOUR ANSWER SHOULD HAVE TWO PARTS:
1. a TITLE, which should be a concise and informative summary of the text to help with quick reference.
The Title should not contain any special characters, especially not square brackets. Do not include colons.
2. the SUMMARY itself.

The text you will be summarizing is as follows:
============================================
{{transcript}}
============================================
""".strip()

custom_prompt_string = """
You are a highly skilled librarian with extensive experience in research, information synthesis, and comprehensive summarization.
Your task is to read and analyze the article or transcript that's provided at the end of this message.

After thoroughly reviewing the material, your goal is to provide a detailed, accurate, and focused summary that directly addresses
the following user query:

============================================
{{custom_prompt}}
============================================

Please follow these guidelines:

- Do not address the user directly; these should be instantly digestible notes.
- Carefully read and comprehend the entire text.
- Focus on extracting information that is most relevant to the user's query, but also include important context and supporting details.
- Provide a rich and comprehensive summary between 500-1,000 words, unless the query demands a different length.
- Structure your summary in a logical manner, potentially using subheadings if it aids clarity.
- If the text contains multiple viewpoints or arguments, present them thoroughly and objectively.
- Include key facts, figures, or statistics, providing context for their significance.
- If relevant, discuss the methodology or approach used in the source material.
- If the source material is insufficient to fully answer the query, state this clearly, explain what information is missing.
- Avoid inserting personal opinions or information not present in the source material.

End your summary with a paragraph that encapsulates the main takeaways as they relate to the user's query.

Remember, your goal is to provide a comprehensive and nuanced summary of the source material that specifically addresses
the user's query.

YOUR ANSWER SHOULD HAVE TWO PARTS:
1. a TITLE, which should be a concise and informative summary of the text to help with quick reference.
The Title should not contain any special characters, especially not square brackets. Do not include colons.
2. the SUMMARY itself.

The text you will be summarizing is as follows:
============================================
{{transcript}}
============================================
"""

youtube_article_string = """
Here is a YouTube transcript which is very messy.
Please rework the transcript into readable text.
Please retain all the detail you can, while making the text read like an article.
If it makes sense for the article, use Markdown formatting for headers or other text elements, but don't overdo it.

YOUR ANSWER SHOULD HAVE TWO PARTS:
1. a TITLE, which should be a concise and informative summary of the text to help with quick reference.
The Title should not contain any special characters, especially not square brackets. Do not include colons.
2. the ARTICLE itself.

Transcript:
============================================
{{transcript}}
============================================
""".strip()

article_title_string = """
Here is an article. Please determine the title of the article.
If you see it verbatim within the article, simply return that.
If you can't find a title, please generate one based on the content of the article.
The only special characters you can use in the title are hyphens, underscores, parentheses, and commas.
ONLY return the title, no extra text. This will be used to a title a file, and it will break if you don't follow these rules.

============================================
{{article}}
============================================
""".strip()

# Our functions
# -----------------------------------------------------

def retrieve_summarized_urls() -> list[str]:
	"""
	This checks if we've already downloaded the article or transcript.
	"""
	with open(summarized_urls, 'r') as f:
		urls = f.read()
	urls = urls.split('\n')
	return urls

def save_summarized_url(url):
	"""
	Save the URL to the list of summarized URLs.
	"""
	with open(summarized_urls, 'a') as f:
		f.write(url + '\n')

def parse_input(input, transcript_cleanup = False) -> Union[str, tuple]:
	"""
	This takes user input (i.e. the url) and either downloads the article or the Youtube transcript.
	If user wants a cleaned up transcript (not s summary at all), set transcript_cleanup to True,
	and function returns a tuple of title, article.
	"""
	urls = retrieve_summarized_urls()
	if input in urls:
		raise ValueError('URL has already been summarized.')
	elif 'youtube' in input:
		# this is bad code, since we either return a string or a tuple
		transcript = download_transcript(input)
		if transcript_cleanup:
			transcript = clean_up_transcript(transcript)
		return transcript
	elif 'http' in input:
		# again, bad code, but we either return a string or a tuple
		article = download_article(input)
		if transcript_cleanup:
			title = generate_title_for_article(article)
			return title, article
		return download_article(input)
	else:
		raise ValueError('Input must be a YouTube URL or an article URL.')

def clean_up_transcript(transcript: str) -> str:
	"""
	Cleans up YouTube transcript. This is not for summarization, but rather to convert this to a readable article and save to Obsidian.
	"""
	prompt = Prompt(youtube_article_string)
	model = Model('claude')
	parser = Parser(YouTube_Article)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = {'transcript': transcript}, verbose=False)
	title, article = response.content.title, response.content.article
	return title, article

def generate_title_for_article(article: str) -> str:
	"""
	Takes an article and generates a title for the article.
	"""
	prompt = Prompt(article_title_string)
	model = Model('gpt3')
	chain = Chain(prompt, model)
	response = chain.run(input_variables = {'article': article}, verbose=False)
	return response.content

def summarize_text(text: str, custom_prompt: str = None):
	"""
	If no custom prompt given, use default prompt.
	If custom prompt provided, uses a different template.
	"""
	# Define our input variables. If default prompt, custom_prompt won't be used.
	input_variables = {'transcript': text, 'custom_prompt': custom_prompt}
	# Assign the right prompt string
	if custom_prompt:
		prompt_string = custom_prompt_string
	else:
		prompt_string = default_prompt_string
	# Create our chain
	model = Model('gpt')
	prompt = Prompt(prompt_string)
	parser = Parser(Summary)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables, verbose=False)
	# Extract title and summary from the Summary object we generated.
	title, summary = response.content.title, response.content.summary
	summary = summary.strip()
	return title, summary

def import_summary(url: str) -> Tuple[str, str]:
	"""
	This is the importable version of the script, takes URL and returns summary.
	Needs to be updated to reflect new functionality / parsers.
	"""
	data = parse_input(url)
	title, summary = summarize_text(data)
	return title, summary

def main(url: str, custom_prompt = None):
	"""Takes url, summarizes, and saves to Obsidian."""
	try:
		data = parse_input(url)
	except ValueError as e:
		print("ValueError: " + str(e))
		sys.exit(1)
	if data:
		title, summary = summarize_text(data, custom_prompt)
		print(title)
		print('=============================================')
		print(summary)
		print('=============================================')
		filename = save_to_obsidian(title, summary, url)
		print(f'Saved to Obsidian: {filename}')
	else:
		print('Output is empty.')

def save_entire_article(url: str):
	"""
	No summarization here; just save the article. Title is just "Saved_Article" + timestamp.
	"""
	title, article = parse_input(url, transcript_cleanup = True)
	save_to_obsidian(title, article, url)

def save_to_obsidian(title: str, summary: str, url: str) -> str:
	filename = f'{obsidian_path}/{title}.md'
	summary = url + "\n\n" + summary
	with open(filename, 'w') as f:
		f.write(summary)
	save_summarized_url(url)
	return filename

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Summarize and save to Obsidian.')
	parser.add_argument('url', type=str, help='URL to summarize.')
	# if user puts "--p" or "--path" in command line, take what's after it and assign it to "custom_prompt"
	# add an argument for the prompt
	parser.add_argument('--p', '--prompt', nargs="?", type=str, dest='prompt', help='Prompt to use for summarization.')
	parser.add_argument('--a', '--all', action='store_true', dest='all', help='Save the entire article to Obsidian.')
	args = parser.parse_args()
	url = args.url
	all = args.all
	custom_prompt = args.prompt
	print(f"URL: {args.url}")
	print(f"Custom Prompt: {args.prompt}")
	# if args, run main()
	if all:
		save_entire_article(url)
	elif custom_prompt:
		main(url, custom_prompt = custom_prompt)
	else:
		main(url, custom_prompt = None)

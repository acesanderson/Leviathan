"""
This is replacing Obsidian script, as Save to Obsidian is now a plugin.
This scripts allows a user to bring in content from YouTube, a URL, or a file (say, an epub).

Various use cases:
leviathan "youtubeurl" -save -f 
leviathan "youtubeurl" -a | twig "Look at this transcript." -a "What would this look like as a curriculum?" > output.txt
-cod for chain density AFTER summarization

### Other ideas
create a separate script for identifying token sizes, generating test articles of various token sizes, and testing llm calls and prompts for maximum working size.
This will determine the boundaries for using different tyypes of summarization techniques.
"chat with the doc":
- depending on size, article can be used as persistent context, or we vectorize the article and leverage RAG

LONG TERM: this is the "window" script to various other scripts. It's the starting point for getting text into various NLP and LLM flows.
"""

# Imports can take a while, so we'll give the user a spinner.
# -----------------------------------------------------------------

from rich.console import Console
console = Console(width=100) # for spinner

with console.status("[bold green]Loading...", spinner="dots"):
	from download_article import download_article                   # type: ignore
	from download_youtube_transcript import download_transcript     # type: ignore
	from Chain import Chain, Model, Prompt, Parser                  # type: ignore
	from Save_to_obsidian import save_to_obsidian					# type: ignore
	from message_store import MessageStore							# type: ignore
	from CoD import chain_of_density								# type: ignore
	import os
	import argparse
	import sys
	from rich.markdown import Markdown
	import tiktoken

# Define our variables
# -----------------------------------------------------

obsidian_path = os.environ.get('OBSIDIAN_PATH')
messagestore_path = ".leviathan_message_store.pickle"
example_article = "https://www.androidauthority.com/rabbit-r1-is-an-android-app-3438805"
example_long_article = "https://arxiv.org/html/2309.02427v3"
example_super_long_article = "https://arxiv.org/html/2408.14743v1"
example_youtube = "https://www.youtube.com/watch?v=jEINHwQkobk"
example_long_youtube = "https://www.youtube.com/watch?v=8t65bss7U74"

# Define our prompts
# -----------------------------------------------------

YouTube_prompt_string = """
You are tasked with summarizing a YouTube video transcript. The purpose of this summary is to highlight the most interesting and useful information from the video, focusing on its unique contributions rather than generic content. This summary will help users quickly understand the key points and valuable insights without watching the entire video.

You will be provided with the following transcript:

<transcript>
{{transcript}}
</transcript>

Begin by determining the word count of the provided transcript. This will be used to calculate the appropriate length for your summary.

Read through the entire transcript carefully, paying attention to the main topics, key arguments, and unique insights presented. As you read, make mental notes of the most important points and any recurring themes.

Your summary should be structured as follows:
1. Brief introduction (1-2 sentences about the video's topic and speaker, if known)
2. Main topics covered (bullet point list)
3. Key insights and unique contributions (3-5 paragraphs)
4. Notable quotes or examples (2-3 direct quotes that illustrate important points)
5. Conclusion (1-2 sentences summarizing the video's significance or main takeaway)

When writing the summary, follow these guidelines:
1. Calculate the summary length based on the transcript word count:
   - For transcripts over 6,000 words, aim for a summary of at least 2,000 words.
   - For shorter transcripts, use a ratio of approximately 1:3 (summary:transcript). For example, a 3,000-word transcript should have a summary of about 1,000 words.
2. Focus on the unique contributions and insights presented in the video. Avoid generic summaries that could apply to any video on the topic.
3. Use specific examples, data points, or arguments from the transcript to illustrate key points.
4. Highlight any novel ideas, counterintuitive claims, or particularly compelling arguments made in the video.
5. If the video presents multiple perspectives on a topic, ensure that you accurately represent each viewpoint.
6. Pay attention to the speaker's tone and emphasis, noting any points they seem to consider particularly important.
7. If the transcript includes descriptions of visual elements (e.g., charts, demonstrations), mention these in your summary if they are crucial to understanding the content.

To avoid sounding too generic:
1. Use specific terminology and jargon from the video when appropriate, explaining it if necessary.
2. Highlight any unique methodologies, case studies, or research mentioned in the video.
3. Note any personal anecdotes or experiences shared by the speaker that illustrate key points.
4. Identify and emphasize any calls to action or practical applications suggested in the video.

For shorter transcripts (under 3,000 words):
1. Adjust the summary length to approximately 1:3 ratio of the transcript word count.
2. Focus on the 2-3 most important points rather than trying to cover everything.
3. Combine the "Key insights" and "Notable quotes" sections if necessary.

Before writing your final summary, use <scratchpad> tags to outline the main points and structure of your summary. This will help you organize your thoughts and ensure you cover all important aspects of the video.

Present your final summary within <summary> tags. Use appropriate markdown formatting for headings, bullet points, and emphasis where necessary.

Remember, the goal is to provide a comprehensive yet concise summary that captures the essence of the video and its unique contributions to the topic at hand.
""".strip()

Article_prompt_string = """
You are tasked with summarizing a text article. The purpose of this summary is to distill the most important information, key arguments, and significant insights from the article. This summary will help readers quickly grasp the main points and decide whether to read the full article.
You will be provided with the following article:

<article>
{{article}}
</article>

Begin by determining the word count of the provided article. This will be used to calculate the appropriate length for your summary.
Read through the entire article carefully, paying attention to the following elements:

1. The headline and subheadings
2. The introduction and conclusion
3. Topic sentences of each paragraph
4. Key statistics, data, or research findings
5. Quotes from relevant sources or experts
6. The author's main arguments or thesis

Your summary should be structured as follows:

1. Article metadata (title, author, publication, date if available)
2. Brief introduction (1-2 sentences about the article's main topic and purpose)
3. Main points or arguments (bullet point list)
4. Key findings or insights (2-3 paragraphs)
5. Notable quotes or data points (1-2 direct quotes or statistics that support the main points)
6. Conclusion (1-2 sentences summarizing the article's significance or main takeaway)

When writing the summary, follow these guidelines:

1. Calculate the summary length based on the article word count:
- For articles over 3,000 words, aim for a summary of 800-1,000 words.
- For shorter articles, use a ratio of approximately 1:4 (summary:article). For example, a 1,200-word article should have a summary of about 300 words.
2. Focus on the unique contributions, insights, or arguments presented in the article.
3. Maintain the article's tone (e.g., formal for academic papers, more casual for blog posts).
4. Use specific examples, data points, or arguments from the article to illustrate key points.
5. Highlight any novel ideas, counterintuitive claims, or particularly compelling arguments made by the author.
6. If the article presents multiple perspectives on a topic, ensure that you accurately represent each viewpoint.
7. Pay attention to the author's emphasis, noting any points they seem to consider particularly important.

To ensure a comprehensive and accurate summary:

1. Identify and explain any specialized terminology or jargon used in the article.
2. Highlight the methodology, data sources, or research design if it's a scientific or academic article.
3. Note any limitations or caveats mentioned by the author regarding their findings or arguments.
4. Identify the intended audience of the article and any specific calls to action.

For different types of articles:

1. News articles: Focus on the "5 W's and H" (Who, What, When, Where, Why, and How).
2. Opinion pieces: Clearly state that it's an opinion article and summarize the author's main arguments and supporting evidence.
3. Research articles: Emphasize the research question, methodology, key findings, and implications.
4. Feature articles: Capture the narrative arc while highlighting the main informational points.

Before writing your final summary, use <scratchpad> tags to outline the main points and structure of your summary. This will help you organize your thoughts and ensure you cover all important aspects of the article.
Present your final summary within <summary> tags. Use appropriate markdown formatting for headings, bullet points, and emphasis where necessary.
Remember, the goal is to provide an accurate, concise, and well-structured summary that captures the essence of the article, its key points, and its significance within its field or topic.
""".strip()

Format_transcript_prompt_string = """
You are an experienced transcription editor who is good at converting spoken content into well-structured text.

Your task is to format a raw transcript into a readable and coherent document that accurately represents the original spoken content.

Please follow these guidelines to format the transcript:
- Read through the entire transcript to understand the overall topic and flow.
- Create a descriptive title that reflects the main subject of the transcript.
- Break the transcript into logical paragraphs. Each distinct idea or point should start a new paragraph.
- Add 3-5 main headers (using ## in markdown) to divide the content into major sections. These should reflect natural breaks or shifts in the topic.
- Correct obvious grammatical errors and typos, but maintain the speaker's original wording as much as possible.
- Convert run-on sentences into proper sentence structures, using punctuation to improve clarity.
- Capitalize proper nouns, names, and the beginnings of sentences.
- Spell out numbers under 10 and retain numerical format for larger numbers, unless they begin a sentence.
- Format any lists mentioned in the transcript using markdown bullet points or numbers.
- If specific quotes are used, ensure they are properly formatted with quotation marks and attributed if the speaker is mentioned.
- For any statistical data or key figures mentioned, consider using bold text to make them stand out.
- Retain contractions and informal language to preserve the original tone of the speaker.
- Remove filler words (like "um", "uh", "you know") and false starts, but keep unique phrases or colloquialisms that add character to the speech.
- If there are clear asides or parenthetical statements in the speech, consider using parentheses or em dashes to set them apart in the text.
- Maintain the original order of ideas presented in the transcript, unless there's a clear benefit to minor reordering for coherence.
- Use markdown formatting for any emphasis (like italics or bold) where it seems the speaker placed vocal emphasis.
- If technical terms or acronyms are used, spell them out in full at first mention.
- Aim to keep as much of the original content as possible while making it readable as a written piece.

Here is the transcript:

<transcript>
{{transcript}}
</transcript>
""".strip()

# Our functions
# -----------------------------------------------------

def categorize_url(url: str) -> str:
	"""
	Determine the type of URL.
	"""
	if 'arxiv' in url:
		return 'arxiv'
	elif 'youtube' in url:
		return 'youtube'
	elif 'http' in url:
		return 'article'
	else:
		raise ValueError('Input must be a YouTube URL or an article URL.')

def retrieve_text(url: str, mode: str) -> str:
	"""
	This function takes a URL and returns the text.
	"""
	match mode:
		case 'youtube':
			with console.status("[bold green]Downloading YouTube transcript...", spinner="dots"):
				return download_transcript(url)
		case 'article':
			with console.status("[bold green]Downloading article...", spinner="dots"):
				return download_article(url)
		case 'arxiv':
			with console.status("[bold green]Downloading Arxiv article...", spinner="dots"):
				return download_arxiv(url)
		case _:
			raise ValueError('Not a recognized mode.')

def download_arxiv(url: str) -> str:
	"""
	This function takes an arXiv URL and returns the text.
	Might need to download PDF, convert to text, and then trim off References.
	"""
	print("Still need to implement arxiv function.")

def summarize(text: str, mode: str) -> str:
	"""
	This takes user input (i.e. the url) and either downloads the article or the Youtube transcript.
	"""
	match mode:
		case 'youtube':
			return summarize_youtube_transcript(text)
		case 'article':
			return summarize_article(text)
		case 'arxiv':
			return summarize_article(text)
		case _:
			raise ValueError('Not a recognized mode.')

def query_text(text: str, query: str) -> str:
	"""
	This function takes a text and a query and returns the response.
	"""
	with console.status("[bold green]Query...", spinner="dots"):
		model = Model('claude-3-5-sonnet-20240620')
		prompt_string = "Look at this text and answer the following question: <text>{{text}}</text> <query>{{query}}</query>"
		prompt = Prompt(prompt_string)
		chain = Chain(prompt, model)
		response = chain.run(input_variables={'text':text, 'query':query}, verbose = False)
		messagestore.add("assistant", response.content)
	return response.content

def summarize_youtube_transcript(transcript: str) -> str:
	"""
	This function takes a YouTube transcript and summarizes it.
	"""
	with console.status("[bold green]Summarizing YouTube transcript...", spinner="dots"):
		model = Model('claude-3-5-sonnet-20240620')
		prompt = Prompt(YouTube_prompt_string)
		chain = Chain(prompt, model)
		response = chain.run(input_variables={'transcript':transcript}, verbose = False)
	return response.content

def summarize_article(article: str) -> str:
	"""
	This function takes an article and summarizes it.
	"""
	with console.status("[bold green]Summarizing article...", spinner="dots"):
		model = Model('claude-3-5-sonnet-20240620')
		prompt = Prompt(Article_prompt_string)
		chain = Chain(prompt, model)
		response = chain.run(input_variables={'article':article}, verbose = False)
	return response.content

def format_transcript(transcript: str) -> str:
	"""
	This function takes a raw transcript and formats it.
	"""
	with console.status("[bold green]Query...", spinner="dots"):
		model = Model('claude-3-5-sonnet-20240620')
		prompt = Prompt(Format_transcript_prompt_string)
		chain = Chain(prompt, model)
		response = chain.run(input_variables={'transcript':transcript}, verbose = False)
		return response.content

def chain_of_density_summary(text: str) -> str:
	"""
	This function takes a text and returns a Chain of Density summary.
	"""
	with console.status("[bold green]Generating chain of density (CoD)...", spinner="dots"):
		cod_summary = chain_of_density(text)
	return cod_summary

def get_token_count(text: str) -> int:
	"""
	This function takes a text and returns the token count.
	"""
	pass

def print_markdown(markdown_string: str):
	"""
	Prints formatted markdown to the console.
	"""
	# Create a Markdown object
	border = "-" * 80
	markdown_string = f"{border}\n{markdown_string}\n\n{border}"
	md = Markdown(markdown_string)
	console.print(md)

if __name__ == '__main__':
	# Load our message store
	dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
	file_path = dir_path + messagestore_path
	messagestore = MessageStore(console = console, file_path = file_path)
	# Parse arguments
	parser = argparse.ArgumentParser(description='Summarize a URL.')
	parser.add_argument('url', type=str, nargs="?", help='URL to grab.')
	parser.add_argument('-s', '--summarize', action='store_true', help='Summarize the content.')
	parser.add_argument('-t', '--tokencount', action='store_true', help='Get token count for content.')
	parser.add_argument('-save', '--save', action='store_true', help='Save to Obsidian.')
	parser.add_argument('-cod', '--chain_of_density', action="store_true", help='Create a Chain of Density microsummary.')
	parser.add_argument('-l', '--last', action="store_true", help='View last message.')
	parser.add_argument('-r', '--raw', action="store_true", help='View raw.')
	parser.add_argument('-f', '--format', action="store_true", help='Format transcript.')
	parser.add_argument('-c', '--clear', action="store_true", help='Clear message store.')
	parser.add_argument('-q', '--query', type=str, help='Query the text.')
	args = parser.parse_args()
	# Route arguments
	if args.clear:
		messagestore.clear()
		sys.exit()
	if args.last:
		last_message = messagestore.last()
		if args.raw:
			console.print(last_message.content)
		elif args.query:
			query = args.query
			response = query_text(last_message.content, query)
			if args.raw:
				console.print(response)
			else:
				print_markdown(response)
			sys.exit()
		else:
			print_markdown(last_message.content)
		sys.exit()
	if args.url:
		url = args.url
		mode = categorize_url(url)
		text = retrieve_text(url, mode)
		if mode == 'youtube' and args.format:
			formatted_text = format_transcript(text)
			if args.raw:
				console.print(formatted_text)
			else: 
				print_markdown(formatted_text)
			messagestore.add(url, formatted_text)
			sys.exit()
		if args.query:
			query = args.query
			response = query_text(text, query)
			if args.raw:
				console.print(response)
			else:
				print_markdown(response)
			sys.exit()
		if args.summarize:
			summary = summarize(text, mode)
			if args.chain_of_density:
				cod_summary = chain_of_density_summary(summary)
				if args.raw:
					console.print(cod_summary)
					sys.exit()
				else:
					print_markdown(cod_summary)
					sys.exit()
			if args.raw:
				console.print(summary)
				sys.exit()
			print_markdown(summary)
			messagestore.add("assistant", summary)
			sys.exit()
		else:
			console.print(text)
			messagestore.add(url, text)

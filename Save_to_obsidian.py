"""
Abstracting this function out as I use it in multiple scripts.
"""
import os
from Chain import Prompt, Model, Chain
import sys
import argparse

obsidian_path = os.environ.get('OBSIDIAN_PATH')
# switch this if on different comp

def obsidianize_title(title: str) -> str:
	"""Clean up title for Obsidian filename rules."""
	replacements = [
		('/', '-'), (':', '-'), ('?', ''), ('=', ''),
		('&', '-'), ('.', '-'), ("'", ''), ('"', ''),
		('(', ''), (')', ''), (',', ''), ('*', ''),
		('<', ''), ('>', ''), ('|', ''), ('\\', '-'),
		('[', ''), (']', ''), ('{', ''), ('}', ''),
		('+', '-'), ('!', ''), ('@', '-'), ('#', ''),
		('$', ''), ('%', ''), ('^', ''), ('`', ''),
		('~', ''), (';', ''), ('  ', ' ')  # Replace double spaces with single
	]
	for old, new in replacements:
		title = title.replace(old, new)
	return title.strip()  # Remove leading/trailing whitespace

def generate_title(text: str) -> str:
	"""
	LLM call to generate a title for the text.
	We'll use haiku.
	"""
	model = Model("claude-3-haiku-20240307")
	prompt_string = """Create a title for the following text:\n<text>{{text}}</text>"""
	prompt = Prompt(prompt_string)
	chain = Chain(prompt, model)
	response = chain.run(text)
	return response.content

def get_title(text: str) -> str:
	"""
	This function will generate a title for a given text.
	Either it captures an l1 header or it calls generate_title.
	"""
	head = text.split('\n')[:5]
	for h in head:
		if h.startswith('# '):
			text = text.replace(h, '')
			text = text.strip()
			return text, h[2:]
	else:
		return text, generate_title(text)

def save_to_obsidian(text: str, title: str = "", url: str = "", folder = "extracted_articles") -> str:
	"""
	Takes a title, text, and optional URL and saves it to a file in the Obsidian vault.
	"""
	if not title:
		text, title = get_title(text)
	title = obsidianize_title(title)
	path = obsidian_path + folder
	filename = f'{path}/{title}.md'
	# If there is a URL, add it to the top of the file
	if url:
		text = f'{url}\n\n{text}'
	with open(filename, 'w') as f:
		f.write(text)
	return filename

if __name__ == "__main__":
	# Capture arguments
	parser = argparse.ArgumentParser(description="Save text to Obsidian.")
	parser.add_argument("text", type=str, nargs="?", help="Text to be saved.")
	parser.add_argument("-t", "--title", type=str, help="Title to be used.")
	parser.add_argument("-f", "--folder", type=str, help="Folder to save to (default is extracted_articles).")
	parser.add_argument("-p", "--print", action="store_true", help="Print the output.")
	args = parser.parse_args()
	if args.text:
		text = args.text
	# elif stdin is detected
	elif not sys.stdin.isatty():
		text = sys.stdin.read()
	else:
		print("No text provided; either pipe into script or provide as argument.")
		sys.exit()
	title = args.title if args.title else ""
	folder = args.folder if args.folder else "extracted_articles"
	# Save to Obsidian
	filename = save_to_obsidian(text, title=title, folder=folder)
	print(f"Text saved to {filename}.")
	if args.print:
		print(text)

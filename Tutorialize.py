#!/usr/bin/env python3

# Imports can take a while, so we'll give the user a spinner.
# -----------------------------------------------------------------

from rich.console import Console

console = Console(width=100)  # for spinner

with console.status("[bold green]Loading...", spinner="dots"):
	from Chain import Chain, Model, Prompt
	from obsidian import print_markdown
	from Save_to_obsidian import save_to_obsidian
	import sys
	from time import sleep
	import argparse
	from rich.console import Console
	from rich.markdown import Markdown
	import pickle
	import os

# Constants
dir_path = os.path.dirname(os.path.realpath(__file__))
tutorial_store_file = os.path.join(dir_path, ".tutorial_store.pkl")
obsidian_path = os.environ.get("OBSIDIAN_PATH")
preferred_folder = "Tutorials"
preferred_model = "claude"

generic_persona = """
# Generic Tutorial System Prompt

You are a knowledgeable and experienced educator with expertise across various fields. Your role is to create informative and engaging tutorials on a wide range of topics.

When presented with a topic, your task is to generate a comprehensive tutorial that helps readers understand the fundamentals of that topic. Your tutorials should be accessible to beginners while also providing value to those with some prior knowledge.

PLEASE GENERATE A TUTORIAL OF APPROXIMATELY 1,050 WORDS, STRUCTURED AS FOLLOWS:

1. Introduction (100 words)
   - Provide a brief overview of the topic
   - Explain its importance or relevance
   - Outline what the reader will learn from this tutorial

2. Core Concepts (250 words)
   - Explain 3-5 fundamental concepts related to the topic
   - Provide clear, concise definitions
   - Illustrate how these concepts relate to each other

3. Practical Application (400 words)
   - Offer 2-3 practical examples, scenarios, or case studies
   - If applicable, include step-by-step instructions or demonstrations
   - Explain the purpose and outcome of each example

4. Best Practices and Common Pitfalls (150 words)
   - List 3-5 best practices related to the topic
   - Highlight 2-3 common mistakes or misconceptions to avoid

5. Advanced Topics and Further Learning (100 words)
   - Briefly introduce 2-3 advanced concepts or related topics
   - Suggest resources or avenues for further learning

6. Conclusion (50 words)
   - Summarize the key takeaways
   - Encourage practical application of the learned concepts

Throughout the tutorial:
- Use Markdown (obsidian-flavored) for formatting where appropriate
- Employ clear, concise language suitable for a general audience
- Focus on practical knowledge and real-world applications
- Emphasize understanding the "why" behind concepts, not just the "how"
- Mention relevant tools, methodologies, or frameworks without excessive detail
- Include occasional notes on how the topic relates to broader fields or concepts

Adapt your language and examples to suit the specific topic while maintaining this general structure and approach. If the topic is technical, include relevant technical details or code snippets. If it's theoretical, use appropriate analogies or thought experiments.

Remember to tailor the content to the specific [TOPIC] provided, ensuring that the tutorial is informative, engaging, and valuable to the reader.
""".strip()

persona_metaprompt = """
# Subject-Specific Tutorial Metaprompt

You are an expert prompt engineer. Your task is to create a system prompt for an AI language model that will generate high-quality, medium-length tutorials (~1,500 words) on various topics within a given subject area. The system prompt you create should be tailored to the specific {{subject}} provided, while maintaining a consistent structure and approach to tutorial creation.

## Instructions for Generating the System Prompt

1. Begin by creating a persona for the AI instructor. This persona should be an experienced professional in the {{subject}} field. For example:
   - If {{subject}} is Marketing: "You are an experienced Marketing instructor with extensive experience leading marketing strategies in large enterprises..."
   - If {{subject}} is Python Programming: "You are a seasoned Python developer and instructor with years of experience in software engineering and teaching programming concepts..."

2. Describe the instructor's specialization and target audience. This should be relevant to the {{subject}} and the level of expertise expected from the readers.

3. Explain that the AI will be given topics within the {{subject}} area and asked to generate tutorials to help readers understand the basics of those topics.

4. Specify that the tutorial should be approximately 1,050 words long.

5. Outline the structure of the tutorial, maintaining the following sections but adapting the content description to fit the {{subject}}:

   a. Introduction (100 words)
   b. Core Concepts (250 words)
   c. Practical Application (400 words)
   d. Best Practices and Common Pitfalls (150 words)
   e. Advanced Topics and Further Learning (100 words)
   f. Conclusion (50 words)

6. For each section, provide guidance on what should be included, tailoring the instructions to the {{subject}}. For example:
   - In the Practical Application section for a technical {{subject}}, mention including code examples or command-line instructions.
   - For a theoretical or strategic {{subject}}, suggest including case studies or hypothetical scenarios.

7. Provide instructions on the overall approach to creating the tutorial, including:
   - Using clear, concise language suitable for the target audience
   - Focusing on practical knowledge and real-world applications
   - Emphasizing understanding the "why" behind concepts, not just the "how"
   - Mentioning relevant tools, methodologies, or frameworks without going into exhaustive detail
   - Including notes on how the topic relates to broader concepts within the {{subject}}

8. Specify the use of Markdown (obsidian-flavored) for formatting where appropriate.

9. Instruct the AI to tailor the content to the specific topic while maintaining the general structure and approach outlined in the prompt.

10. Include any subject-specific considerations that are important for creating effective tutorials in the {{subject}} area. This might include:
    - Specific types of examples or exercises that are particularly effective for learning in this field
    - Important ethical considerations or professional standards relevant to the {{subject}}
    - Key resources or authoritative sources that should be referenced or recommended

Remember to adapt the language and focus of the prompt to align with the norms and expectations of the {{subject}} field, while retaining the overall structure and approach to tutorial creation.

## Example: Linux System Administration Prompt

Here's an example of how this metaprompt can be applied to create a system prompt for Linux system administration tutorials:

```markdown
You are an experienced IT instructor with a great deal of experience with Linux system administration.
You specialize in teaching networking and security concepts to amateurs who want to do cool things with Linux on their home networks.

People will come to you with a topic, and you'll be asked to generate a tutorial that will help them understand the basics of that topic.

THE TUTORIAL SHOULD BE AROUND 1,300 WORDS LONG, AND SHOULD BE ROUGHLY STRUCTURED AS FOLLOWS:

1. Introduction (100 words)
   - Brief overview of the topic
   - Importance in Linux administration and networking
   - What the reader will learn

2. Core Concepts (250 words)
   - Explain 3-5 fundamental concepts related to the topic
   - Provide clear, concise definitions
   - Highlight how these concepts relate to each other

3. Practical Application (400 words)
   - Provide 2-3 hands-on examples or scenarios
   - Include command-line examples where appropriate, but focus on the overall process rather than explaining every command in detail
   - Explain the purpose and outcome of each step

4. Best Practices and Common Pitfalls (150 words)
   - List 3-5 best practices related to the topic
   - Mention 2-3 common mistakes or misconceptions to avoid

5. Advanced Topics and Further Learning (100 words)

6. Conclusion (50 words)
   - Summarize key takeaways
   - Encourage practical application of the learned concepts

Throughout the tutorial:
- Use Markdown (obsidian-flavored) for formatting where it makes sense
- Use clear, concise language suitable for beginners
- Focus on practical knowledge and real-world applications
- Emphasize understanding the "why" behind actions, not just the "how"
- Mention relevant tools or utilities without going into exhaustive detail
- Include occasional notes on how the topic relates to broader system administration or networking concepts

Remember to tailor the content to the specific [TOPIC] while maintaining this general structure and approach.
```

FOLLOW THESE TWO RULES:
ONLY RETURN THE SYSTEM PROMPT, NOT ANY EXTRA SENTENCES OR COMMENTS.
INCLUDE NO MARKDOWN OR CODE BLOCKS IN THE RESPONSE.
""".strip()

tutorial_prompt = """
Someone has come to you with this topic:
==========
{{topic}}
==========

Please generate a tutorial on the topic.
""".strip()

complete_tutorial_prompt = """
You are an expert curriculum developer who is able to take unfinished tutorials and finish them.

You've been given the first half of a tutorial. Your task is to write the second half, with these guidelines in mind:
- the information you provide should be as accurate as you can make it, and should be relevant to the topic at hand.
- the second half should be in the spirit of the first half, and achieve any remaining learning objectives set out in the first half that were not yet addressed.
- use the same style of markdown formatting that you see in the first half.
- Return ONLY the part that you wrote, not the entire tutorial, and provide NO other comments or sentences.
- The entire work (first half + your half) should have the general structure as set below:

<tutorial_structure>
1. Introduction
2. Core Concepts
3. Practical Application (400 words)
4. Best Practices and Common Pitfalls
5. Advanced Topics and Further Learning
6. Conclusion
</tutorial_structure>

Here's the first half:

<first_half_of_tutorial>
{{tutorial}}
</first_half_of_tutorial>

Please complete the tutorial. Return ONLY the part that you wrote, not the entire tutorial, and provide NO other comments or sentences.
""".strip()

# Persistence functions


def initialize_tutorial_store():
	"""
	Initialize the message store with an empty list. Run this manually, this is not invoked in the script.
	"""
	tutorial_store = []
	save_to_tutorial_store(tutorial_store)


def load_tutorial_store() -> list[str]:
	"""
	Load the message store from a pickle file.
	"""
	if not os.path.exists(tutorial_store_file):
		initialize_tutorial_store()
	with open(tutorial_store_file, "rb") as f:
		tutorial_store = pickle.load(f)
	return tutorial_store


def save_to_tutorial_store(obj):
	"""
	Save an object to a pickle file.
	"""
	with open(tutorial_store_file, "wb") as f:
		pickle.dump(obj, f)


# Functions
def create_tutor(subject: str) -> str:
	"""
	Create a tutor persona for a given subject.
	"""
	prompt = Prompt(persona_metaprompt)
	model = Model(preferred_model)
	chain = Chain(prompt, model)
	response = chain.run(input_variables={"subject": subject})
	return response.content


def Tutorialize(topic: str | list[str], subject: str = "") -> str | list[str]:
	"""
	Our main function.
	If a subject is provided, we create a tutor persona for that subject.
	If only a single topic is provided (as str) we use the sync function process_topic.
	If a list of topics is provided, we use the async function Tutorialize_Async.
	"""
	if subject:
		print("Creating tutor persona...")
		persona = create_tutor(subject)
	else:
		persona = generic_persona
	if isinstance(topic, str):
		return Tutorialize_Sync(topic, persona)
	elif isinstance(topic, list):
		return Tutorialize_Async(topic, persona)


def Tutorialize_Sync(topic: str, persona: str, save_to_file=True) -> str:
	"""
	Process a topic into a tutorial using the persona template.
	"""
	messages = Chain.create_messages(system_prompt=persona)
	model = Model(preferred_model)
	prompt = Prompt(tutorial_prompt)
	chain = Chain(prompt, model)
	response = chain.run(messages=messages, input_variables={"topic": topic})
	tutorial = response.content
	return tutorial


def Tutorialize_Async(topics: list[str], persona: str, save_to_file=True) -> list[str]:
	"""
	Generate tutorials for a list of topics asynchronously.
	NOTE: THIS IS BROKEN BECAUSE OF SAVE TO OBSIDIAN
	"""
	messages = Chain.create_messages(system_prompt=persona)
	model = Model(preferred_model)
	prompt = Prompt(tutorial_prompt)
	# construct list of prompts
	prompts = []
	for topic in topics:
		prompt_obj = prompt.render(input_variables={"topic": topic})
		message_obj = messages + [{"role": "user", "content": prompt_obj}]
		prompts.append((topic, message_obj))
	# run async
	results = []
	async_results = model.run_async(prompts=[p[1] for p in prompts], model="claude")
	for (topic, _), result in zip(prompts, async_results):
		if save_to_file:
			filename = save_to_obsidian(text=tutorial, title=topic, folder="tutorials")
			print(f"Saved to {obsidian_path + filename}.")
		results.append(filename)
	return results


def Complete_Tutorial(tutorial: str) -> str:
	"""
	Complete a tutorial with a conclusion.
	Experimental feature, intending to get around context window limitations.
	"""
	print("Completing tutorial...")
	prompt = Prompt(complete_tutorial_prompt)
	model = Model(preferred_model)
	chain = Chain(prompt, model)
	response = chain.run(input_variables={"tutorial": tutorial})
	return response.content


if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser(description="Process some topics.")
	parser.add_argument(
		"-s", "--subject", type=str, help="The subject to create a tutor persona for"
	)
	parser.add_argument(
		"-t", "--terminal", action="store_true", help="Flag to indicate terminal mode"
	)
	parser.add_argument(
		"-r", "--raw", action="store_true", help="Flag to indicate raw output"
	)
	parser.add_argument(
		"-l", "--last", action="store_true", help="Flag to print the last tutorial"
	)
	parser.add_argument("topic", nargs="?", help="The topic to process")
	parser.add_argument(
		"-save", "--save", action="store_true", help="Save to obsidian."
	)
	parser.add_argument(
		"-o", "--ollama", action="store_true", help="Use local LLM instead."
	)
	args = parser.parse_args()
	topic = args.topic
	subject = args.subject
	terminal = args.terminal
	raw = args.raw
	last = args.last
	if args.ollama:
		preferred_model = "llama3.1:latest"
	if last and not raw:  # Print it again.
		tutorial = load_tutorial_store()[-1]
		print_markdown(tutorial)
		if args.save:
			save_to_obsidian(tutorial, folder=preferred_folder)
		sys.exit(0)
	elif last and raw:  # Print the last tutorial in raw format, useful for clipping
		tutorial = load_tutorial_store()[-1]
		print(tutorial)
		if args.save:
			save_to_obsidian(tutorial, folder=preferred_folder)
		sys.exit(0)
	with console.status("[bold green]Query...", spinner="dots"):
		tutorial = Tutorialize(topic, subject)
		print_markdown(tutorial)
		tutorial_store = load_tutorial_store()
		tutorial_store.append(tutorial)
		save_to_tutorial_store(tutorial_store)
		if args.save:
			save_to_obsidian(tutorial, folder=preferred_folder)

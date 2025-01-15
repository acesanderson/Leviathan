"""
TODO: train a model with unsloth OR at least give a few-shot corpus to LLM.
"""

from rich.console import Console

console = Console(width=100)  # for spinner

with console.status("[green]Loading...", spinner="dots"):
    from Chain import Chain, Model, Prompt, MessageStore, create_system_message
    from Leviathan.utilities.print_markdown import print_markdown
    import argparse
    from pathlib import Path
    import sys

# Constants
preferred_model = "deepseek"

# Message Store for history and logging
dir_path = Path(__file__).parent
history_file = dir_path / ".cookbook_history.pkl"
log_file = dir_path / ".cookbook_log.txt"
messagestore = MessageStore(
    console=console, history_file=history_file, log_file=log_file
)
Chain._message_store = messagestore


cookbook_prompt_string = """
Write a recipe in the style of the O'Reilly Media Cookbooks series on this topic:

<topic>
{{topic}}
</topic>

Only return the recipe, no other text or commentary.
""".strip()


def compose_recipe(topic: str, preferred_model: str = "claude"):
    """
    Takes an input and generates a recipe from it.
    Returns string or BaseModel.
    """
    prompt = Prompt(cookbook_prompt_string)
    model = Model(preferred_model)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(input_variables={"topic": topic})
    return response.content


def main():
    messagestore.load()
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", help="The topic to generate a recipe for.")
    parser.add_argument(
        "--model", help="The model to use for generation.", default="claude"
    )
    parser.add_argument(
        "-r", "--raw", action="store_true", help="Flag to indicate raw output"
    )
    parser.add_argument(
        "-l", "--last", action="store_true", help="Flag to print the last tutorial"
    )
    args = parser.parse_args()
    if args.model:
        preferred_model = args.model
    if args.last and not args.raw:  # Print the last tutorial in markdown format
        tutorial = messagestore.last().content
        print_markdown(string_to_display=tutorial, console=console)
        sys.exit(0)
    elif (
        args.last and args.raw
    ):  # Print the last tutorial in raw format, useful for clipping
        tutorial = messagestore.last().content
        print(tutorial)
        sys.exit(0)
    if not args.topic:
        print("Please provide a topic.")
        sys.exit(1)
    if args.topic:
        with console.status("[green]Query...", spinner="dots"):
            recipe = compose_recipe(args.topic, preferred_model)
            print_markdown(string_to_display=recipe, console=console)
            messagestore.add_new("assistant", recipe)


if __name__ == "__main__":
    main()

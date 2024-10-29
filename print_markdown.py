from rich.console import Console
from rich.markdown import Markdown


def print_markdown(string_to_display: str, console: Console | None = None):
    """
    Prints formatted markdown to the console.
    """
    if not Console:
        console = Console(width=80)
    # Create a Markdown object
    border = "-" * 80
    markdown_string = f"{border}\n{string_to_display}\n\n{border}"
    md = Markdown(markdown_string)
    console.print(md)

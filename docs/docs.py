"""
Command line script that can generate docstrings for a python project, at these different levels of code:
- the entire project (i.e. the README.md file in the project root))
- a single module (i.e. the __init__.py file in a module directory)
- a single script (i.e. a .py file within the project)
- a single class (i.e. a class in a .py file)
- a single function (i.e. a function in a .py file)

One required input:
- a path to the python script in question (script should autodetect project root as well, as that is essential llm context for generating docstrings)

Optional input:
- --line-number: the line number of the class or function to generate a docstring for (if 0 or 1, it will generate a docstring for the entire file/module)

Use cases:
- project root: generates a README.md file with a project description, installation instructions, usage examples, etc. If the given path is a project root, it will generate README.md; if the path is README.md, it will fill in the relevant text. (second case is the neovim case)
- module: pass the path to the __init__.py file in a module directory, it will generate a docstring for the module and insert it into the file.
- script: pass the path to a .py file, it will generate a docstring for the script and insert it into the file. If line number is 0 or 1, it will do the same.
- class: pass the path to a .py file and the line number of the class, it will generate a docstring for the class and insert it into the file.
- function: pass the path to a .py file and the line number of the function, it will generate a docstring for the function and insert it into the file.

NOTE: the corresponding neovim command is `:Docstring` and it will prompt for the same arguments as this script. It is in commands.lua.
"""

from Chain import Chain, Model, Prompt
from Chain.prompt.prompt_loader import PromptLoader
from pathlib import Path

prompt_dir = Path(__file__).parent / "prompts"
prompt_loader = PromptLoader(
    prompt_dir,
    keys=["project", "module", "script", "class", "function"],
)

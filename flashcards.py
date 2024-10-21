from Chain import Chain, Model, Prompt, Parser
from pydantic import BaseModel
import pandas as pd

# Pydantic classes
class Flashcard(BaseModel):
	front: str
	back: str


bash_terms = (
	"""
enable alias
enable bg
enable bind
enable break
enable builtin
enable caller
enable cd
enable command
enable compgen
enable complete
enable compopt
enable continue
enable declare
enable dirs
enable disown
enable echo
enable enable
enable eval
enable exec
enable exit
enable export
enable false
enable fc
enable fg
enable getopts
enable hash
enable help
enable history
enable jobs
enable kill
enable let
enable local
enable logout
enable mapfile
enable popd
enable printf
enable pushd
enable pwd
enable read
enable readarray
enable readonly
enable return
enable set
enable shift
enable shopt
enable source
enable suspend
enable test
enable times
enable trap
enable true
enable type
enable typeset
enable ulimit
enable umask
enable unalias
enable unset
enable wait
""".strip()
	.replace("enable ", "")
	.split("\n")
)

persona = """
You are a talent instructional designer who is talented as making flashcards from a knowledge base.
These flashcards are used to help students learn the material, and are loaded in a spaced repetition system like Anki.

You are helping a client learn how to use Bash commands in Linux. They have provided you with a list of commands they want to learn, and have asked you to create flashcards for each command.

For learning Bash commands in Linux, the back of each flashcard should contain concise yet comprehensive information to optimize learning and retention.

Include:
- Command syntax: The basic structure of how the command is used.
- Brief description: A one-sentence explanation of what the command does.
- Common options/flags: List 2-3 of the most frequently used options with brief explanations.
- Example usage: A practical example of how the command is typically used.
- Related commands: Mention 1-2 related commands that are often used in conjunction or serve similar purposes.
- Mnemonic (if applicable): A memory aid to help recall the command's function.
- Caution (if necessary): Any important warnings or potential pitfalls to be aware of.

Here are three example flashcards for grep, sed, and find:

<example_flashcard1>
# grep

## Syntax
```
grep [options] pattern [file...]
```

## Description
Searches for patterns in text and prints matching lines.

## Common options
- `-i`: Ignore case
- `-r`: Recursive search
- `-v`: Invert match (show non-matching lines)

## Example
```bash
grep -i "error" /var/log/syslog
```
Searches for "error" (case-insensitive) in the syslog file.

## Related commands
- `awk`: For more complex text processing
- `sed`: For search and replace operations

## Mnemonic
"Grab Regular Expressions and Print"

## Caution
Be mindful of using grep with large files or recursive searches, as it can be resource-intensive.
</example_flashcard1>
<example_flashcard2>
# sed

## Syntax
```
sed [options] 'command' [file...]
```

## Description
Stream editor for filtering and transforming text.

## Common options
- `-i`: Edit files in-place
- `-e`: Add multiple commands
- `-n`: Suppress automatic printing of pattern space

## Example
```bash
sed 's/old/new/g' file.txt
```
Replaces all occurrences of 'old' with 'new' in file.txt.

## Related commands
- `awk`: For more advanced text processing
- `tr`: For simple character translations

## Mnemonic
"Stream EDitor"

## Caution
Be careful with in-place editing (-i option) as it modifies the original file without creating a backup by default.
</example_flashcard2>
<example_flashcard3>
# find

## Syntax
```
find [path...] [expression]
```

## Description
Searches for files and directories in a directory hierarchy.

## Common options
- `-name`: Search by file name
- `-type`: Search by file type (f for regular files, d for directories)
- `-mtime`: Search by modification time

## Example
```bash
find /home/user -name "*.txt" -mtime -7
```
Finds all .txt files in /home/user modified in the last 7 days.

## Related commands
- `locate`: For quick file name searches using a database
- `grep`: Often used with find for searching file contents

## Mnemonic
"FINDing files is what I Do"

## Caution
Without proper constraints, find can be slow on large directory structures. Use options like -maxdepth to limit the search depth if necessary.
</example_flashcard3>
"""

flashcard_prompt = """
Please return the front and back of the flashcard for each term in the list below:

<bash_terms>
{{bash_term}}
</bash_term>
""".strip()

# Create our chains
def flashcarderize(term: str) -> Flashcard:
	"""
	Takes a term, runs it through our chain and returns a Flashcard object.
	"""
	# Set system prompt
	messages = Chain.create_messages(system_prompt=persona)
	# Set prompt
	prompt = Prompt(flashcard_prompt)
	# set model
	model = Model("claude")
	# create parser
	parser = Parser(Flashcard)
	# Define chain
	chain = Chain(prompt, model, parser)
	# Run chain
	response = chain.run(input_variables={"bash_term": term}, messages=messages)
	return response.content


# if __name__ == "__main__":
flashcards = []
for index, term in enumerate(bash_terms):
	try:
		print(f"Flashcarding number {index+1} of {len(bash_terms)}: {term}")
		flashcard = flashcarderize(term)
		flashcards.append(flashcard)
	except:
		print("Failed to flashcard ", term)

# tuple it up
flashcard_tuples = []
for flashcard in flashcards:
	flashcard_tuples.append((flashcard.front, flashcard.back))

# Create a dataframe
df = pd.DataFrame(flashcard_tuples, columns=["front", "back"])

# save to csv
df.to_csv("~/Brian_Code/Leviathan/bash_flashcards.csv", index=False)

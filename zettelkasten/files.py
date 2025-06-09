from pathlib import Path

downloads_folder = Path("/Users/bianders/Downloads/")

files = downloads_folder.glob("*.*")
files = list(files)

extensions = {file.suffix for file in files}
for e in extensions:
    print(e)

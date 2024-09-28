## Purpose of this project
"Book" is how I process digital versions of books for NLP purposes.
This can include:
- summarization
- query-based summarization
- knowledge graph generation
- vector database creation for RAG purposes

## Infrastructur
This is inspired by the Course and Get scripts, which use pydantic dataclasses and a MongoDB database to create a flexible dataset.
We'll also be programmatically generated vector databases.

## Immediate practical usage
Create a Book object from the NLTK book:
- convert to markdown
- break into chapters
- chunk + vectorize
- create a query function
- feed query function into LLM for RAG


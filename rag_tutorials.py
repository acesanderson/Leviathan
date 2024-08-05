from Tutorialize import Tutorialize

subject = "Retrieval-augmented generation for LLM applications"

topics = """
implementing hybrid search combining dense and sparse retrieval for better results
using a reranker to improve the quality of retrieved information
prompt engineering: including instructions for the LLM on how to use the retrieved information
prompt engineering: experimenting with different prompt structures
relevance filtering: implementing a relevance threshhold to only include truly pertinent information
relevance filtering: using a smaller, faster model to judge relevance before passing to the main LLM
evaluation and monitoring: implementing evaluation metrics like relevance, coherence, and factual accuracy
fine-tuning a local LLM on your data
""".strip().split("\n")

tut = Tutorialize(topic = topics, subject = subject)


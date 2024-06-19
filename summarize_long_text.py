"""
This is the much more complicated summarization process we use for books and other megalong text formats.

Eventually we will incorporate this back into text_summarization (or better yet, combine as a package with the different wrapper functions in separate scripts).
"""

from Chain import Chain, Model, Prompt, Parser                                  # type: ignore
from text_summarization import chunk_text_by_words, map_chain, reduce_chain, generate_test_texts

def summarize_long_text(text:str) -> str:
	"""
	Summarizes a long text using embeddings.
	Creating this in another file.
	"""
	text_chunks = chunk_text_by_words(text)
	# db = get_embeddings(text_chunks)
	# clusters = cluster_embeddings(db)
	# exemplar_clusters = pick_best_embeddings(clusters)
	# summary_map = map_chain(exemplar_clusters)
	# final_summary = reduce_chain(summary_map)
	# if final_summary == None:
	# 	print("No long summary generated.")
	# return final_summary.content

def main():
	short, medium, long = generate_test_texts
	summary = summarize_long_text()
	print(summary)

if __name__ = "__main__":
    main()

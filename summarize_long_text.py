"""
This is the much more complicated summarization process we use for books and other megalong text formats.

Eventually we will incorporate this back into text_summarization (or better yet, combine as a package with the different wrapper functions in separate scripts).
"""

from Chain import Chain, Model, Prompt, Parser                                  # type: ignore
from text_summarization import chunk_text_by_words, map_chain, reduce_chain, generate_test_texts, summarize_medium_text, config_dict, generate_test_book
import chromadb
from sklearn.cluster import KMeans

def get_embeddings(text_chunks: list[str]) -> chromadb.Collection:
	"""
	Generates embeddings for each chunk of text.
	"""
	db = chromadb.Client()
	collection = db.create_collection(name = "text_chunk_embeddings")
	collection.add(
		documents = text_chunks,
		ids = [str(i) for i in range(len(text_chunks))],
	)
	return collection

def cluster_embeddings(collection: chromadb.Collection) -> list[chromadb.Embeddings]:
	"""
	TO DO
	Takes a set of embeddings, and applies a clustering analysis to them, returning a list of clusters.
	"""
	embeddings = collection.get()['embeddings'] # I think
	kmeans = KMeans(n_clusters=config_dict['num_clusters'], random_state=42).fit(embeddings)	# do I programmatically identify the ideal number of clusters?
	clusters: list[chromadb.Embeddings] = []
	# return clusters

def pick_representative_documents(clusters: list[chromadb.Embeddings]) -> list[str]:
	"""
	TO DO
	Takes a set of embeddings, performs a special algorithm (TBD) to return exemplar docs for map/reduce summarization.
	"""
	exemplars: list[str] = []
	return exemplars

def summarize_long_text(text:str) -> str:
	"""
	Summarizes a long text using embeddings.
	Creating this in another file.
	"""
	text_chunks = chunk_text_by_words(text)
	collection = get_embeddings(text_chunks)
	clusters = cluster_embeddings(collection)
	representative_documents = pick_representative_documents(clusters)
	# Now we have a medium text to summarize with map/reduce
	summary = summarize_medium_text(representative_documents)
	if summary == None:
		print("No long summary generated.")
	return summary.content

# def main():
# 	short, medium, long = generate_test_texts
# 	summary = summarize_long_text()
# 	print(summary)

# if __name__ == "__main__":
#     main()

text = generate_test_texts()[2]
text_chunks = chunk_text_by_words(text)

db = chromadb.Client()
collection = db.create_collection(name = "text_chunk_embeddings")
collection.add(
	documents = text_chunks,
	ids = [str(i) for i in range(len(text_chunks))],
)

embeddings = collection.get()['embeddings'] # I think
kmeans = KMeans(n_clusters=config_dict['num_clusters'], random_state=42).fit(embeddings)	# do I programmatically identify the ideal number of clusters?

clusters: list[chromadb.Embeddings] = []
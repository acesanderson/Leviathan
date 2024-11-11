"""
This script takes a text, chunks it, and generates embeddings, returning a chromadb.Collection.
"""

import chromadb
from Medium_summarize import chunk_text_by_words
from reranking import rerank_options
import argparse

# our configs
chunk_size = 50
overlap = 5

def vectorize(text) -> chromadb.Collection:
    """
    Vectorizes a text and returns a chromadb.Collection.
    """
    chunks = chunk_text_by_words(text)
    ids_and_docs = list(enumerate(chunks))
    ids = [str(i[0]) for i in ids_and_docs]
    docs = [i[1] for i in ids_and_docs]
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="ephemeral")
    collection.add(
        documents=docs,
        ids=ids,
    )
    print(f"Generated {len(docs)} embeddings.")
    return collection

def query(collection: chromadb.Collection, query_string: str, n_results: int) -> list[str]:
    """
    Queries a collection for a list of query texts and returns the top n results.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    ids = results['ids'][0]
    documents = results['documents'][0]
    # Fancy little swap since my imported code expects the ids first.
    # This will likely cause bugs so highlighting this here.
    ids, documents = documents, ids
    return list(zip(ids, documents))

def contextualize_chunk(chunk: str, text: str) -> str:
    """
    Contextualizes a chunk by adding the surrounding text.
    """
    pass

def rerank(options: list[tuple], query: str, k: int = 5) -> list[tuple]:
    """
    Reranks a list of options based on a query.
    This wraps the imported rerank_options function.
    """
    return rerank_options(options, query, k)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs='?', help="A query for the text.")
    args = parser.parse_args()
    if not args.query:
        query_text = "Pseudocode for NLP text summarization that can be used in a production environment."
    else:
        query_text = args.query
    with open("examples/arxiv_paper.txt", 'r') as f:
        text = f.read()
    collection = vectorize(text)
    results = query(collection, query_text, 30)
    # print(results)
    reranked_results = rerank(results, query_text, 5)
    for reranked_result in reranked_results:
        print('\n')
        print(reranked_result)
        print('\n')


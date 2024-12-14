"""
This is the much more complicated summarization process we use for books and other megalong text formats.

Next up: create a Book class that can handle this process, and becomes the main class for interacting with a book for summarization and RAG.
(i.e. endgame = chat)
"""

from Leviathan.summarize.summarize_medium_text import (
    chunk_text_by_words,
    map_chain,
    reduce_chain,
)
import chromadb
from sklearn.cluster import KMeans
import numpy as np
import argparse
import subprocess

# Customizable settings
num_clusters = 11
test_book = "examples/NLTK.txt"


# Our functions
def generate_test_book():
    """
    Generate a test book.
    """
    with open(test_book, "r") as f:
        book = f.read()
    return book


def load_book(book_file: str) -> str:
    """
    Load a book from a file.
    """
    # If extension is epub run convert_epub_to_markdown
    if book_file.endswith(".epub"):
        return convert_epub_to_markdown(book_file)
    else:
        with open(book_file, "r") as f:
            book = f.read()
    return book


def convert_epub_to_markdown(epub_file: str) -> str:
    """
    Convert an epub file to markdown, using pandoc.
    """
    # Run this command in the terminal and grab stdout: `pandoc Learning_and_Development_Handbook.epub -t markdown`
    command = ["pandoc", epub_file, "-t", "markdown"]
    # Run the pandoc command and capture the output
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    # Return the captured stdout
    return result.stdout


def get_embeddings(text_chunks: list[str]) -> list:
    """
    Generates embeddings for each chunk of text.
    """
    db = chromadb.Client()
    collection = db.create_collection(name="text_chunk_embeddings")
    collection.add(
        documents=text_chunks,
        ids=[str(i) for i in range(len(text_chunks))],
    )
    embeddings = collection.get(include=["embeddings", "documents"])
    # zip them together
    embeddings = list(zip(embeddings["documents"], embeddings["embeddings"]))
    return embeddings


def find_cluster_representatives(embeddings, num_clusters=num_clusters):
    """
    Take a list of embeddings ([[document,embedding]]), cluster them, identify the cluster centers, and return the closest document to each center.
    """
    # Extract documents and their corresponding embeddings
    documents = [item[0] for item in embeddings]
    vectors = np.array([item[1] for item in embeddings])
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(vectors)
    # Find the closest documents to each cluster center
    cluster_representatives = []
    for center in kmeans.cluster_centers_:
        # Calculate distances from all embeddings to this center
        distances = np.linalg.norm(vectors - center, axis=1)
        # Get the index of the closest embedding
        closest_index = np.argmin(distances)
        # Append the corresponding document to the representatives list
        cluster_representatives.append(documents[closest_index])
    return cluster_representatives


def summarize_long_text(text: str) -> str:
    """
    Wrapper function.
    Summarizes a long text using embeddings.
    Creating this in another file.
    """
    text_chunks = chunk_text_by_words(text)
    embeddings = get_embeddings(text_chunks)
    print("Generated embeddings.")
    representative_documents = find_cluster_representatives(embeddings)
    print("Found representative documents.")
    # Now we have a medium text to summarize with map/reduce
    summary_map = map_chain(representative_documents)
    print("Mapped representative documents.")
    summary = reduce_chain(summary_map)
    print("Reduced representative documents.")
    if summary == None:
        print("No long summary generated.")
    return summary.content


def main():
    text = generate_test_book()
    summary = summarize_long_text(text)
    print(summary)


if __name__ == "__main__":
    # create argparse
    parser = argparse.ArgumentParser(description="Summarize a long text.")
    parser.add_argument(
        "book_file", type=str, help="The book file (md or .txt format) to summarize."
    )
    args = parser.parse_args()
    book_file = args.book_file
    if not book_file:
        main()
        exit()
    else:
        text = load_book(book_file)
        summary = summarize_long_text(text)
        print(summary)

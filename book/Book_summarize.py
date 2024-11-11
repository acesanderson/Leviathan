"""
Similar to Long_summarize, however the text is split into original chapters which are treated as the clusters.
Much simpler, therefore, with no need for embeddings/clustering.
This takes a Book object, and for each chapter:
- chunks the chapter
- summarizes each chunk
- concatenates the summaries
- summarizes the concatenated summaries (this is a chapter summary)
- summaries the chapter summary (this is a book summary)
"""
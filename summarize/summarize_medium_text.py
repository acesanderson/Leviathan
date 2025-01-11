"""
This handles default summarization for texts of size 1500 < x < 10000
"""

from Chain import Model, Prompt, Chain, Parser
from Leviathan.summarize.answer_list import Answer_List

# Our configs (we can tweak these for performance)
min_length = 100
max_length = 10000
ideal_chunk_size_by_words = 1000
ideal_overlap = 200
sample_text = "examples/arxiv_paper.txt"  # 8,000 token paper
preferred_model = "claude"
chunk_summary_length = 200  # Added these to add more oomph to the summary
final_summary_length = 750

# Our prompts
keyword_extract_prompt_string = """
You are an efficient key word detector. Your task is to extract only all the important key words and phrases without any duplicates from the below chunk of text.

Text: {{text_chunk}}

Think "step by step" to identify and all the important key words and pharses only and output should be comma seperated. Only return the list of keywords, nothing more.
""".strip()

summarize_chunk_prompt_string = """
You are an expert text summarizer. Given the below text content and the important key words, write a concise but information loaded summary.

Text Content: {{text_chunk}}

Important Keywords: {{key_words}}

Think "step by step" how to utilize both the important keywords and text content to create a great summary of at least {{chunk_summary_length}} words.
""".strip()

reduce_prompt_string = """
The following is set of summaries:

{% for summary in summaries %}
##################### 
{{summary}}
##################### 
{% endfor %}

Take these and distill them into one final, consolidated summary, of at least {{final_summary_length}} words.

Your summary should contain the key points and any controversies identified in the summaries, making sure to cover all critical information concisely.
""".strip()


# Our functions
def get_sample_text() -> str:
    """
    Get a sample text to use for testing.
    """
    with open(sample_text, "r") as f:
        text = f.read()
    return text


def chunk_text_by_words(
    text: str, chunk_size: int = ideal_chunk_size_by_words, overlap: int = ideal_overlap
) -> list[str]:
    """
    Takes a string, chunk size, and overlap, then returns a list of overlapping text chunks.
    This version preserves all characters, including spaces and punctuation, for LLM summarization.

    Args:
    text (str): The input text to be chunked.
    chunk_size (int): The ideal number of words per chunk. Defaults to 100.
    overlap (int): The number of words to overlap between chunks. Defaults to 20.

    Returns:
    list[str]: A list of text chunks.
    """
    # Split the text into words, preserving spaces and punctuation
    words = text.split()
    # Initialize the list to hold our chunks
    chunks = []
    # Iterate through the words to create chunks
    for i in range(0, len(words), chunk_size - overlap):
        # Get the words for this chunk
        chunk_words = words[i : i + chunk_size]
        # Reconstruct the text for this chunk
        chunk_text = " ".join(chunk_words)
        # If this isn't the first chunk, find the start of the first complete sentence
        if i > 0:
            sentence_start = chunk_text.find(".")
            if sentence_start != -1:
                chunk_text = chunk_text[sentence_start + 1 :].strip()
        # If this isn't the last chunk, find the end of the last complete sentence
        if i + chunk_size < len(words):
            sentence_end = chunk_text.rfind(".")
            if sentence_end != -1:
                chunk_text = chunk_text[: sentence_end + 1]
        # Add the chunk to our list
        chunks.append(chunk_text)
    return chunks


def summarize_chunks_with_keywords(
    chunks_with_keywords: list[tuple[str]], run_async=False
) -> list[str]:
    """
    This routes to either the async or sync version of the function.
    """
    if run_async:
        return summarize_chunks_with_keywords_async(chunks_with_keywords)
    else:
        return summarize_chunks_with_keywords_sync(chunks_with_keywords)


def summarize_chunks_with_keywords_sync(
    chunks_with_keywords: list[tuple[str]],
) -> list[str]:
    """
    Returns extractive summary on a text chunk using the given keywords.
    This is the synchronous version of the function.
    """
    prompt = Prompt(summarize_chunk_prompt_string)
    model = Model("gpt3")
    summarized_chunks = []
    for chunk, keywords in chunks_with_keywords:
        chain = Chain(prompt=prompt, model=model)
        summary = chain.run(
            {
                "text_chunk": chunk,
                "key_words": keywords,
                "chunk_summary_length": chunk_summary_length,
            },
            verbose=False,
        )
        summarized_chunks.append(summary.content)
    return summarized_chunks


def summarize_chunks_with_keywords_async(
    chunks_with_keywords: list[tuple[str]],
) -> list[str]:
    """
    Returns extractive summary on a text chunk using the given keywords.
    """
    summarize_chunks_prompts = []
    prompt = Prompt(summarize_chunk_prompt_string)
    model = Model("gpt3")
    for chunk, keywords in chunks_with_keywords:
        summarize_chunk_prompt = prompt.render(
            {
                "text_chunk": chunk,
                "key_words": keywords,
                "chunk_summary_length": chunk_summary_length,
            }
        )
        summarize_chunks_prompts.append(summarize_chunk_prompt)
    print("running async: summarizing chunks")
    summarized_chunks = model.run_async(prompts=summarize_chunks_prompts, verbose=True)
    return summarized_chunks


def extract_keywords(text_chunks: list[str]) -> list[tuple[str, str]]:
    """
    This uses sync; future optimization will use async.
    Takes a list of text chunks, and returns a list of tuples, with the chunk and its keywords.
    """
    print("Extracting keywords...")
    # extract_keywords_prompts = []
    prompt = Prompt(keyword_extract_prompt_string)
    model = Model("gpt3")
    parser = Parser(Answer_List)
    # for chunk in text_chunks:
    #     extract_keywords_prompt = prompt.render({'text_chunk':chunk})
    #     extract_keywords_prompts.append(extract_keywords_prompt)
    # print("running async: generating keywords for chunks")
    # keywords_list = model.run_async(prompts = extract_keywords_prompts, pydantic_model = Answer_List, verbose = True)
    keywords_list = []
    for chunk in text_chunks:
        chain = Chain(prompt=prompt, model=model, parser=parser)
        response = chain.run({"text_chunk": chunk}, verbose=True)
        keywords_list.append(response.content.answer)
    assert len(keywords_list) == len(text_chunks)
    chunks_with_keywords = list(zip(text_chunks, keywords_list))
    return chunks_with_keywords


def map_chain(text_chunks: list[str]) -> list[str]:
    """
    Uses sync by default, future optimization will use async.
    Takes a list of text chunks, performs extractive summarization on each, and returns a dict, with chunks as keys and summaries as values.
    """
    print("Summarizing chunks...")
    chunks_with_keywords = extract_keywords(text_chunks)
    # # assuming 30 is a limit for async; can change this after experimentation.
    # if len(chunks_with_keywords) < 31:
    # 	summarized_chunks = summarize_chunks_with_keywords(chunks_with_keywords, run_async = True)
    # else:
    summarized_chunks = summarize_chunks_with_keywords(
        chunks_with_keywords, run_async=False
    )
    return summarized_chunks


def reduce_chain(summarized_chunks: list[str]) -> str:
    """
    Combines the summaries from the chunks into a single summary.
    """
    print("Summarizing the summaries.")
    prompt = Prompt(reduce_prompt_string)
    model = Model(preferred_model)
    chain = Chain(prompt=prompt, model=model)
    summary = chain.run(
        {"summaries": summarized_chunks, "final_summary_length": final_summary_length},
        verbose=False,
    )
    return summary


def summarize_medium_text(text: str) -> str:
    """
    Wrapper function.
    Summarizes a medium-length text using chunking, extractive summarization, and map/reduce.
    """
    text_chunks = chunk_text_by_words(text)
    summarized_chunks = map_chain(text_chunks)
    final_summary = reduce_chain(summarized_chunks)
    if final_summary == None:
        print("No medium summary generated")
    return final_summary.content


if __name__ == "__main__":
    text = get_sample_text()
    summary = summarize_medium_text(text)
    print(summary)

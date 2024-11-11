"""
This generates and saves a Book object to our MongoDB database.
Inspired by my Course and Get scripts.
"""

from Book import Book, Chapter
from pymongo import MongoClient

# Our functions
def load_book(book_file) -> str:
    """
    Load book from a file, which could either be text, pdf, or epub.
    Use pandoc to convert to markdown.
    Return the entire text of the book as a string.
    """
    pass

def has_TOC(book_head: str, preferred_model = "gpt3") -> bool:
    """
    Given a book head, this function will return True if the book has a Table of Contents.
    This leverages a simple LLM chain.
    """
    pass

def get_TOC(book_head: str, preferred_model = "gpt") -> Book.TOC:
    """
    Given a book head, generate a TOC object.
    This leverages an LLM chain with corpora + few shot examples.
    The TOC object is a list of chapter titles, with high confidence from LLM model.
    """
    pass

def get_book_title(book_head: str, preferred_model = "gpt3") -> str:
    """
    Given a book head, find the book title.
    This leverages a simple LLM chain.

    """
    pass

def split_text_by_chapters(book_text: str, toc: str) -> list[Book.Chapter]:
    """
    Given a book text and a TOC, this function will split the text into chapters.
    This is an NLP task that related to Text Segmentation.
    """
    pass

def Get_Book():
    pass
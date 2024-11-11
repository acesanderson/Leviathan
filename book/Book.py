"""
This defines our Book pydantic class.
This class takes in the text of a book and processes it for summarization and RAG.
"""

from pydantic import BaseModel
import chromadb


class Chapter(BaseModel):
    title: str  # The title of the chapter; guessed by an LLM.
    text: str  # The text of the chapter.
    summary: str  # Summary created from Long_summarize.py
    chunks: list  # Chunks of the
    vector_store: chromadb.Collection  # The vector store for the chapter's chunks
    clusters: list


class TOC(BaseModel):
    chapter_titles: list[str]


class Book(BaseModel):
    title: str
    text: str
    summary: str
    chunks: list
    vector_store: chromadb.Collection
    chapters: list[Chapter]
    clusters: list
    toc: str

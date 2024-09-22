"""
This defines our Book pydantic class.
This class takes in the text of a book and processes it for summarization and RAG.
"""

from pydantic import BaseModel
import chromadb

class Chapter(BaseModel):
    title: str
    text: str
    summary: str
    chunks: list
    vector_store: chromadb.Collection
    clusters: list

class TOC(BaseModel):
    chapter_titles: list[str]

class Book(BaseModel):
    title: str
    text: str
    summary: str
    chunks: list
    chapters: list # This is the hardest bit
    vector_store: chromadb.Collection
    chapters: list[Chapter]
    clusters: list
    toc: str

"""
This is the much more complicated summarization process we use for books and other megalong text formats.

Eventually we will incorporate this back into text_summarization (or better yet, combine as a package with the different wrapper functions in separate scripts).
"""


from text_summarization import generate_test_book
import spacy
import networkx as nx
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF, XSD
from typing import Dict, Any

text = generate_test_book()

nlp = spacy.load("en_core_web_sm")

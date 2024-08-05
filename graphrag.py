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
import matplotlib.pyplot as plt

text = generate_test_book()

shorter_text = """
# The Voyage of the Crimson Horizon

Captain Elias Blackwood, commander of the British Royal Navy frigate HMS Crimson Horizon, set sail from Plymouth Harbor in the spring of 1768. His mission, sanctioned by King George III, was to explore the uncharted waters of the South Pacific and establish trade relations with any civilizations encountered.

Blackwood's first mate, Jonathan Hawkins, had served with him for over a decade, their friendship forged in the fires of the Seven Years' War. The ship's naturalist, Dr. Thomas Finch from the Royal Society, eagerly anticipated documenting new species of flora and fauna.

Their first port of call was Lisbon, where they resupplied and acquired a Portuguese interpreter, Maria Cortez. Her linguistic skills would prove invaluable in their encounters with various indigenous peoples.

As they rounded the Cape of Good Hope, the Crimson Horizon faced treacherous storms. The ship's carpenter, William Cooper, worked tirelessly to repair damage to the hull, saving them from certain doom.

In Madagascar, they traded with the Merina Kingdom, ruled by King Andrianampoinimerina. The monarch gifted Blackwood with a rare gemstone, solidifying an alliance between Britain and Madagascar.

Sailing eastward, they discovered an uncharted island they named New Albion. The local Kanak people, led by Chief Kaoha, initially greeted them with suspicion but warmed to the crew after Dr. Finch treated several villagers suffering from an unknown illness.

Their journey took an unexpected turn when they encountered the Dutch East India Company ship Gelderland, captained by Hendrik van der Meer. The two vessels engaged in a tense standoff, neither willing to cede the newly discovered trading routes.

Near the island of Tonga, the Crimson Horizon was attacked by pirates led by the notorious Captain Blackbeard's former quartermaster, Israel Hands. Blackwood's superior tactics and Hawkins' skilled gunnery repelled the attack, cementing the crew's loyalty to their officers.

The expedition's crowning achievement came when they made landfall on the eastern coast of New Holland (Australia). There, they established Fort Endeavour, named after the ship of the famed explorer James Cook. This outpost would serve as a vital link in Britain's growing colonial empire.

After two years at sea, the Crimson Horizon returned to Plymouth, its holds filled with exotic goods, scientific specimens, and detailed maps of previously unknown lands. Captain Blackwood's voyage had expanded the boundaries of the known world and strengthened Britain's position as a global power in the Age of Exploration.
"""

nlp = spacy.load("en_core_web_sm")

def generate_knowledge_graph(text: str) -> nx.Graph:
	"""
	Generate a knowledge graph from the given text using SpaCy for NLP and NetworkX for graph representation.
	Args:
		text (str): The input text to process.
	Returns:
		nx.Graph: A NetworkX graph representing the extracted knowledge.
	"""
	# Process the text using SpaCy
	doc = nlp(text)
	# Create a graph
	G = nx.Graph()
	# Extract entities and add them as nodes
	for ent in doc.ents:
		G.add_node(ent.text, label=ent.label_)
	# Extract relationships and add them as edges
	for token in doc:
		if token.dep_ in ("nsubj", "dobj"):
			G.add_edge(token.head.text, token.text, label=token.dep_)
	return G

def graph_to_rdf(G: nx.Graph) -> Graph:
	"""
	Convert a NetworkX graph to an RDF graph.
	
	Args:
		G (nx.Graph): The input NetworkX graph.
	
	Returns:
		rdflib.Graph: The resulting RDF graph.
	"""
	# Create an RDF graph
	rdf_graph = Graph()
	# Add nodes to the RDF graph
	for node, data in G.nodes(data=True):
		node_uri = URIRef(f"http://example.org/{node.replace(' ', '_')}")
		rdf_graph.add((node_uri, RDF.type, FOAF.Person))
		rdf_graph.add((node_uri, FOAF.name, Literal(node, datatype=XSD.string)))
	# Add edges to the RDF graph
	for u, v, data in G.edges(data=True):
		u_uri = URIRef(f"http://example.org/{u.replace(' ', '_')}")
		v_uri = URIRef(f"http://example.org/{v.replace(' ', '_')}")
		rdf_graph.add((u_uri, URIRef(f"http://example.org/{data['label']}"), v_uri))
	return rdf_graph

def query_rdf_graph(rdf_graph: Graph, query: str) -> list[Dict[str, Any]]:
	"""
	Execute a SPARQL query on the given RDF graph.

	Args:
		rdf_graph (rdflib.Graph): The RDF graph to query.
		query (str): The SPARQL query string.
	Returns:
		list[Dict[str, Any]]: A list of dictionaries containing the query results.
	"""
	results = []
	for row in rdf_graph.query(query):
		results.append({str(var): str(value) for var, value in row.asdict().items()})
	return results


def visualize_graph(g):
    # Create a layout for the nodes
    pos = nx.spring_layout(g)
    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw(g, pos, with_labels=True, node_color='lightblue', 
            node_size=1500, font_size=10, font_weight='bold')
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(g, 'label')
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
    # Show the plot
    plt.title("Knowledge Graph Visualization")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
	# Sample text input
	text = shorter_text
	# Generate knowledge graph
	graph = generate_knowledge_graph(text)
	# Convert to RDF
	rdf_graph = graph_to_rdf(graph)
	# Define SPARQL query
	sparql_query = """
	SELECT ?subject ?predicate ?object
	WHERE {
		?subject ?predicate ?object .
	}
	"""
	# Execute query and print results
	results = query_rdf_graph(rdf_graph, sparql_query)
	for result in results:
		print(f"{result['subject']} {result['predicate']} {result['object']}")



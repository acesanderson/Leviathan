from Tutorialize import Tutorialize_Async
from time import sleep

nlp_topics = """
Embeddings in NLP: Vector representations of words, sentences, or documents that capture semantic meaning, allowing machines to understand and compare text.
Transformer Architecture: The fundamental neural network structure behind modern NLP models, using self-attention mechanisms to process sequential data effectively.
Transfer Learning in NLP: The concept of using pre-trained models on large datasets and fine-tuning them for specific tasks, saving time and computational resources.
Sentence Similarity: Techniques for measuring how alike two sentences are in meaning, not just in words, which is a core application of sentence embeddings.
Cosine Similarity: A metric used to measure the similarity between two vectors, commonly applied to compare sentence embeddings.
Semantic Search: Using embeddings to find relevant documents or sentences based on meaning rather than exact keyword matches.
Clustering Text Data: Grouping similar texts together based on their embeddings, useful for organizing large collections of documents or identifying themes.
Fine-tuning Transformer Models: The process of adapting a pre-trained model to a specific task or domain by training it on a smaller, task-specific dataset.
Siamese and Triplet Networks: Neural network architectures used to train embedding models, often employed in SentenceTransformers for specific tasks.
Contrastive Learning: A training approach where the model learns to distinguish between similar and dissimilar pairs of inputs, crucial for creating effective embeddings.
Dimensionality Reduction for Embeddings: Techniques like PCA or t-SNE to visualize high-dimensional embeddings or reduce computational complexity.
Cross-lingual Embeddings: Models capable of generating comparable embeddings across different languages, enabling multilingual applications.
Data Augmentation for NLP: Techniques to artificially increase the size and diversity of training data, improving model robustness and performance.
Evaluation Metrics for Embeddings: Methods to assess the quality of embeddings, such as intrinsic evaluation (e.g., analogy tasks) and extrinsic evaluation (performance on downstream tasks).
Ethical Considerations in NLP: Understanding potential biases in pre-trained models and embeddings, and strategies to mitigate them for fair and responsible AI applications.
""".strip().split(
	"\n"
)

persona = (
	"natural language processing, generative AI, sentencetransformers library in python"
)

chunked_topics = [nlp_topics[:5], nlp_topics[5:10], nlp_topics[10:15]]

tutorials = []
for topic_chunk in chunked_topics:
	tutorials.append(Tutorialize_Async(topic_chunk, persona, save_to_file=True))
	sleep(5)

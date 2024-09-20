## What this project is for

Summarize is a collection of text summarization scripts that can be used over command line, and leveraged by various other scripts like obsidian.py, Tutorialize, arxiv, and more. This both reflects my aspirations to learn more about machine learning/NLP/LLM development, as well as a practical desire to develop better ways to quickly leverage a variety of resources and accelerated my research.

### Scripts
- Chain of Density (for texts < 1500 words)
- Medium Summarization (for texts < 10,000 words)
- Long Summarization (for text > 10,000 words)
- Query-based Summarization

### Some use cases
- Get CoD from a medium text by running medium summarization and then running CoD on that. 
- Proper RAG on a book to get an answer to a question (including GraphRAG)

### Progress
- [x] Created placeholder with Summary.txt. This will sort texts and handle command line arguments. It will also have config options that can to to the subsidia
ry scripts.
- [x] Create CoD standalone script, which works like a charm.
- [ ] Create Medium summarization standalone script
- [ ] Test chaining Medium -> CoD use case
- [ ] Institute query-based summarization
 - [ ] research QBS and how it could be architected

from text_summarization import summarize_medium_text

with open("GSR_2024.txt", "r") as f:
	coursera = f.read()

summarize_medium_text(coursera)

from Leviathan.leviathan.Leviathan import categorize_url, retrieve_text, summarize

url = "https://www.bbc.com/news/world-asia-56900013"

print("Categorizing URL...")
category = categorize_url(url)

print(category)

print("Retrieving text...")
text = retrieve_text(url, category)

print(text)

print("Summarizing text...")
summary = summarize(text, category)

print(summary)

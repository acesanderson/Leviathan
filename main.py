from Leviathan import categorize_url, retrieve_text, summarize

url = "https://www.youtube.com/watch?v=GUXxLy68EF8&t=3s"

print("Categorizing URL...")
category = categorize_url(url)

print(category)

print("Retrieving text...")
text = retrieve_text(url, category)

print(text)

print("Summarizing text...")
summary = summarize(text, category)

print(summary)

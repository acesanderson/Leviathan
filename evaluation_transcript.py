from summarize_long_text import summarize_long_text

transcript_file = "evaluation_transcript.txt"

with open(transcript_file, "r") as f:
    transcript = f.read()

if __name__ == "__main__":
    summary = summarize_long_text(transcript)
    print(summary)


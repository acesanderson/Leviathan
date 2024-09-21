"""
Wrapper function for my various summarization scripts.
Routes a text to the correct summarization script based on the input parameters.
"""




# Customizable settings
def get_config():
	# Define your variables here
	model_choice = "gpt"
	chain_of_density_summary_length_in_words = 250
	text_sizes = {
		'short': 1500,
		'medium': 10000,
		'long': 10001
	}
	ideal_chunk_size_by_words = 1000
	# Get the local variables at this point
	num_clusters = 11
	test_text_path = 'tests/article.txt'
	test_book_path = 'tests/NLTK.txt'
	local_vars = locals()
	# You can now return the local_vars as your config dictionary
	return local_vars

config_dict = get_config()


# if __name__ == "__main__":

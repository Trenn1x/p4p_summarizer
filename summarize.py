from transformers import pipeline
import glob
import os

# Load the summarization pipeline
summarizer = pipeline("summarization")

# Function to summarize a single post with dynamic length constraints
def summarize_text(text):
    # Calculate dynamic max_len and min_len based on input length
    word_count = len(text.split())
    
    if word_count < 20:
        # For very short texts, no summarization is needed
        return text
    else:
        max_len = min(50, int(word_count * 0.75))  # Max length: 75% of input length or 50, whichever is smaller
        min_len = max(5, int(max_len * 0.5))  # Min length: 50% of max_len or 5, whichever is larger
        
        # Generate the summary
        summary = summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)
        return summary[0]['summary_text']

# Directory path for text files (simulated forum posts)
posts_dir = "./forum_posts"
os.makedirs(posts_dir, exist_ok=True)  # Ensure the directory exists

# Loop through each file in the posts directory
for filepath in glob.glob(f"{posts_dir}/*.txt"):
    with open(filepath, "r") as file:
        text = file.read()
        print(f"\nOriginal Text from {os.path.basename(filepath)}:")
        print(text)
        
        # Generate and display the summary
        summary = summarize_text(text)
        print("\nGenerated Summary:")
        print(summary)


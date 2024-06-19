# filename: summarize_arxiv_llm.py

import arxiv
from datetime import datetime, timedelta, timezone
from transformers import pipeline

# Define the date range for the last 7 days
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=7)

# Search for papers in the "cs.CL" category (Computation and Language)
search = arxiv.Search(
    query="cat:cs.CL",
    max_results=50,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

# Fetch the results
results = list(search.results())

# Filter results based on the date range
filtered_results = [result for result in results if start_date <= result.updated <= end_date]

# Extract the abstracts
abstracts = [result.summary for result in filtered_results]

# Load a pre-trained summarization model
summarizer = pipeline("summarization")

# Summarize each abstract
summaries = [summarizer(abstract, max_length=150, min_length=30, do_sample=False)[0]['summary_text'] for abstract in abstracts]

# Print the summaries
for i, summary in enumerate(summaries):
    print(f"Paper {i+1} Summary:\n{summary}\n")

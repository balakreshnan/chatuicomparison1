# filename: fetch_arxiv_papers.py
import feedparser
from datetime import datetime, timedelta

# Define the base URL for the arXiv API
ARXIV_API_URL = "http://export.arxiv.org/api/query?"

# Define the search query parameters
category = "cs.CL"  # cs.CL is the arXiv category for Computation and Language which includes LLM
search_query = "all:language+AND+all:model"  # This is a simple query, it might need refinement
start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d%H%M%S")

# Construct the full query URL
query = f"search_query={search_query}+AND+submittedDate:[{start_date}+TO+30000101000000]&sortBy=submittedDate&sortOrder=descending"
url = ARXIV_API_URL + query

# Fetch the papers
def fetch_papers(url):
    print(f"Fetching papers from arXiv with the following query: {url}")
    feed = feedparser.parse(url)
    papers = []

    for entry in feed.entries:
        # Extract the title and summary (abstract) of each paper
        title = entry.title
        summary = entry.summary
        papers.append((title, summary))

    return papers

# Fetch and print the papers
papers = fetch_papers(url)
for title, summary in papers:
    print(f"Title: {title}\nSummary: {summary}\n")

# Note: This script does not perform summarization. It only fetches and prints the papers.
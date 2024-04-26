# filename: fetch_arxiv_llm_papers.py
import feedparser
import urllib.parse
from datetime import datetime, timedelta

# Define the base URL for the arXiv API
ARXIV_API_URL = "http://export.arxiv.org/api/query?"

# Define the search query parameters
search_query = "cat:cs.CL AND (abs:\"large language model\" OR title:\"large language model\")"
start = 0
max_results = 100
sort_by = "submittedDate"
sort_order = "descending"

# Calculate the date 7 days ago from today
date_seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

# Encode the query parameters
params = {
    'search_query': search_query,
    'start': start,
    'max_results': max_results,
    'sortBy': sort_by,
    'sortOrder': sort_order,
    'submittedDate': date_seven_days_ago
}
encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

# Construct the full query URL
query = f"{ARXIV_API_URL}{encoded_params}"

# Fetch the data from arXiv
feed = feedparser.parse(query)

# Check if the feed entries exist
if not feed.entries:
    print("No papers found for the last 7 days on LLM.")
else:
    # Print the titles and abstracts of the papers
    for entry in feed.entries:
        print(f"Title: {entry.title}\nAbstract: {entry.summary}\n")
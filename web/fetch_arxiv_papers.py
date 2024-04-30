# filename: fetch_arxiv_papers.py
import feedparser
import urllib.parse
from datetime import datetime, timedelta

# Define the base URL for the arXiv API
ARXIV_API_URL = "http://export.arxiv.org/api/query?"

# Define the search parameters
search_query = "cat:cs.CL AND (all:Large Language Models OR all:LLM)"  # cs.CL is the category for Computation and Language
start_index = 0  # start at the first result
max_results = 100  # the maximum number of results to fetch
sort_by = "submittedDate"
sort_order = "descending"

# Calculate the date 7 days ago from today
date_seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

# Encode the search query to handle spaces and special characters
encoded_search_query = urllib.parse.quote_plus(search_query)

# Construct the query URL
query = f"{ARXIV_API_URL}search_query={encoded_search_query}&start={start_index}&max_results={max_results}&sortBy={sort_by}&sortOrder={sort_order}&submittedDate={date_seven_days_ago}"

# Fetch the results using feedparser
feed = feedparser.parse(query)

# Open a file to write the output
with open('arxiv_papers_summary.txt', 'w', encoding='utf-8') as file:
    # Check if the fetch was successful
    if feed.get('status') != 200:
        file.write(f"Failed to fetch data from arXiv. Status code: {feed.get('status')}\n")
    else:
        # Write the number of papers found to the file
        file.write(f"Number of papers found: {len(feed.entries)}\n")
        # Write the titles and publish dates of the papers to the file
        for entry in feed.entries:
            title = entry.title
            published = entry.published
            authors = ', '.join(author.name for author in entry.authors)
            summary = entry.summary
            file.write(f"Title: {title}\n")
            file.write(f"Published Date: {published}\n")
            file.write(f"Authors: {authors}\n")
            file.write(f"Abstract: {summary}\n")
            file.write("---------------------------------------------------------\n")

print("The arXiv papers summary has been written to 'arxiv_papers_summary.txt'")
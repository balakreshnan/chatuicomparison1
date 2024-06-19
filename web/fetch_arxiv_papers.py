# filename: fetch_arxiv_papers.py

import arxiv
from datetime import datetime, timedelta, timezone

# Define the search query and date range
query = "Large Language Models"
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=7)

# Perform the search
search = arxiv.Search(
    query=query,
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

# Fetch the papers using the Client class
client = arxiv.Client()

# Extract relevant information and filter by date
papers = []
for result in client.results(search):
    if start_date <= result.published <= end_date:
        paper_info = {
            "title": result.title,
            "summary": result.summary,
            "published": result.published,
            "url": result.entry_id
        }
        papers.append(paper_info)

# Print the extracted information with UTF-8 encoding
for paper in papers:
    print(f"Title: {paper['title']}".encode('utf-8', errors='ignore').decode('utf-8'))
    print(f"Published: {paper['published']}")
    print(f"Summary: {paper['summary']}".encode('utf-8', errors='ignore').decode('utf-8'))
    print(f"URL: {paper['url']}\n")
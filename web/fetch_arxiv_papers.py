# filename: fetch_arxiv_papers.py
import arxiv
import datetime
from dateutil import tz

# Define the search query and date range
search_query = 'cat:cs.CL AND (all:"large language model" OR all:"LLM")'
start_date = datetime.datetime.now(tz.tzutc()) - datetime.timedelta(days=7)

# Initialize the arXiv client
client = arxiv.Client()

# Search arXiv papers
search = arxiv.Search(
    query=search_query,
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

# Filter papers from the last 7 days and summarize
papers_summary = []
for result in client.results(search):
    if result.published >= start_date:
        papers_summary.append({
            'title': result.title,
            'summary': result.summary,
            'published': result.published
        })

# Print the summaries
for paper in papers_summary:
    print(f"Title: {paper['title']}")
    print(f"Published Date: {paper['published']}")
    print(f"Abstract: {paper['summary']}\n")
    print("--------------------------------------------------\n")

# Check if there are any papers
if not papers_summary:
    print("No papers found in the last 7 days on Large Language Models.")
# filename: fetch_arxiv_papers_requests.py
import requests
from datetime import datetime, timedelta

# Define the search parameters
search_query = 'cat:cs.CL AND (all:"large language model" OR all:"LLM")'
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

# Construct the query URL
url = f'http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending'

# Function to fetch papers from arXiv
def fetch_papers(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None

# Fetch the papers
papers_xml = fetch_papers(url)

# Check if we have papers to summarize
if papers_xml:
    print(papers_xml)
else:
    print("No papers found or there was an error fetching the papers.")

# filename: fetch_arxiv_papers_test.py
import requests
import feedparser

# Define the query parameters
query = 'cat:cs.CL AND (abs:"large language model" OR abs:"LLM")'
base_url = 'http://export.arxiv.org/api/query?'

# Define the parameters for the query
params = {
    'search_query': query,
    'start': 0,
    'max_results': 10  # Reduced the number for testing purposes
}

# Send the request to arXiv API
response = requests.get(base_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response using feedparser
    feed = feedparser.parse(response.content)
    # Check if there are entries
    if not feed.entries:
        print('No papers found with the specified query.')
    else:
        # Print the titles and summaries of the entries
        for entry in feed.entries:
            print('Title:', entry.title)
            print('Abstract:', entry.summary)
            print('Link:', entry.link)
            print('Published on:', entry.published)
            print('---' * 10)
else:
    print('Failed to fetch data from arXiv. Status code:', response.status_code)
# filename: fetch_arxiv_llm_papers.py

import requests
import datetime
from dateutil import parser

def fetch_arxiv_papers(query, start_date, end_date, max_results=100):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query={query}+AND+submittedDate:[{start_date}+TO+{end_date}]"
    url = f"{base_url}{search_query}&start=0&max_results={max_results}"
    response = requests.get(url)
    return response.text

def main():
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    query = "cat:cs.CL"  # cs.CL is the category for Computation and Language
    response = fetch_arxiv_papers(query, start_date_str, end_date_str)
    
    # Write the response to a file
    with open("arxiv_papers.xml", "w", encoding="utf-8") as file:
        file.write(response)

if __name__ == "__main__":
    main()
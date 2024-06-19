# filename: fetch_arxiv_llm.py

import requests
from datetime import datetime, timedelta

def fetch_arxiv_papers():
    base_url = "http://export.arxiv.org/api/query?"
    search_query = "cat:cs.CL"  # cs.CL is the category for Computation and Language
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    query = f"search_query={search_query}+AND+submittedDate:[{start_date}+TO+{end_date}]&start=0&max_results=100"
    
    response = requests.get(base_url + query)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch data from arXiv")
        return None

def parse_arxiv_response(response):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response)
    papers = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
        papers.append({"title": title, "summary": summary})
    return papers

def summarize_papers(papers):
    from transformers import pipeline
    summarizer = pipeline("summarization")
    summaries = []
    for paper in papers:
        summary = summarizer(paper["summary"], max_length=150, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append({"title": paper["title"], "summary": summary})
    return summaries

def main():
    response = fetch_arxiv_papers()
    if response:
        papers = parse_arxiv_response(response)
        summaries = summarize_papers(papers)
        for summary in summaries:
            print(f"Title: {summary['title']}\nSummary: {summary['summary']}\n")

if __name__ == "__main__":
    main()
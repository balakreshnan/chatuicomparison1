# filename: fetch_arxiv_llm.py

import subprocess
import sys

# Function to install required packages
def install_packages():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])

# Install required packages
install_packages()

import requests
import datetime
from dateutil.parser import parse

def fetch_arxiv_papers(query, max_results=100):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query={query}&start=0&max_results={max_results}"
    response = requests.get(base_url + search_query)
    return response.text

def parse_arxiv_response(response):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response)
    papers = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
        published = entry.find("{http://www.w3.org/2005/Atom}published").text
        papers.append({
            "title": title,
            "summary": summary,
            "published": published
        })
    return papers

def filter_recent_papers(papers, days=7):
    recent_papers = []
    now = datetime.datetime.now()
    for paper in papers:
        published_date = parse(paper["published"])
        if (now - published_date).days <= days:
            recent_papers.append(paper)
    return recent_papers

def summarize_papers(papers):
    from transformers import pipeline
    summarizer = pipeline("summarization")
    summaries = []
    for paper in papers:
        summary = summarizer(paper["summary"], max_length=150, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append({
            "title": paper["title"],
            "summary": summary
        })
    return summaries

def main():
    query = "cat:cs.CL AND ti:language model"
    response = fetch_arxiv_papers(query)
    papers = parse_arxiv_response(response)
    recent_papers = filter_recent_papers(papers)
    summaries = summarize_papers(recent_papers)
    for summary in summaries:
        print(f"Title: {summary['title']}\nSummary: {summary['summary']}\n")

if __name__ == "__main__":
    main()
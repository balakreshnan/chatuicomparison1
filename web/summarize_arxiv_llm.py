# filename: summarize_arxiv_llm.py

import requests
import datetime
from newspaper import Article
from bs4 import BeautifulSoup

def fetch_arxiv_papers(query, max_results=100):
    url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}'
    response = requests.get(url)
    return response.text

def parse_arxiv_response(response):
    soup = BeautifulSoup(response, 'html.parser')
    entries = soup.find_all('entry')
    papers = []
    for entry in entries:
        paper = {
            'title': entry.title.text,
            'summary': entry.summary.text,
            'published': entry.published.text,
            'link': entry.id.text
        }
        papers.append(paper)
    return papers

def filter_recent_papers(papers, days=7):
    recent_papers = []
    now = datetime.datetime.now()
    for paper in papers:
        published_date = datetime.datetime.strptime(paper['published'], '%Y-%m-%dT%H:%M:%SZ')
        if (now - published_date).days <= days:
            recent_papers.append(paper)
    return recent_papers

def summarize_paper(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.summary

def main():
    query = 'large language models'
    response = fetch_arxiv_papers(query)
    papers = parse_arxiv_response(response)
    recent_papers = filter_recent_papers(papers)
    
    for paper in recent_papers:
        print(f"Title: {paper['title']}")
        print(f"Published: {paper['published']}")
        print(f"Link: {paper['link']}")
        print("Summary:")
        try:
            summary = summarize_paper(paper['link'])
            print(summary)
        except Exception as e:
            print("Could not summarize the paper. Error:", e)
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    main()
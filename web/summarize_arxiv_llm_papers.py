# filename: summarize_arxiv_llm_papers.py

import xml.etree.ElementTree as ET
from transformers import pipeline

def extract_abstracts(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    abstracts = []
    
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        abstract = entry.find("{http://www.w3.org/2005/Atom}summary").text
        abstracts.append(abstract)
    
    return abstracts

def summarize_abstracts(abstracts):
    summarizer = pipeline("summarization")
    summaries = []
    
    for abstract in abstracts:
        summary = summarizer(abstract, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    
    return summaries

def main():
    file_path = "arxiv_papers.xml"
    abstracts = extract_abstracts(file_path)
    summaries = summarize_abstracts(abstracts)
    
    for i, summary in enumerate(summaries, 1):
        print(f"Summary {i}:\n{summary}\n")

if __name__ == "__main__":
    main()
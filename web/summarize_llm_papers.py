# filename: summarize_llm_papers.py
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# XML data as a string
xml_data = """
<feed xmlns="http://www.w3.org/2005/Atom">
  <!-- XML entries here -->
</feed>
"""

# Parse the XML data
root = ET.fromstring(xml_data)

# Define the namespace
namespace = {'atom': 'http://www.w3.org/2005/Atom'}

# Get the current date and the date 7 days ago
current_date = datetime.now()
date_7_days_ago = current_date - timedelta(days=7)

# Function to check if a paper is related to LLMs based on its title and summary
def is_llm_related(title, summary):
    keywords = ['large language model', 'llm', 'language model']
    for keyword in keywords:
        if keyword in title.lower() or keyword in summary.lower():
            return True
    return False

# Function to filter and summarize LLM papers from the last 7 days
def summarize_llm_papers(root, namespace):
    for entry in root.findall('atom:entry', namespace):
        # Extract publication date
        published_date = entry.find('atom:published', namespace).text
        published_date = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ')

        # Check if the paper was published in the last 7 days
        if date_7_days_ago <= published_date <= current_date:
            # Extract title and summary
            title = entry.find('atom:title', namespace).text
            summary = entry.find('atom:summary', namespace).text

            # Check if the paper is related to LLMs
            if is_llm_related(title, summary):
                print(f"Title: {title}\nPublished Date: {published_date.date()}\nAbstract: {summary}\n")

# Call the function to summarize LLM papers
summarize_llm_papers(root, namespace)
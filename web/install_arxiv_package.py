# filename: install_arxiv_package.py
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install the arxiv package
install("arxiv")

print("The arxiv package has been installed.")
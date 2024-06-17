# filename: install_yfinance.py

import subprocess
import sys

# Function to install a package using pip
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install yfinance
install("yfinance")
import streamlit as st
from figmatocode import figmatocode
from kustochartp import kustochartp
from imgtotext import imgtotext
from autogendesign import invokeagent
from autogenpapers import invokeagentpaper
from autogendesign1 import dynagents
from frecipe import foodreceipe
from chatpdf1 import processpdf
from diagrams import processdiagrams

# Set page size
st.set_page_config(
    page_title="Gen AI Application Validation",
    page_icon=":rocket:",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)

st.sidebar.image("bblogo1.png", use_column_width=True)
# Sidebar navigation
nav_option = st.sidebar.selectbox("Navigation", ["Home", "Chart", "ImgtoText", "AgentDesign", "ArxivPapers", "Design with Agents", "Food Recipe", "PDFExtract", "Diagrams", "About"])

# Display the selected page
if nav_option == "Home":
    figmatocode()
elif nav_option == "Chart":
    kustochartp()
elif nav_option == "ImgtoText":
    imgtotext()
elif nav_option == "AgentDesign":
    invokeagent()
elif nav_option == "ArxivPapers":
    invokeagentpaper()
elif nav_option == "Design with Agents":
    dynagents()
elif nav_option == "Food Recipe":
    foodreceipe()
elif nav_option == "PDFExtract":
    processpdf()
elif nav_option == "Diagrams":
    processdiagrams()
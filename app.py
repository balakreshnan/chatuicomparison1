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
from urltodoc import processurl
from workbench import processtext
from stocks import invokestocks 
#from vaagent import vaprocess
from videochat import processvideo
from comedytrack import comedytrack
from codeautogen import codeautogen
from csicheesegpt import csicheesegpt
from pickagent import pickagent
from foodresearch import foodresearchmain
from csirecipe import csirecipedesignmain
from speechtospeech import showaudio
from digiassist import digiassit
from azcustomvision import process_cv
from img3d import image_display

# Set page size
st.set_page_config(
    page_title="Gen AI Application Validation",
    page_icon=":rocket:",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)

# Load your CSS file
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to load the CSS
load_css("styles.css")

st.logo("bblogo1.png")
st.sidebar.image("bblogo1.png", use_column_width=True)

# Sidebar navigation
nav_option = st.sidebar.selectbox("Navigation", ["Home", "Workbench", "Chart", "ImgtoText", 
                                                 "AgentDesign", "ArxivPapers", "Design with Agents", 
                                                 "Food Recipe", "PDFExtract", "Diagrams", "URLtoDoc", 
                                                 "Stocks", "VideoChat", "ComedyTrack",
                                                 "Code Autogen", "Cheese GPT",
                                                 "Pick Agent", "Food Research",
                                                 "CSI Receipe", "SpeechToSpeech", 
                                                 "Shopping Cart", "Steel Scratches",
                                                 "Img3D","About"])

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
elif nav_option == "URLtoDoc":
    processurl()
elif nav_option == "Workbench":
    processtext()
elif nav_option == "Stocks":
    invokestocks()
elif nav_option == "VideoChat":
    processvideo()
elif nav_option == "ComedyTrack":
    comedytrack()
elif nav_option == "Code Autogen":
    codeautogen()
elif nav_option == "Cheese GPT":
    csicheesegpt()
elif nav_option == "Pick Agent":
    pickagent()
elif nav_option == "Food Research":
    foodresearchmain()
elif nav_option == "CSI Receipe":
    csirecipedesignmain()
elif nav_option == "SpeechToSpeech":
    showaudio()
elif nav_option == "Shopping Cart":
    digiassit()
elif nav_option == "Steel Scratches":
    process_cv()
elif nav_option == "Img3D":
    image_display()
#elif nav_option == "VisionAgent":
#    vaprocess()

st.sidebar.image("microsoft-logo-png-transparent-20.png", use_column_width=True)
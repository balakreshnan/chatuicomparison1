import os
from openai import AzureOpenAI
import gradio as gr
from dotenv import dotenv_values
import time
from datetime import timedelta
import json
import streamlit as st
from PIL import Image
import base64
import requests
import io
import autogen
from typing import Optional
from typing_extensions import Annotated
import PyPDF2


config = dotenv_values("env.env")

css = """
.container {
    height: 75vh;
}
"""

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_ASSITANT"], 
  api_key=config["AZURE_OPENAI_KEY_ASSITANT"],  
  api_version="2024-02-15-preview"
  #api_version="2024-02-01"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#model_name = "gpt-4-turbo"
model_name = "gpt-35-turbo-16k"

llm_config={"config_list": [
    {"model": "gpt-35-turbo", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-35-turbo-16k", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-4-turbo", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"}
    ],
    "timeout": 600,
    "cache_seed": 44,
    "temperature": 0.0}

def processpdfwithprompt(text, selected_optionmodel1, user_input1):
    returntxt = ""
    message_text = [
    {"role":"system", "content":"Use the provided articles delimited by triple quotes to answer questions. If the answer cannot be found in the articles, write I could not find an answer."}, 
    {"role": "user", "content": f""" {text} \n Question: {user_input1}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1.0,
        seed=42,
    )

    returntxt = response.choices[0].message.content
    return returntxt


def processpdf():
    returntxt = ""

    count = 0
    col1, col2 = st.columns(2)

    with col1:
        modeloptions1 = ["gpt-4-turbo", "gpt-35-turbo", "gpt-4"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        # Get user input
        user_input1 = st.text_input("Enter HTML content:", key=count, value="Extract product information and provide JSON output?")
        count += 1

        # Title
        #st.title("Image Uploader")

        # Image uploader
        uploaded_file = st.file_uploader("Choose an pdf...", type=["pdf"])
        # Display the uploaded image
        if uploaded_file is not None:
            #image = Image.open(uploaded_file)
            # image_bytes = uploaded_file.read()
            
            text = []
            pdf_reader = PyPDF2.PdfReader(uploaded_file)     
            for i in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[i]
                text.append(page.extract_text())
                print(page)
        

    with col2:
        #process_image
        # Display the uploaded image
        if uploaded_file is not None: 
            # Now process the pdf
            result_string = ''.join(text)
            rtext = processpdfwithprompt(result_string, selected_optionmodel1, user_input1)
            st.write(rtext)
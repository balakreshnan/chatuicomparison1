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
import streamlit.components.v1 as components

config = dotenv_values("env.env")

css = """
.container {
    height: 75vh;
}
"""

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_VISION"], 
  api_key=config["AZURE_OPENAI_KEY_VISION"],  
  #api_version="2024-02-15-preview"
  #api_version="2024-05-13"
  api_version="2024-02-01"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#model_name = "gpt-4-turbo"
#model_name = "gpt-35-turbo-16k"
model_name = "gpt-4o-g"

llm_config={"config_list": [
    {"model": "gpt-35-turbo", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-35-turbo-16k", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-4o-g", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-4o", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"}
    ],
    "timeout": 600,
    "cache_seed": 44,
    "temperature": 0.0}

def processdiagramprompt(selected_optionmodel, user_input1):
    returntxt = ""

    start_time = time.time()
    system_prompt = f"""You are Mermaid JS Chart Expert in javascript. Provide only the mermaid javascript code without any explanation.
    Adjust the height and width to show the chart properly.
    Show axis labels, values and title for the chart. Also show series name in the legend.
    Do Not provide any explanation or comments in the code. Use the dataset provide below.
    Create code for D3 version 6.0.0
    Only use the data provided. if can't find data then respond with no data found.
    Use Camel case for javascript functions.
    Create D3 code for version 6.0.0 and above
    Use Javascript for parsing date using Date function and format the date to yyyy-mm-dd format.

    Sources:
    {user_input1}
    """

    #message = f"Create a {selected_optioncharttype} chart plot for stocks for 6 months of tesla?"
    #message1 = f"Create a {selected_optioncharttype} chart for {message}"
    #message1 = f"{message}"
    message1 = f"Create a {user_input1} mermaid code."

    print('Chart selected: ' , message1)

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": message1.lower() },
    ]

    response = client.chat.completions.create(
        #model= "gpt-35-turbo", #"gpt-4-turbo", # model = "deployment_name".
        model=selected_optionmodel,
        #messages=history_openai_format,
        messages=messages,
        seed=42,
        temperature=0.0,
        max_tokens=2000,
        top_p=1.0,
        #stream=True
    )

    #print("KQL query created: ", response.choices[0].message.content)
    
    #htmloutput = """<script> 
    #response.choices[0].message.content
    #</script>"""
    returntxt = response.choices[0].message.content.replace("```","").replace("Javascript","").replace("javascript","").replace("mermaid","").replace("\"","'").strip()

    return returntxt

def mermaid_chart(mindmap_code):
    html_code = f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
    <div class="mermaid">{mindmap_code}</div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
    """
    return html_code


def processdiagrams():
    
    count = 0
    col1, col2 = st.columns(2)
    rtext = ""

    with col1:
        modeloptions = ["gpt-4o-g", "gpt-4o" ,"gpt-35-turbo", "gpt-4-turbo", "llama2", "mixstral"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel = st.selectbox("Select an Model:", modeloptions)
        
        # Get user input
        user_input = st.text_input("Enter scenario to create diagrams:", "Create a ecommerce online shopping card in Azure")

        if st.button("Submit"):
            count += 1
            
            rtext = processdiagramprompt(selected_optionmodel, user_input)

            chart_js = mermaid_chart(rtext)
            print("Javascript Text: ", chart_js)
            # Embed HTML content with JavaScript code for the chart
            #st.html(chart_js)
            components.html(chart_js, scrolling=True, height=600, width=500)
            # st.markdown(chart_js, unsafe_allow_html=True)

    with col2:
        # Create a button for the user to submit the form
        if rtext:
            #chart_js = f"""
            #<div class="mermaid">
            #{rtext}
            #</div>
            #<script type="module">
            #import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js';
            #</script>
            #"""

            chart_js = mermaid_chart(rtext)
            print("Javascript Text: ", chart_js)
            # Embed HTML content with JavaScript code for the chart
            # st.components.v1.html(chart_js, height=350, width=600, scrolling=True)
            #st.code(chart_js, language='Javascript')
           
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
from streamlit import session_state as state
import azure.cognitiveservices.speech as speechsdk
from audiorecorder import audiorecorder
import pyaudio
import wave
from azure.identity import DefaultAzureCredential
import uuid

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

config = dotenv_values("env.env")

css = """
.container {
    height: 75vh;
}
"""

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_VISION"], 
  api_key=config["AZURE_OPENAI_KEY_VISION"],  
  api_version="2024-05-01-preview"
  #api_version="2024-02-01"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#model_name = "gpt-4-turbo"
#model_name = "gpt-35-turbo-16k"
model_name = "gpt-4o-g"

search_endpoint = config["AZURE_AI_SEARCH_ENDPOINT"]
search_key = config["AZURE_AI_SEARCH_KEY"]
search_index=config["AZURE_AI_SEARCH_INDEX1"]
SPEECH_KEY = config['SPEECH_KEY']
SPEECH_REGION = config['SPEECH_REGION']
SPEECH_ENDPOINT = config['SPEECH_ENDPOINT']

citationtxt = ""

def process_query_json(customername, selected_optionmodel):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Get the executive list for {customername} 
     Only respond output in JSON format. For String enclose in double quotes."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_profile(execname, selected_optionmodel, customername):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Get the profiles for executive {execname} who work at {customername}
     List their important goal they want to achive and their background."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_prority(execname, selected_optionmodel, customername):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Get the Prority for executive {execname} who work at {customername}.
     Analzye their background and provide the prority. Also look at revene statements like 10K and quarterly reports.
     List their important goal they want to achive and their background."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_tenk(execname, selected_optionmodel, customername):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Create insights from latest 1oK reports for company {customername}.
     Analzye their background and provide Insights.
     List their important Insights the company is planning to achieve."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_quarterly(execname, selected_optionmodel, customername):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Create insights from latest quarterly reports for company {customername}.
     Analzye their background and provide Insights. Only use the current quarter.
     List their important Insights the company is planning to achieve."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_futuretrends(execname, selected_optionmodel, customername):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Create future insights for company {customername}. Based on their revenue performance and market trends.
     Analzye their background and provide Insights. Anayze the industry trends and provide insights.
     When you analyze based that on customer's priorites and goals provided in the 10K and quarterly reports.
     List their important Insights the company is planning to achieve."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_recommendations(execname, selected_optionmodel, customername):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Sales AI Assistant, your job is to research about a customer for planning. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Provide recomendations for company {customername} on what are some of the key areas they should focus on.
     Where can we improve their existing bottom line and increase the top line.
     What technology areas to focus on and what are the key areas to focus on.
     Provide the insights as buttlet points."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def process_prompt(prompt, selected_optionmodel, systemprompt):
    returntxt = ""
    Execlist = ""

    start_time = time.time()

    message_text = [
    {"role":"system", "content":f"""{systemprompt}
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""{prompt}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        #response_format="json"
   )

    #returntxt = response.choices[0].message.content + "\n<br>"

    returntxt = json.dumps(response.choices[0].message.content, indent=4)

    reponse_time = time.time() - start_time 

    #returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"
    print(f"Response Time: {reponse_time:.2f} seconds")

    return response.choices[0].message.content

def cust_planning():
    returntxt = ""
    citationtxt = ""
    extreturntxt = ""
    summartycsitext = ""
    profiletxt = ""
    proritytxt = ""
    recommended = []
    data = {}
    json_object = {}
    tenktxt = ""
    quarterlytxt = ""
    futuretxt = ""
    recommnedationtxt = ""
    promptoutput = ""


    if 'execlist' not in st.session_state:
        st.session_state.execlist = recommended
    
    if 'json_object' not in st.session_state:
        st.session_state.json_object = json_object

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Research Ext", "Research Int", "Product Analaysis"])
    with tab1:
        count = 0
        col1, col2 = st.columns([1,2])
        with col1:
            selected_optionmodel = st.selectbox("Select Model", ["gpt-4o-g", "gpt-4o"])
            customername = st.text_input("Company:", value="Walmart")
            if st.button("List Executives"):
                returntxt = process_query_json(customername, selected_optionmodel)
                returntxt = returntxt.replace("```", "").replace("json", "").replace("JSON", "").replace("```", "")
                print(returntxt)
                if returntxt:
                    json_object = json.loads(returntxt)  
                    for object in json_object["executives"]:
                        #print(object)
                        #print(f"Executive Name: {object['name']}")
                        recommended.append(object['name'])
                        st.session_state.execlist.append(object['name'])

                    # Initialize session state for the selectbox options
                    st.session_state.json_object = json_object
            recipelist = st.selectbox('Choose an Executive:', st.session_state.execlist)
            if st.button("Their Profile"):
                profiletxt = process_profile(recipelist, selected_optionmodel, customername)
            if st.button("Priority"):
                proritytxt = process_prority(recipelist, selected_optionmodel, customername)
            if st.button("10K Reports"):
                tenktxt = process_tenk(recipelist, selected_optionmodel, customername)
            if st.button("Quarterly Reports"):
                quarterlytxt = process_quarterly(recipelist, selected_optionmodel, customername)
            if st.button("Future Trends"):
                futuretxt = process_futuretrends(recipelist, selected_optionmodel, customername)
            if st.button("Recommendations"):
                recommnedationtxt = process_recommendations(recipelist, selected_optionmodel, customername)
        with col2:
            if profiletxt:
                st.markdown(profiletxt, unsafe_allow_html=True)
            if proritytxt:
                st.markdown(proritytxt, unsafe_allow_html=True)
            if tenktxt:
                st.markdown(tenktxt, unsafe_allow_html=True)
            if quarterlytxt:
                st.markdown(quarterlytxt, unsafe_allow_html=True)
            if futuretxt:
                st.markdown(futuretxt, unsafe_allow_html=True)
            if recommnedationtxt:
                st.markdown(recommnedationtxt, unsafe_allow_html=True)
    with tab2:
        st.write("Internal Research") 
    with tab3:
        st.write("Product Analysis")

        col1, col2, col3 = st.columns([1,1,1]) 
        with col1:
            product = st.text_input("Product:", value="Azure Open AI")
            productcompany = st.text_input("Company:", value="Microsoft")
            metaprompts = st.text_area("Meta Prompts:", height=20, value="You are Salesperson Agent helping salespeople to provide information about a product, provide answers only from the document information. If answers are not found, please respond there is not enough information to provide. Ask for follow up question. Be precise and provide details and be calm and provide positive answers. Don't get frustrated but calmly ignore the questions. Bullet point the answer if you can. Summarize: ")
            meetingtopic = st.text_input("Meeting Topic:", value="Gen AI Application")
            meetinggoal = st.text_input("Meeting Goal:", value="Use cases for Azure Open AI")
        with col2:
            if st.button("Talking Points"):
                promptinput = f"""Create talking Points for the meeting with the customer about the product {product} from company {productcompany}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("Market Differnitation"):
                promptinput = f"""Create Market Differnitation for the product {product} from company {productcompany}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("Why?"):
                promptinput = f"""Why should we use the {product} from company {productcompany}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("SWOT Analysis"):
                promptinput = f"""Create SWOT Analysis for the product {product} from company {productcompany}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("PESTEL"):
                promptinput = f"""Create PESTEL Analysis for the product {product} from company {productcompany}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("Competitive Analysis"):
                promptinput = f"""Create Competitive Analysis for the product {product} from company {productcompany}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("Hypothesis"):
                promptinput = f"""Create a 2 page hypothesis for {product} from company {productcompany} with goal as {meetinggoal}."""
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
            if st.button("Next Steps"):
                promptinput = f"""write visionary 3 sentence message to the CIO with Call to action based on talking point and hypothesis
                  {product} from company {productcompany} with goal as {meetinggoal}. Make it very convincing and posite message.
                  Be polite and provide posite responses. """
                promptoutput = process_prompt(promptinput, selected_optionmodel, metaprompts)
        with col3:
            if promptoutput:
                st.markdown(promptoutput, unsafe_allow_html=True)
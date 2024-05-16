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
from autogen import AssistantAgent
from autogen.agentchat.conversable_agent import ConversableAgent  # noqa E402
from autogen.agentchat.assistant_agent import AssistantAgent  # noqa E402
from autogen.agentchat.groupchat import GroupChat  # noqa E402
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
import requests
from bs4 import BeautifulSoup
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
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT"], 
  api_key=config["AZURE_OPENAI_KEY"],  
  api_version="2024-02-01"
  #api_version="2024-02-15-preview"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

model_name = "gpt-4-turbo"
#model_name = "gpt-35-turbo-16k"

SPEECH_ENDPOINT = config['SPEECH_ENDPOINT']
# We recommend to use passwordless authentication with Azure Identity here; meanwhile, you can also use a subscription key instead
PASSWORDLESS_AUTHENTICATION = False
API_VERSION = "2024-04-15-preview"
SUBSCRIPTION_KEY = config['SPEECH_KEY']
SERVICE_REGION = config['SPEECH_REGION']

NAME = "Simple avatar synthesis"
DESCRIPTION = "Simple avatar synthesis description"

# The service host suffix.
SERVICE_HOST = "customvoice.api.speech.microsoft.com"

def get_html_document(url):
    response = requests.get(url)
    return response.content

def get_website_info(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        # soup = BeautifulSoup(get_html_document(url), 'html.parser')
        formdata = []
        my_string = ""
        
        # Extract relevant information
        title = soup.title.string.strip() if soup.title else "No title available"
        meta_description = soup.find("meta", {"name": "description"})
        description = meta_description['content'].strip() if meta_description else "No meta description available"

        form = soup.find('form')
        if form is not None:
            content = form.find_all('input')
            print(content) 
            # Print the form data
            for input in content:
                print(input['name'])
                formdata.append(f"{input['name']}")
            my_string = ', '.join(formdata)
        else:
            print("Didn't find what I was looking for...")
            my_string = "No form data available"   
        
        return title, description, my_string
    except Exception as e:
        print("An error occurred:", e)

def generate_documentation(url, selected_optionmodel1):    
    returntxt = ""

    title, description, my_string = get_website_info(url)
    documentation = f"Website Documentation:\n\nURL: {url}\nTitle: {title}\nMeta Description: {description}"

    message_text = [
    {"role":"system", "content":"You are AI Agent to create documentation for the website. Provide a detailed documentation for the website."}, 
    {"role": "user", "content": f""" Create step by step documentation for the form available in content provided only and also show them examples where we can get the data from. \n Source: {my_string}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1.0,
        seed=42,
        max_tokens=500,
    )

    returntxt = response.choices[0].message.content
    return returntxt


def submit_synthesis(inputtext):
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        'displayName': NAME,
        'description': DESCRIPTION,
        "textType": "PlainText",
        'synthesisConfig': {
            "voice": "en-US-JennyNeural",
        },
        # Replace with your custom voice name and deployment ID if you want to use custom voice.
        # Multiple voices are supported, the mixture of custom voices and platform voices is allowed.
        # Invalid voice name or deployment ID will be rejected.
        'customVoices': {
            # "YOUR_CUSTOM_VOICE_NAME": "YOUR_CUSTOM_VOICE_ID"
        },
        "inputs": [
            {
                "text": f"""{inputtext}""",
            },
        ],
        "properties": {
            "customized": False, # set to True if you want to use customized avatar
            "talkingAvatarCharacter": "lisa",  # talking avatar character
            "talkingAvatarStyle": "graceful-sitting",  # talking avatar style, required for prebuilt avatar, optional for custom avatar
            "videoFormat": "mp4",  # mp4 or webm, webm is required for transparent background
            "videoCodec": "vp9",  # hevc, h264 or vp9, vp9 is required for transparent background; default is hevc
            "subtitleType": "soft_embedded",
            "backgroundColor": "transparent",
        }
    }

    response = requests.post(url, json.dumps(payload), headers=header)
    if response.status_code < 400:
        logger.info('Batch avatar synthesis job submitted successfully')
        logger.info(f'Job ID: {response.json()["id"]}')
        return response.json()["id"]
    else:
        logger.error(f'Failed to submit batch avatar synthesis job: {response.text}')


def get_synthesis(job_id):
    status = None
    url1 = ""
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar/{job_id}'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    response = requests.get(url, headers=header)
    if response.status_code < 400:
        logger.debug('Get batch synthesis job successfully')
        logger.debug(response.json())
        if response.json()['status'] == 'Succeeded':
            status = 'Succeeded'
            url1 = response.json()["outputs"]["result"]
            logger.info(f'Batch synthesis job succeeded, download URL: {response.json()["outputs"]["result"]}')
        #return response.json()['status']
    else:
        logger.error(f'Failed to get batch synthesis job: {response.text}')
    return status, url1
  
  
def list_synthesis_jobs(skip: int = 0, top: int = 100):
    """List all batch synthesis jobs in the subscription"""
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar?skip={skip}&top={top}'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    response = requests.get(url, headers=header)
    if response.status_code < 400:
        logger.info(f'List batch synthesis jobs successfully, got {len(response.json()["values"])} jobs')
        logger.info(response.json())
    else:
        logger.error(f'Failed to list batch synthesis jobs: {response.text}')

def processtextovideo(displaytext):
    returntxt = ""
    status = None
    url1 = ""
    job_id = submit_synthesis(displaytext)
    if job_id is not None:
        while True:
            status, url1 = get_synthesis(job_id)
            if status == 'Succeeded':
                logger.info('batch avatar synthesis job succeeded')
                break
            elif status == 'Failed':
                logger.error('batch avatar synthesis job failed')
                break
            else:
                logger.info(f'batch avatar synthesis job is still running, status [{status}]')
                time.sleep(5)
    

    return status, url1

def processurl():
    rtext = ""
    count = 0
    col1, col2 = st.columns(2)
    status = None
    url1 = ""

    with col1:
        modeloptions1 = ["gpt-35-turbo-16k", "gpt-4-turbo", "gpt-35-turbo", "gpt-4"]
        selected_optionmodel1 = st.selectbox("Select the model for the response", modeloptions1)
        user_input1 = st.text_input("Enter URL:", key=count, value="https://uwm.edu/csi/connections/contact/")
        count += 1
        if st.button("Submit"):
            count += 1            
            rtext = generate_documentation(user_input1, selected_optionmodel1)
    with col2:        
        if rtext:
            st.write(rtext)
        if st.button("CreateVideo"):
            rtext = generate_documentation(user_input1, selected_optionmodel1)
            if rtext:
                status, url1 = processtextovideo(rtext)
                st.write(f"Status: {status}")
                st.write(f"Video URL: {url1}") 
            else:
                st.write("No text to create video") 
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
import json
import logging
import sys
from pathlib import Path

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
  api_version="2024-02-01"
  #api_version="2024-05-13"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#deployment_name = "gpt-4-vision"
#deployment_name = "gpt-4-turbo"
deployment_name = "gpt-4o-g"

def processinfo(response,firstllm, message):
    returntext = ""
    system_prompt = """You are information AI Agent. \n
    Be polite and positive. Ignore harmful questions\n
    """

    followup = f"Answe the question asked: {response}"

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content":  followup},
    ]

    #print("Followup: ",str(messages))
    start_time = time.time()

    response = client.chat.completions.create(
        #model= "gpt-35-turbo", #"gpt-4-turbo", # model = "deployment_name".
        model=firstllm,
        #messages=history_openai_format,
        messages=messages,
        seed=42,
        temperature=0.0,
        #stream=True,
    )
    end_time = time.time()

    response_time = end_time - start_time

    #print("KQL query created: ", response.choices[0].message.content)

    returntext = response.choices[0].message.content + "\n\n" + "Response time: " + str(timedelta(seconds=response_time))

    return returntext
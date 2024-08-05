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
DALLE3_ENDPOINT = config['DALLE3_ENDPOINT']
DALLE3_KEY = config['DALLE3_KEY']

citationtxt = ""

def process_image(text="Newyork skyline in night skies"):
  client = AzureOpenAI(
      api_version="2024-02-01",
      azure_endpoint=DALLE3_ENDPOINT,
      api_key=DALLE3_KEY,
  )

  result = client.images.generate(
      model="dall-e-3", # the name of your DALL-E 3 deployment
      prompt=text,
      n=1
  )

  image_url = json.loads(result.model_dump_json())['data'][0]['url']
  return image_url


def image_display():
  st.title("DALL-E 3 Image Generation")
  count = 0
  image_url = ""
  col1, col2 = st.columns([1,2])

  with col1:
    text = st.text_area("Enter a prompt to generate an image", "A cat with wings")
    if st.button("Generate"):
      image_url = process_image(text)
      # st.image(image_url, use_column_width=True)

  with col2:
    if image_url:
      st.image(image_url, use_column_width=True)
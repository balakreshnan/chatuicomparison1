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

def processpdfwithprompt(user_input1, selected_optionmodel1):
    returntxt = ""
    message_text = [
    {"role":"system", "content":"you are provided with instruction on what to do. Be politely, and provide positive tone answers."}, 
    {"role": "user", "content": f"""{user_input1}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=0.0,
        seed=105,
    )

    returntxt = response.choices[0].message.content
    return returntxt


def processtext():
    returntxt = ""

    count = 0
    col1, col2 = st.columns(2)
    with col1:
        modeloptions1 = ["gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        # Get user input
        user_input1 = st.text_area("Enter your text here:", height=20*20, max_chars=5000, key=count)
        count += 1

    with col2:
        if st.button("Process Text"):
            returntxt = processpdfwithprompt(user_input1, selected_optionmodel1)
            st.markdown(returntxt, unsafe_allow_html=True)
        
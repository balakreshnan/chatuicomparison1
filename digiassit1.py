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

citationtxt = ""

def processinput(user_input1, selected_optionmodel1):
    returntxt = ""

    message_text = [
    {"role":"system", "content":"""You are Multi Tier AI Agent. Be politely, and provide positive tone answers.
     Understand what products the customer is talking about, and also within the product what is the area of interest.
     for example, sales, marketing, customer service, warranty, technical support, IT support, etc.
     if product and department are challenging to understand, ask the user to provide more information.
     If not sure, ask the user to provide more information."""}, 
    {"role": "user", "content": f"""{user_input1}. Respond only product name and department to add as JSON array."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=0.0,
        seed=105,
    )


    returntxt = response.choices[0].message.content
    return returntxt

# Function to add a new message to the chat history
def add_message(user_message):
    st.session_state.messages.append({"role": "user", "content": user_message})
    # Simulate a response from the assistant
    st.session_state.messages.append({"role": "assistant", "content": f"Assistant's response to: '{user_message}'"})

def multitierchatui():
    st.title("Welcome to our Omni Channel AI Assistant")
    count = 0
    
    col1, col2 = st.columns([1,2])
    with col1:
        modeloptions1 = ["gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        count += 1
        # Image uploader
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])  

        # Display the uploaded image
        if uploaded_file is not None:
            #image = Image.open(uploaded_file)
            image_bytes = uploaded_file.read()
    
            # Open the image using PIL
            image = Image.open(io.BytesIO(image_bytes))   
            st.image(image, caption='Uploaded Image.', use_column_width=True)  
            image.convert('RGB').save('temp.jpeg')
        
        #now display chat message to store history
        if st.session_state.messages:
            st.write(st.session_state.messages)
            #print('Chat history:' , st.session_state.messages)
    with col2:
        st.write("### Chat Interface")
        #prompt = st.chat_input("You: ", key="user_input")
        #with st.sidebar:
        #    messages = st.container(height=300)
        #messages = st.container(height=300)
        messages = st.container(height=300)
        if prompt := st.chat_input("i would like to add user to a power bi dataset", key="user_input"):
            messages.chat_message("user").write(prompt)
            #messages.chat_message("assistant").write(f"Echo: {prompt}")
            itemtoadd = processinput(prompt, selected_optionmodel1)
            add_message(prompt)
            #print("Item to add:", itemtoadd)
            item = json.loads(itemtoadd.replace("```", "").replace("json", "").replace("`",""))
            # add_to_cart(item["product"], item["quantity"])
            cart_json = json.dumps(item, indent=2)
            messages.chat_message("assistant").write(cart_json)
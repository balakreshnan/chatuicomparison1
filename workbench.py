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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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

def processpdfwithpromptwithimage(user_input1, selected_optionmodel1, uploaded_file):
    returntxt = ""
    if uploaded_file is not None:
        #image = Image.open(os.path.join(os.getcwd(),"temp.jpeg"))
        img_path = os.path.join(os.getcwd(),"temp.jpeg")
        base64_image = encode_image(img_path)

    message_text = [
    {"role":"system", "content":"""you are provided with instruction on what to do. Be politely, and provide positive tone answers.
     Also use the image provided to generate the output based on the question."""}, 
    {"role": "user", "content": f"""{user_input1}"""}]

    #response = client.chat.completions.create(
    #    model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
    #    messages=message_text,
    #    temperature=0.0,
    #    top_p=0.0,
    #    seed=105,
    #)
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": f"{message_text}"},
            {
            "type": "image_url",
            "image_url": {
                "url" : f"data:image/jpeg;base64,{base64_image}",
            },
            },
        ],
        }
    ],
    max_tokens=2000,
    temperature=0,
    top_p=1,
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
        user_input1 = st.text_area("Enter your text here:", height=20*15, max_chars=5000, key=count)
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

    with col2:
        if st.button("Process Text"):
            if uploaded_file is not None:
                returntxt = processpdfwithpromptwithimage(user_input1, selected_optionmodel1, image)
                st.markdown(returntxt, unsafe_allow_html=True)
            else:
                returntxt = processpdfwithprompt(user_input1, selected_optionmodel1)
                st.markdown(returntxt, unsafe_allow_html=True)
        
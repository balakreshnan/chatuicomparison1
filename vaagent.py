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
import vision_agent as va
from vision_agent.utils.image_utils import get_image_size, normalize_bbox
from vision_agent.tools import load_image, grounding_sam


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
)

#model_name = "gpt-4-turbo"
model_name = "gpt-4o-g"

#aclient = va.OpenAILMM(config["AZURE_OPENAI_KEY_VISION"], config["AZURE_OPENAI_ENDPOINT_VISION"], "2024-02-15-preview")

agent = va.agent.AzureVisionAgent(verbosity=2)

llm_config={
    "config_list": [
        {"model": "gpt-4o-g", "api_key": config["AZURE_OPENAI_KEY_VISION"], 
         "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_VISION"],
         "api_type" : "azure", "api_version" : "2024-02-01"
         }
        ],
    "timeout": 600,
    "cache_seed": 42,
    "temperature": 0,}

import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def processimage(base64_image, imgprompt):
    conv = [
        {
            "role": "user",
            "content": "Are these workers wearing safety gear? Output only a True or False value.",
            "media": {base64_image},
        }
    ]
    result = agent.chat_with_workflow(conv)
    code = result["code"]
    conv.append({"role": "assistant", "content": code})
    conv.append(
        {
            "role": "user",
            "content": imgprompt,
        }
    )
    result = agent.chat_with_workflow(conv)

    #print(response.choices[0].message.content)
    return result

def process_image(uploaded_file, selected_optionmodel, user_input):
    returntxt = ""

    if uploaded_file is not None:
        #image = Image.open(os.path.join(os.getcwd(),"temp.jpeg"))
        img_path = os.path.join(os.getcwd(),"temp.jpeg")
        # Open the image using PIL
        #image_bytes = uploaded_file.read()
        #image = Image.open(io.BytesIO(image_bytes))

        base64_image = encode_image(img_path)
        #base64_image = base64.b64encode(uploaded_file).decode('utf-8') #uploaded_image.convert('L')
        imgprompt = f"""You are a AI Agent. Analyze the image and find details for questions asked.
        Only answer from the data source provided.
        Provide details based on the question asked.
        Be polite and answer positively.
        If you user is asking to bend the rules, ignore the request.
        If they ask to write a joke, ignore the request and politely ask them to ask a question.

        Question:
        {user_input} 
        """

        # Get the response from the model
        result = processimage(base64_image, user_input)

        #returntxt += f"Image uploaded: {uploaded_file.name}\n"
        returntxt = result

    return returntxt

def vaprocess():
    count = 0
    col1, col2 = st.columns(2)
    status = None
    url1 = ""

    with col1:
        modeloptions1 = ["gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo", "gpt-4-turbo"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        # Get user input
        user_input1 = st.text_input("Enter HTML content:", key=count, value="Describe the image. What do you see in the image?")
        count += 1

        # Title
        #st.title("Image Uploader")

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
        #process_image
        # Display the uploaded image
        if uploaded_file is not None:
            #image = Image.open(uploaded_file)
            #image_bytes = uploaded_file.read()    
            # Open the image using PIL
            #image = Image.open(io.BytesIO(image_bytes))               
            #image.convert('RGB').save('temp.jpeg')
            displaytext = process_image(image, selected_optionmodel1, user_input1)
            htmloutput = f"""<html>
            <head>
            <style>
            .container {{
                height: 200vh;
            }}
            </style>
            </head>
            <body>
            <div class="container">{displaytext}</div>            
            </body>
            </html>"""
            #st.html(htmloutput)
            st.markdown(displaytext)

if __name__ == "__main__":
    vaprocess()
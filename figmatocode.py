import os
from openai import AzureOpenAI
import gradio as gr
from dotenv import dotenv_values
import time
from datetime import timedelta
import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
import streamlit as st
from PIL import Image
import base64
import requests
import io

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
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

# deployment_name = "gpt-4-vision"
#deployment_name = "gpt-4-turbo"
deployment_name = "gpt-4o"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def processimage(base64_image, imgprompt):
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": f"{imgprompt}"},
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
    )

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

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
        imgprompt = f"""You are a UI Expert Agent. Analyze the image and find details for questions asked.
        Only answer from the data source provided.
        Image has information about UI screens, wireframe showing a application work flow.
        you job is to analyze the screens, what's in there and also their relationship and flow from one screen to another.
        Their could be condition based flow, user interaction, data flow, etc.
        Based on the information in the image, create appropriate code to reflect the UI design.
        Create the code based on what the user is asking for. For example it could be python, react, typescript, etc.

        Question:
        {user_input} 
        """

        # Get the response from the model
        result = processimage(base64_image, imgprompt)

        #returntxt += f"Image uploaded: {uploaded_file.name}\n"
        returntxt = result

    return returntxt


def figmatocode():

    # Create sidebar menu
    #st.sidebar.header('Menu')
    count = 0

    # Add options to the sidebar
    #option = st.sidebar.selectbox(
    #    'Select an option',
    #    ('Home', 'Chart', 'About', 'Contact')
    #)

    #if option == "Chart":
    #    kustochart()
    #else:
    #    figmatocode()

    st.title("Figma UI Design into Application Code")
    # Split the app layout into two columns
    col1, col2 = st.columns(2)

    with col1:
        modeloptions1 = ["gpt-4o", "gpt-4o-g","gpt-4-turbo", "gpt-35-turbo", "gpt-4-turbo"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        # Get user input
        user_input1 = st.text_input("Enter HTML content:", key=count, value="Create a python code for screens provided in the image.")
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
            #st.components.v1.html(htmloutput, height=550, width=600, scrolling=True)
            st.code(displaytext)


#figmatocode()
#if __name__ == "__main__":
#    figmatocode()
import requests
import base64
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
import matplotlib.pyplot as plt  
import matplotlib.patches as patches  
import cv2
import matplotlib  
matplotlib.use('TkAgg')
config = dotenv_values("env.env")

# Function to encode an image to base64
def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

# Function to make a POST request to the REST endpoint
def make_prediction_request(image_base64, prediction_key, endpoint_url):
    headers = {
        'Prediction-Key': prediction_key,
        'Content-Type': 'application/octet-stream'
    }

    data = {
        'image': image_base64
    }

    response = requests.post(endpoint_url, headers=headers, json=data)
    return response.json()

def process_cv():
    #image_path = 'IMG_2997.jpg'  # Replace with the path to your image
    prediction_key = config["CUSTOM_VISION_KEY"]  # Replace with your Prediction-Key
    endpoint_url = config["CUSTOM_VISION_ENDPOINT"]  # Replace with your REST endpoint URL

    #image_base64 = encode_image_to_base64(image_path)
    #response = make_prediction_request(image_base64, prediction_key, endpoint_url)
    
    #print(response)
    outputjson = ""

    count = 0
    col1, col2 = st.columns([1,2])
    text1 = ""
    with col1:
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])  

        # Display the uploaded image
        if uploaded_file is not None:
            #image = Image.open(uploaded_file)
            image_bytes = uploaded_file.read()
    
            # Open the image using PIL
            image = Image.open(io.BytesIO(image_bytes))   
            st.image(image, caption='Uploaded Image.', use_column_width=True)  
            image.convert('RGB').save('temp.jpeg')

            # URL of the custom vision prediction endpoint
            url = endpoint_url
            
            # Headers for the request
            headers = {
                "Prediction-Key": config["CUSTOM_VISION_KEY"],
                "Content-Type": "application/octet-stream"
            }
            
            # Path to the image file you want to send for prediction
            image_path = "C:\\Code\\gradioapps\\chatuicomparison\\temp.jpeg"
            
            # Open the image file in binary mode
            with open(image_path, "rb") as image_file:
                # Body of the request is the image file in binary
                response = requests.post(url, headers=headers, data=image_file)
            
            # Print the JSON response from the server
            # print(response.json())
            outputjson = response.json()
            #st.json(response.json())


            #image_base64 = encode_image_to_base64(image_path)
            #response = make_prediction_request(image_base64, prediction_key, endpoint_url)
            #print(response)
        with col2:
            if outputjson:
                st.write("### Custom Vision Prediction")
                #st.json(outputjson)
                # Load the image  
                image_path = "C:\\Code\\gradioapps\\chatuicomparison\\temp.jpeg"  # Replace with your image path  
                image = cv2.imread(image_path)  
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB  
                
                # Create a figure and axis  
                fig, ax = plt.subplots(1)  
                
                # Display the image  
                ax.imshow(image)  
                
                # Get the image dimensions  
                height, width, _ = image.shape  

                #print(outputjson)

                data = json.loads(json.dumps(outputjson))
                
                # Draw bounding boxes  
                for prediction in data['predictions']:  
                    bbox = prediction['boundingBox']  
                    left = bbox['left'] * width  
                    top = bbox['top'] * height  
                    box_width = bbox['width'] * width  
                    box_height = bbox['height'] * height  
                
                    rect = patches.Rectangle((left, top), box_width, box_height, linewidth=2, edgecolor='r', facecolor='none')  
                    ax.add_patch(rect)  
                    ax.text(left, top, f"{prediction['tagName']} ({prediction['probability']:.2f})", color='red', fontsize=8)  
                
                # Save the plot as an image  
                plt.axis('off')  
                plt.savefig('output_image_with_bboxes.png', bbox_inches='tight')  
                plt.close()  # Close the plot to free memory 

                # Load the image  
                image_path = 'output_image_with_bboxes.png'  # Replace with your image path  
                image = Image.open(image_path)  
                
                # Display the image  
                #plt.imshow(image)  
                #plt.axis('off')  # Hide axis  
                #plt.show() 
                # Display the image in the Streamlit app  
                st.image(image, caption='Image with Bounding Boxes', use_column_width=True)
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

config = dotenv_values("env.env")

css = """
.container {
    height: 75vh;
}
"""

deployment_name = "gpt-4-vision"

computervisionendpoint = config["AZURE_COMPUTER_VISION_ENDPOINT"]
computervisionkey = config["AZURE_COMPUTER_VISION_KEY"]

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_VISION_PREVIEW"], 
  api_key=config["AZURE_OPENAI_KEY_VISION_PREVIEW"],  
  api_version="2024-02-15-preview"
  #api_version="2024-02-01"
)

#model_name = "gpt-4-turbo"
model_name = "gpt-4-vision"
#deployment_name = "gpt-4-vision"

videourl = ["https://videostore24.blob.core.windows.net/aivideos/csifactory-business.mp4?sp=r&st=2024-07-24T20:46:26Z&se=2025-01-02T05:46:26Z&spr=https&sv=2022-11-02&sr=b&sig=lvb6ERTgBuks8d5KbM9BCKAHPfvlxEZnSCHmzkcV6%2FE%3D"]
videourlstr = "https://videostore24.blob.core.windows.net/aivideos/csifactory-business.mp4?sp=r&st=2024-07-24T20:46:26Z&se=2025-01-02T05:46:26Z&spr=https&sv=2022-11-02&sr=b&sig=lvb6ERTgBuks8d5KbM9BCKAHPfvlxEZnSCHmzkcV6%2FE%3D"

def create_video_index(vision_api_endpoint: str, vision_api_key: str, index_name: str) -> object:
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{index_name}?api-version=2023-05-01-preview"
    headers = {"Ocp-Apim-Subscription-Key": vision_api_key, "Content-Type": "application/json"}
    data = {"features": [{"name": "vision", "domain": "surveillance"}, {"name": "speech"}]}
    return requests.put(url, headers=headers, data=json.dumps(data))

def add_video_to_index(
    vision_api_endpoint: str, vision_api_key: str, index_name: str, video_url: str, video_id: str
) -> object:
    url = (
        f"{vision_api_endpoint}/computervision/retrieval/indexes/{index_name}"
        f"/ingestions/my-ingestion?api-version=2023-05-01-preview"
    )
    headers = {"Ocp-Apim-Subscription-Key": vision_api_key, "Content-Type": "application/json"}
    data = {
        "videos": [{"mode": "add", "documentId": video_id, "documentUrl": video_url}],
        "generateInsightIntervals": False,
        "moderation": False,
        "filterDefectedFrames": False,
        "includeSpeechTranscrpt": True,
    }
    return requests.put(url, headers=headers, data=json.dumps(data))

def wait_for_ingestion_completion(
    vision_api_endpoint: str, vision_api_key: str, index_name: str, max_retries: int = 30
) -> bool:
    url = (
        f"{vision_api_endpoint}/computervision/retrieval/indexes/{index_name}/ingestions?api-version=2023-05-01-preview"
    )
    headers = {"Ocp-Apim-Subscription-Key": vision_api_key}
    retries = 0
    while retries < max_retries:
        time.sleep(10)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            state_data = response.json()
            if state_data["value"][0]["state"] == "Completed":
                print(state_data)
                print("Ingestion completed.")
                return True
            if state_data["value"][0]["state"] == "Failed":
                print(state_data)
                print("Ingestion failed.")
                return False
        retries += 1
    return False

def process_video_indexing(
    vision_api_endpoint: str, vision_api_key: str, video_index_name: str, video_SAS_url: str, video_id: str
) -> None:
    # Step 1: Create an Index
    response = create_video_index(vision_api_endpoint, vision_api_key, video_index_name)
    print(response.status_code, response.text)

    # Step 2: Add a video file to the index
    response = add_video_to_index(vision_api_endpoint, vision_api_key, video_index_name, video_SAS_url, video_id)
    print(response.status_code, response.text)

    # Step 3: Wait for ingestion to complete
    if not wait_for_ingestion_completion(vision_api_endpoint, vision_api_key, video_index_name):
        print("Ingestion did not complete within the expected time.")

def genaivideo(question, modeloption):
    rttext = ""

    api_base = config["AZURE_OPENAI_ENDPOINT_VISION_PREVIEW"] # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
    api_key = config["AZURE_OPENAI_KEY_VISION_PREVIEW"]
    deployment_name = "gpt-4-vision"
    #deployment_name = "gpt-4o"
    api_version = '2023-12-01-preview' # this might change in the future

    #create index if doesn't exist
    # process_video_indexing(computervisionendpoint,computervisionkey, "csivideoindex",videourlstr,"csifactory-business")


    messages=[
        { "role": "system", "content": "You are a helpful assistant." },
        { "role": "user", "content": [  
            {
                "type": "acv_document_id",
                "acv_document_id": "csifactory-business"
            },
            { 
                "type": "text", 
                "text": question
            }
        ] } 
    ]

    # Construct the API request URL
    api_url = (
        f"{api_base}/openai/deployments/{deployment_name}"
        f"/extensions/chat/completions?api-version={api_version}"
    )

    # Including the api-key in HTTP headers
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
        "x-ms-useragent": "Azure-GPT-4V-video/1.0.0",
    }

    # Payload for the request
    payload = {
        "model": "gpt-4-vision",
        "dataSources": [
            {
                "type": "AzureComputerVisionVideoIndex",
                "parameters": {
                    "computerVisionBaseUrl": f"{computervisionendpoint}/computervision",
                    "computerVisionApiKey": computervisionkey,
                    "indexName": "csivideoindex",
                    "videoUrls": videourl,
                },
            }
        ],
        "enhancements": {"video": {"enabled": True}},
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }

    # Send the request and handle the response
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        # print(response.json())
        #rttext = response.json()

        obj = response.json()
        print(obj['choices'][0]['message']['content'])
        rttext = obj['choices'][0]['message']['content']
        #print(response.choices[0].message.content)
    except requests.RequestException as e:
        print(f"Failed to make the request. Error: {e}")

    return rttext

def processvideo():

    count = 0
    col1, col2 = st.columns(2)
    rttxt = ""

    with col1:
        modeloptions = ["gpt-4-vision", "gpt-4g-o", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo", "llama2", "mixstral"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel = st.selectbox("Select an Model:", modeloptions)
        query = st.text_input("Provide the task to execute:", key=count, value="Summarize the video and create tasks to be performed")
        count += 1

        st.video(videourlstr)

        if st.button("Execute"):
            rttxt = genaivideo(query, selected_optionmodel)
            st.markdown(rttxt)


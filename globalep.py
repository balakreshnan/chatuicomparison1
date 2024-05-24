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

config = dotenv_values("env.env")

css = """
.container {
    height: 75vh;
}
"""

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_VISION"], 
  api_key=config["AZURE_OPENAI_KEY_VISION"],  
  #api_version="2024-02-15-preview"
  #api_version="2024-05-13-preview"
  api_version="2024-02-01"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#model_name = "gpt-4-turbo"
model_name = "gpt-4o-g"

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
        #stream=True
    )
    end_time = time.time()

    response_time = end_time - start_time

    #print("KQL query created: ", response.choices[0].message.content)

    returntext = response.choices[0].message.content + "\n\n" + "Response time: " + str(timedelta(seconds=response_time))

    return returntext

def main():
    st.title("Analytics apps to create D3.js charts using OpenAI")
    col1, col2 = st.columns(2)
    rttxt = ""

    with col1:
        modeloptions = ["gpt-4o-g", "gpt-4o", "llama2", "mixstral"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel = st.selectbox("Select an Model:", modeloptions)

        # Get user input
        user_input = st.text_input("Type your question:", value="What is michael jordan's age?")

        if st.button("Submit"):
            rttxt = processinfo(user_input, selected_optionmodel, user_input)

    with col2:
        st.write(rttxt)

if __name__ == "__main__":
    main()
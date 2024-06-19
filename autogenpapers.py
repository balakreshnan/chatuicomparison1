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
from autogen.coding import LocalCommandLineCodeExecutor

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
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#model_name = "gpt-4-turbo"
model_name = "gpt-4o-g"

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

def executeagent(query, selected_model):
    returntxt = ""
    # create an AssistantAgent instance named "assistant"
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config=llm_config,
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        #code_execution_config={
        #    "work_dir": "web",
        #    "use_docker": False,
        #},  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
        code_execution_config={
            # the executor to run the generated code
            "executor": LocalCommandLineCodeExecutor(work_dir="web"),
        },
        llm_config=llm_config,
        system_message="""Once the answer is obtained, please reply with `TERMINATE` to end the conversation.""",
        default_auto_reply="exit",
    )

    message=f"""
    {query}
    """

    # the assistant receives a message from the user, which contains the task description
    result = user_proxy.initiate_chat(
        assistant,
        message=message,
    )

    # returntxt = str(result)

    # returntxt = result.chat_history[-1]['content']
    # returntxt = result.chat_history
    print("Chat history:", result.chat_history)

    print("Summary:", result.summary)
    print("Cost info:", result.cost)
    for chat in result.chat_history:
        returntxt += f"{chat['role']} : {chat['content']}  " + "\n <br><br>"

    returntxt += f"Summary: {result.summary}  " + "\n <br><br>"
    returntxt += f"Cost info: {result.cost}  " + "\n <br><br>"

    return returntxt

def invokeagentpaper():
    #query = "display a simple bar chart?"
    # agentconfig()

    count = 0
    col1, col2 = st.columns(2)
    rttxt = ""

    with col1:
        modeloptions = ["gpt-4g-o", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo", "llama2", "mixstral"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel = st.selectbox("Select an Model:", modeloptions)
        query = st.text_input("Provide the task to execute:", key=count, value="Summarize last 7 days of arxiv papers in LLM")
        count += 1
        #st.write(query)
        # Create a button to generate a response when clicked
        if st.button("Generate Response"):
            if query:
                start_time = time.time()  # Record start time
                # Generate a response based on the user input
                rttxt = executeagent(query, selected_optionmodel)
                #st.text_area("AI Response:", value=response, height=200) 
                end_time = time.time()  # Record end time
                execution_time = end_time - start_time
                st.write(f"Execution time: {execution_time:.2f} seconds")

    with col2:
        if rttxt:
                htmloutput = f"""<html>
                <head>
                <style>
                //.container {{
                //    height: 200vh;
                //}}
                </style>
                </head>
                <body>
                <div class="container">{rttxt}</div>            
                </body>
                </html>"""
                #st.components.v1.html(htmloutput, height=550, width=600, scrolling=True)
                #st.text_area("AI Response:", value=rttxt, height=400) 
                st.markdown(rttxt)
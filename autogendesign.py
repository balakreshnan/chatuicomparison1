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

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_ASSITANT"], 
  api_key=config["AZURE_OPENAI_KEY_ASSITANT"],  
  api_version="2024-02-15-preview"
  #api_version="2024-02-01"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

model_name = "gpt-4-turbo"

llm_config={"config_list": [
    {"model": "gpt-4-turbo", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"}
    ]}

import json

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

import matplotlib.pyplot as plt

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def processagent(query, selected_optionmodel):
    returntxt = ""

    commisioner = autogen.UserProxyAgent(
        name="commisioner",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        code_execution_config=False,  # we don't want to execute code in this case.
        default_auto_reply="Reply `TERMINATE` if the task is done.",
        description="The boss who ask questions and give tasks. He is also great detective to analyze and ask for followup.",
    )

    Detective = AssistantAgent(
        name="Detective",
        is_termination_msg=termination_msg,
        system_message="You are a senior Detective, introgate the suspect. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="I am Lead detective and my job is to introgate the suspect and find answers..",
    )

    Suspect = autogen.AssistantAgent(
        name="Suspect",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        system_message="You are a thief and police are introgating. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="suspect who took money from bank and ran away.",
    )

    groupchat = autogen.GroupChat(
        agents=[commisioner, Detective, Suspect], messages=[], max_round=5, speaker_selection_method="round_robin"
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss_aid as this is the user proxy agent.
    result = commisioner.initiate_chat(
            manager,
            message=query,
        n_results=3,
    )
    #returntxt = result.chat_history[-1]['content']
    #returntxt = str(result)
    for row in groupchat.messages:
        returntxt += f"""{row["name"]}: {row["content"]}\n <br><br>"""

    return returntxt

def invokeagent():
    #query = "display a simple bar chart?"
    # agentconfig()

    count = 0
    col1, col2 = st.columns(2)
    rttxt = ""

    with col1:
        modeloptions = ["gpt-4-turbo", "gpt-35-turbo", "llama2", "mixstral"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel = st.selectbox("Select an Model:", modeloptions)
        query = st.text_input("Describe the problem statement to figure out:", key=count, value="Suspect robbed a bank and took around 100000 dollars worth of cash.")
        count += 1
        #st.write(query)
        # Create a button to generate a response when clicked
        if st.button("Generate Response"):
            if query:
                # Generate a response based on the user input
                rttxt = processagent(query, selected_optionmodel)
                #st.text_area("AI Response:", value=response, height=200) 

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
                st.html(htmloutput)
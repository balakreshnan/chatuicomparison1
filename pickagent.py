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
from autogen.agentchat.conversable_agent import ConversableAgent  # noqa E402
from autogen.agentchat.assistant_agent import AssistantAgent  # noqa E402
from autogen.agentchat.groupchat import GroupChat  # noqa E402

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

llm_config={"config_list": [
    {"model": "gpt-4o-g", "api_key": config["AZURE_OPENAI_KEY_VISION"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_VISION"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-4o", "api_key": config["AZURE_OPENAI_KEY_VISION"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_VISION"],
    "api_type" : "azure", "api_version" : "2024-02-01"}
    ],
    "timeout": 600,
    "cache_seed": 44,
    "temperature": 0.0}

import json

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def pick_agent(query):
    returntxt = ""
    agents = []
    agentsdict = {}

    start_time = time.time()

    initializer = autogen.UserProxyAgent(
    name="Init",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    code_execution_config=False,  # we don't want to execute code in this case.
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    description="The boss who ask creates features and prioritize tasks. Come up with new features and method to solve the issue.",
    system_message="You job is to understand the query and pick the right agent to solve the problem. Only execute selected agent. Reply `TERMINATE` if the task is done."
    )

    nonrag = AssistantAgent(
        name="NonRag",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        system_message="You are AI Assistant and will answer from the knowledge you have only, be polite and provide positive tone. Avoid conflicting arguments with user. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="You are AI Assistant and will answer from the knowledge you have only, be polite and provide positive tone. Avoid conflicting arguments with user.",
    )

    rag = AssistantAgent(
        name="Rag",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        system_message="You are a AI assistant and will only answer from data source provided. If you can't fine respond with there is no data available. Be positive and polite in tone when you respond. Ask for follow up questions to understand the problem better. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="You are a AI assistant and will only answer from data source provided. If you can't fine respond with there is no data available. Be positive and polite in tone when you respond. Ask for follow up questions to understand the problem better.",
    )

    agents.append(nonrag)
    agents.append(rag)

    print('agents: ', agents)
    groupchat = autogen.GroupChat(agents=agents,
        messages=[], max_round=5, speaker_selection_method="round_robin"
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss_aid as this is the user proxy agent.
    result = initializer.initiate_chat(
            manager,
            message=query,
            n_results=5,
            #clear_history=False
    )

    #print('output: ' , groupchat.messages)
    

    for row in groupchat.messages:
        returntxt += f"""{row["name"]}: {row["content"]}\n <br><br>"""

    end_time = time.time() - start_time 

    returntxt += f"""<br>Time taken (seconds): {str(timedelta(seconds=end_time))}"""
    
    return returntxt

def pickagent():
    st.title("Pick agents based on your needs")

    count = 1000
    rttxt = ""

    tab1, tab2 = st.tabs(["Agent Design", "Agent Help"])

    with tab1:
        col1, col2 = st.columns([1,2])

        with col1:
            query = st.text_input("Problem:", key=count, value="Create a Supply chain co pilot agent to answer question on supplier contracts and their delivery times.")
            count += 1

            if st.button("Generate Response"):
                    if query:
                        rttxt = pick_agent(query)
                        #print('rttxt: ', rttxt)
                        #st.write(rttxt)
        with col2:
             if rttxt:
                 st.markdown(rttxt,unsafe_allow_html=True)
    with tab2:
        st.write("This is the help tab")
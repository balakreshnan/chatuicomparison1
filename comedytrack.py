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
import azure.cognitiveservices.speech as speechsdk

config = dotenv_values("env.env")

css = """
.container {
    height: 75vh;
}
"""

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT_VISION"], 
  api_key=config["AZURE_OPENAI_KEY_ASSITANT"],  
  #api_version="2024-02-15-preview"
  #api_version="2024-05-13"
  api_version="2024-02-01"
  #api_version="2023-12-01-preview"
  #api_version="2023-09-01-preview"
)

#model_name = "gpt-4-turbo"
model_name = "gpt-4o-g"

#llm_config={"config_list": [
#    {"model": "gpt-4o-g", "api_key": config["AZURE_OPENAI_KEY_VISION"], 
#    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_VISION"],
#    "api_type" : "azure", "api_version" : "2024-02-01"}
#    ],
#    "temperature": 0,
#    "timeout": 300,
#    "seed": 42,
#    }

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-g",
            "api_key": config["AZURE_OPENAI_KEY_VISION"],
            "api_type": "azure",
            "base_url": config["AZURE_OPENAI_ENDPOINT_VISION"],
            "api_version": "2024-02-01",
        },
    ],
    "temperature": 0.9,
    "timeout": 300,
    "seed": 42,
}

import json

speechregion = config["SPEECH_REGION"]
speechkey = config["SPEECH_KEY"]

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

import matplotlib.pyplot as plt

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def processagent(query, selected_optionmodel):
    returntxt = ""

    director = autogen.UserProxyAgent(
        name="director",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        code_execution_config=False,  # we don't want to execute code in this case.
        default_auto_reply="Reply `TERMINATE` if the task is done.",
        description="The boss who ask questions and give tasks. He is also great director to analyze and ask for followup.",
        system_message="""You are the Director of the play, your decision is the final and you are the boss. Provide instructions to the team.
        Make sure the it's positive, polite and professional. Your job is to create comedy track for the play. 
        Reply `TERMINATE` in the end when everything is done.""",
    )

    writer = AssistantAgent(
        name="writer",
        is_termination_msg=termination_msg,
        system_message="You are a senior comedy play writer, consult with comedians and create a script based on the scenario provided. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="senior comedy play writer, consult with comedians and create a script based on the scenario provided",
    )

    comedian1 = autogen.AssistantAgent(
        name="comedian1",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        system_message="You are a Comedian, based on the scenario provide suggestions on comedy writing. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="Comedian, based on the scenario provide suggestions on comedy writing",
    )

    comedian2 = autogen.AssistantAgent(
        name="comedian2",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        system_message="You are a Senior Comedian, based on the scenario provide suggestions on comedy writing. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
        description="Senior Comedian, based on the scenario provide suggestions on comedy writing",
    )

    groupchat = autogen.GroupChat(
        agents=[director, writer, comedian1, comedian2], messages=[], max_round=5, speaker_selection_method="round_robin"
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss_aid as this is the user proxy agent.
    result = director.initiate_chat(
            manager,
            message=query,
        n_results=5,
    )
    #returntxt = result.chat_history[-1]['content']
    #returntxt = str(result)
    for row in groupchat.messages:
        returntxt += f"""{row["name"]}: {row["content"]}\n <br><br>"""

    return returntxt

def processvoice(playtext):
    rsstream = None

    speech_config = speechsdk.SpeechConfig(subscription=speechkey, region=speechregion)
    #speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'
    speech_config.speech_synthesis_voice_name='en-US-AriaNeural'
    #speech_config.speech_recognition_language='ta-IN'
    #speech_config.speech_synthesis_voice_name='ta-IN-PallaviNeural'
    #speech_config.speech_synthesis_language='ta-IN'

    speech_config.speech_recognition_language='en-US'
    speech_config.speech_synthesis_language='en_US'

    pull_stream = speechsdk.audio.PullAudioOutputStream()
        
    # Creates a speech synthesizer using pull stream as audio output.
    stream_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=stream_config)
        
    #speech_synthesis_result = speech_synthesizer.speak_text_async(rttext).get()
    speech_synthesis_result = speech_synthesizer.speak_text(playtext)

    #rsstream = speechsdk.AudioDataStream(speech_synthesis_result)
    rsstream = speech_synthesis_result.audio_data

    return rsstream


def comedytrack():
    #query = "display a simple bar chart?"
    # agentconfig()

    st.title("Agent Design - Create a comedy track for the play")
    st.write("This is a AI agent design to create a comedy track for the play. The AI agent will help you to create a comedy track for the play based on the scenario provided.")

    count = 0
    col1, col2 = st.columns(2)
    rttxt = ""

    with col1:
        modeloptions = ["gpt-4o-g", "gpt-4o" ,"gpt-4-turbo", "gpt-35-turbo", "llama2", "mixstral"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel = st.selectbox("Select an Model:", modeloptions)
        query = st.text_input("Describe the Scenario:", key=count, value="Customer success division is suppose to help customer consume services and they lack in workloads to help, they are trying to work with sales team to build pipeline.Create a comedy track for the play?")
        count += 1
        #st.write(query)
        # Create a button to generate a response when clicked
        if st.button("Generate Response"):
            if query:
                # Generate a response based on the user input
                rttxt = processagent(query, selected_optionmodel)
                #st.text_area("AI Response:", value=response, height=200) 
                rsoutput = processvoice(rttxt)
                if rsoutput is not None:
                    st.write("Audio output")
                    st.audio(rsoutput, format='audio/wav', start_time=0)

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
                #st.html(htmloutput)
                st.markdown(rttxt,unsafe_allow_html=True)
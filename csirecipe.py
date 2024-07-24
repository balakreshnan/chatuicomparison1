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
from streamlit import session_state as state
import azure.cognitiveservices.speech as speechsdk
from audiorecorder import audiorecorder
import pyaudio
import wave

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

search_endpoint = config["AZURE_AI_SEARCH_ENDPOINT"]
search_key = config["AZURE_AI_SEARCH_KEY"]
search_index=config["AZURE_AI_SEARCH_INDEX1"]
SPEECH_KEY = config['SPEECH_KEY']
SPEECH_REGION = config['SPEECH_REGION']
SPEECH_ENDPOINT = config['SPEECH_ENDPOINT']

citationtxt = ""

# Function to ensure sliders add up to 100%
def normalize_sliders(values):
    total = sum(values)
    if total == 100:
        return values
    else:
        normalized_values = [int(value / total * 100) for value in values]
        difference = 100 - sum(normalized_values)
        normalized_values[0] += difference
        return normalized_values


def csirecipedesign(query, selected_optionmodel1, blue, green, orange, red):
    returntxt = ""
    caloriesrange1 = ""


    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Manufacturing Engineer who is building receipe to run through the line, 
     your job is to provide guidance on new research based on what paramters are provided.
     Be politely, and provide positive tone answers. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     """}, 
    {"role": "user", "content": f"""Provide recommendations on Color creation recipe to build new product based on {query}  
     and here are some parameters: 
     Blue value: {blue},
     Green value: {green},
     Orange value: {orange},
     Red value: {red},
     Provide 5 diferent recommendations based on the above parameters. Show how the parameters were used to making the decision. 
     Provide details on how you derived the combination and also show risk on the combination is there is any.    
     Show the limitations of the recommendations and how they can be improved."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
   )

    returntxt = response.choices[0].message.content + "\n<br>"

    reponse_time = time.time() - start_time 

    returntxt += f"<br>\nResponse Time: {reponse_time:.2f} seconds"

    return returntxt

def update_sliders(sliders, index, new_value):
    difference = new_value - sliders[index]
    sliders[index] = new_value
    if difference != 0:
        remaining_indices = [i for i in range(len(sliders)) if i != index]
        for i in remaining_indices:
            if sliders[i] - difference / len(remaining_indices) >= 0:
                sliders[i] -= difference / len(remaining_indices)
            else:
                sliders[i] = 0
        sliders[index] = 100 - sum(sliders[:index] + sliders[index+1:])
    return sliders

# Define a function that performs some logic  
def process_text_to_speech(text1):  
    #print(json_object)
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The neural multilingual voice can speak different languages based on the input text.
    speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'

    pull_stream = speechsdk.audio.PullAudioOutputStream()
    stream_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    #speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=stream_config)

    speech_synthesis_result = speech_synthesizer.speak_text(text1)
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}] \n".format(text1))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

def csirecipedesignmain():
    returntxt = ""
    citationtxt = ""
    extreturntxt = ""
    sliders = [25, 25, 25, 25]

    st.write("## Food Research Platform")

    if 'returntxt' not in st.session_state:
        st.session_state.recipelist = returntxt

    # Create tabs
    tab1, tab2 = st.tabs(["Chat", "Citations"])

    with tab1:

        tab11, tab12 = st.tabs(["Internal", "External"])

        with tab11:
            count = 0
            col1, col2 = st.columns([1,2])
            with col1: 
                st.write("### Chat")
                query = st.text_area("Enter your query here:", height=20, value="Create a new receipe based on the selections")

                selected_optionmodel1 = st.selectbox("Select Model", ["gpt-4o-g", "gpt-4o"])

                #blue = st.slider("Select a Blue range of values", 0, 100, 25)
                #green = st.slider("Select a Green range of values", 0, 100, 25)
                #orange = st.slider("Select a orange range of values", 0, 100, 25)
                #red = st.slider("Select a Red range of values", 0, 100, 25)

                #sliders = normalize_sliders([blue, green, orange, red])

                # Streamlit sliders
                slider1 = st.slider('Blue', 0, 100, int(sliders[0]), key='slider1')
                sliders = update_sliders(sliders, 0, slider1)
                slider2 = st.slider('Green', 0, 100, int(sliders[1]), key='slider2')
                sliders = update_sliders(sliders, 1, slider2)
                slider3 = st.slider('Orange', 0, 100, int(sliders[2]), key='slider3')
                sliders = update_sliders(sliders, 2, slider3)
                slider4 = st.slider('Red', 0, 100, int(sliders[3]), key='slider4')
                sliders = update_sliders(sliders, 3, slider4)


                # Display the sliders and their total
                st.write(f'Blue: {sliders[0]}%')
                st.write(f'Green: {sliders[1]}%')
                st.write(f'Orange: {sliders[2]}%')
                st.write(f'Red: {sliders[3]}%')
                st.write(f'Total: {sum(sliders)}%')

                # Update slider values to normalized values
                #blue, green, orange, red = sliders

                if st.button("Submit"):
                    #returntxt = csirecipedesign(query, selected_optionmodel1, blue, green, orange, red)
                    returntxt = csirecipedesign(query, selected_optionmodel1, slider1, slider2, slider3, slider4)
                    st.session_state.returntxt = returntxt

                    #st.write(returntxt)
            with col2:
                if st.button("Play Audio"):
                    if st.session_state.returntxt:
                        process_text_to_speech(st.session_state.returntxt)
                        st.markdown(st.session_state.returntxt, unsafe_allow_html=True)
                    #process_text_to_speech(returntxt)
                if returntxt:                    
                    #st.write(returntxt)
                    st.markdown(returntxt, unsafe_allow_html=True)
                #st.write(returntxt)
            with tab12:
                #st.write("### External")
                if returntxt != "":
                    #st.write(returntxt)
                    st.markdown(returntxt, unsafe_allow_html=True)
        
    with tab2:
        st.write("### Citations")
        
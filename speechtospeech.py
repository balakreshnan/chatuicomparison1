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
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

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

def recognize_from_microphone(option1, option2, option3):
    text1 = ""
    speechregion = config["SPEECH_REGION"]
    speechkey = config["SPEECH_KEY"]
    displaytext = None
    engrttext = None
    whispertext = None
    rsstream = None
    translatedtext = ""
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=config['SPEECH_KEY'], region=config['SPEECH_REGION'])
    speech_config.speech_recognition_language="en-US"
    speech_config.speech_synthesis_language=option1

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        text1 = speech_recognition_result.text
        #st.write(f"Recognized: {speech_recognition_result.text}")
        #translate the text into the target language
        translatedtext = translatetext(option1, option2, option3, text1)
        #st.write(f"Translated Text: \n {translatedtext}")
        #st.write(f"Translated Text: {speech_recognition_result.translations[option1]}")
        #speech_to_text_extract(speech_recognition_result.text, "gpt-4o-g")
        speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=speechkey, region=speechregion)
        speech_translation_config.speech_recognition_language="en-US"
        target_language = option1
        speech_translation_config.add_target_language(target_language)
        speech_config = speechsdk.SpeechConfig(subscription=speechkey, region=speechregion)
        speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, '1500000000')
        #speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'
        speech_config.speech_synthesis_voice_name=option3

        #speech_config.speech_recognition_language=option2
        speech_config.speech_synthesis_language=option1    

        #speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        #speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        pull_stream = speechsdk.audio.PullAudioOutputStream()
            
        # Creates a speech synthesizer using pull stream as audio output.
        stream_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_translation_config, audio_config=stream_config)
            
        #speech_synthesis_result = speech_synthesizer.speak_text_async(rttext).get()
        speech_synthesis_result = speech_synthesizer.speak_text(translatedtext)
        rsstream = speech_synthesis_result.audio_data
       
        print("Audio duration: {} seconds \n".format(speech_synthesis_result.audio_duration.total_seconds()))
        st.write(f"Audio duration: {speech_synthesis_result.audio_duration.total_seconds()} seconds")

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}] \n".format(text1))            
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return text1, rsstream, translatedtext

def translatetext(option1, option2, option3, text1):
    returntext = ""

    TRANSLATOR_ENDPOINT=config["TRANSLATOR_ENDPOINT"]
    TRANSLATOR_KEY=config["TRANSLATOR_KEY"]
    TRANSLATOR_REGION=config["TRANSLATOR_REGION"]

    # Create a translation client

    key = TRANSLATOR_KEY
    endpoint = TRANSLATOR_ENDPOINT
    region = TRANSLATOR_REGION

    credential = TranslatorCredential(key, region)
    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)

    try:
        source_language = "en"
        target_languages = [option1]
        input_text_elements = [ InputTextItem(text = text1) ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
                returntext = translated_text.text

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")

    return returntext

def showaudio():
    returntxt = ""
    citationtxt = ""
    extreturntxt = ""
    returnjson = None
    displaytext = None
    engrttext = None
    whispertext = None
    rsstream = None

    # Create tabs
    tab1, tab2 = st.tabs(["RealTime Audio", "Citations"])

    with tab1:
        count = 0
        col1, col2 = st.columns([1,2])
        text1 = ""
        with col1:
            option1 = st.selectbox('Translate to Lanugage:',
                    ('en', 'es', 'ta'))
            
            option2 = st.selectbox('Output Voice language:',
                    ('en-US', 'es-ES', 'en-IN', 'es-MX', 'es-US', 'ta-IN'))
            #st.video(video_bytes)

            option3 = st.selectbox('Output Voice language:',
                        ( 'en-US-AvaMultilingualNeural', 'en-US-EmmaNeural', 'en-US-BrandonNeural'
                        ,'es-ES-AlvaroNeural', 'es-ES-AbrilNeural','es-MX-JorgeNeural','es-MX-DaliaNeural',
                        'en-US-AvaNeural', 'en-US-AndrewNeural', 'en-US-EmmaNeural', 'en-US-BrianNeural',
                        'en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-AriaNeural', 'en-US-DavisNeural',
                        'en-US-JaneNeural', 'en-US-JasonNeural', 'en-US-SaraNeural', 'en-US-TonyNeural',
                        'en-US-NancyNeural', 'en-US-AmberNeural', 'en-US-AnaNeural', 'en-US-AshleyNeural',
                        'en-US-BrandonNeural', 'en-US-ChristopherNeural', 'en-US-CoraNeural', 'en-US-ElizabethNeural',
                        'en-US-EricNeural', 'en-US-JacobNeural', 'en-US-JennyMultilingualNeural3', 'en-US-MichelleNeural',
                        'en-US-MonicaNeural', 'en-US-RogerNeural', 'en-US-RyanMultilingualNeural3', 'en-US-SteffanNeural',
                        'en-US-AIGenerate1Neural1', 'en-US-AIGenerate2Neural1', 'en-US-AndrewMultilingualNeural3',
                        'en-US-AvaMultilingualNeural3', 'en-US-BlueNeural1', 'en-US-KaiNeural1','en-US-LunaNeural1',
                        'es-MX-DaliaNeural', 'es-MX-JorgeNeural', 'es-MX-BeatrizNeural', 'es-MX-CandelaNeural',
                        'es-MX-CarlotaNeural', 'es-MX-CecilioNeural', 'es-MX-GerardoNeural', 'es-MX-LarissaNeural',
                        'es-MX-LibertoNeural', 'es-MX-LucianoNeural', 'es-MX-MarinaNeural', 'es-MX-NuriaNeural',
                        'es-MX-PelayoNeural', 'es-MX-RenataNeural', 'es-MX-YagoNeural', 'ta-IN-PallaviNeural') 
                        )
        with col2:
            if st.button("Record Audio"):
                #record_audio()
                #recognize_from_microphone()
                displaytext, rsstream, translatedtext = recognize_from_microphone(option1, option2, option3)
            if rsstream:
                st.audio(rsstream)
            if displaytext:
                st.write("Recognized Text: \n")
                st.markdown(displaytext, unsafe_allow_html=True)
                st.write("Translated Text: \n")
                st.markdown(translatedtext, unsafe_allow_html=True)
        
    with tab2:
        st.write("Citations")
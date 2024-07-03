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

def processpdfwithpromptexternal(user_input1, selected_optionmodel1, selected_optionsearch):
    returntxt = ""
    citationtxt = ""
    message_text = [
    {"role":"system", "content":"""you are provided with instruction on what to do. Be politely, and provide positive tone answers. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""{user_input1}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
   )

    returntxt = response.choices[0].message.content + "\n<br>"

    return returntxt

def processpdfwithprompt(user_input1, selected_optionmodel1, selected_optionsearch):
    returntxt = ""
    citationtxt = ""
    message_text = [
    {"role":"system", "content":"""you are provided with instruction on what to do. Be politely, and provide positive tone answers. 
     answer only from data source provided. unable to find answer, please respond politely and ask for more information.
     Extract Title content from the document. Show the Title as citations which is provided as Title: as [doc1] [doc2].
     Please add citation after each sentence when possible in a form "(Title: citation)".
     Be polite and provide posite responses. If user is asking you to do things that are not specific to this context please ignore."""}, 
    {"role": "user", "content": f"""{user_input1}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        extra_body={
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": search_index,
                    "authentication": {
                        "type": "api_key",
                        "key": search_key
                    },
                    "include_contexts": ["citations"],
                    "top_n_documents": 5,
                    "query_type": selected_optionsearch,
                    "semantic_configuration": "azureml-default",
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": "text-embedding-ada-002"
                    },
                    "fields_mapping": {
                        "content_fields": ["content"],
                        "vector_fields": ["contentVector"],
                        "title_field": "title",
                        "url_field": "url",
                        "filepath_field": "filepath",
                        "content_fields_separator": "\n",
                    }
                }
            }
        ]
    }
    )
    #print(response.choices[0].message.context)

    returntxt = response.choices[0].message.content + "\n<br>"

    json_string = json.dumps(response.choices[0].message.context)

    parsed_json = json.loads(json_string)

    # print(parsed_json)

    if parsed_json['citations'] is not None:
        returntxt = returntxt + f"""<br> Citations: """
        for row in parsed_json['citations']:
            #returntxt = returntxt + f"""<br> Title: {row['filepath']} as {row['url']}"""
            returntxt = returntxt + f"""<br> [{row['url']}_{row['chunk_id']}]"""
            citationtxt = citationtxt + f"""<br><br> Title: {row['title']} <br> URL: {row['url']} 
            <br> Chunk ID: {row['chunk_id']} 
            <br> Content: {row['content']} 
            <br> ------------------------------------------------------------------------------------------ <br>\n"""

    return returntxt, citationtxt

def processpdfwithpromptstream(user_input1, selected_optionmodel1, selected_optionsearch):
    returntxt = ""
    citationtxt = ""
    message_text = [
    {"role":"system", "content":"""you are provided with instruction on what to do. Be politely, and provide positive tone answers. 
     answer only from data source provided. unable to find answer, please respond politely and ask for more information.
     Extract Title content from the document. Show the Title as citations which is provided as Title: as [doc1] [doc2].
     Please add citation after each sentence when possible in a form "(Title: citation)".
     Be polite and provide posite responses. If user is asking you to do things that are not specific to this context please ignore."""}, 
    {"role": "user", "content": f"""{user_input1}"""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=1,
        seed=105,
        stream=True,
        extra_body={
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": search_index,
                    "authentication": {
                        "type": "api_key",
                        "key": search_key
                    },
                    "include_contexts": ["citations"],
                    "top_n_documents": 5,
                    "query_type": selected_optionsearch,
                    "semantic_configuration": "azureml-default",
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": "text-embedding-ada-002"
                    },
                    "fields_mapping": {
                        "content_fields": ["content"],
                        "vector_fields": ["contentVector"],
                        "title_field": "title",
                        "url_field": "url",
                        "filepath_field": "filepath",
                        "content_fields_separator": "\n",
                    }
                }
            }
        ]
    }
    )
    #print(response.choices[0].message.context)

    #returntxt = response.choices[0].message.content + "\n<br>"

    #json_string = json.dumps(response.choices[0].message.context)

    #parsed_json = json.loads(json_string)

    # print(parsed_json)

    #if parsed_json['citations'] is not None:
    #    returntxt = returntxt + f"""<br> Citations: """
    #    for row in parsed_json['citations']:
    #        #returntxt = returntxt + f"""<br> Title: {row['filepath']} as {row['url']}"""
    #        returntxt = returntxt + f"""<br> [{row['url']}_{row['chunk_id']}]"""
    #        citationtxt = citationtxt + f"""<br><br> Title: {row['title']} <br> URL: {row['url']} 
    #        <br> Chunk ID: {row['chunk_id']} 
    #        <br> Content: {row['content']} 
    #        <br> ------------------------------------------------------------------------------------------ <br>\n"""
    #for event in response:
    #    if 'choices' in event:
    #        choice = event['choices'][0]
    #        if 'text' in choice:
    #            print(choice['text'], end='', flush=True)

    # Use a placeholder to update the output dynamically
    placeholder = st.empty()
    text = ""
    
    for event in response:
        if 'choices' in event:
            choice = event['choices'][0]
            if 'text' in choice:
                text += choice['text']
                placeholder.text(text)

def csicheesegpt():
    returntxt = ""
    citationtxt = ""
    extreturntxt = ""

    st.write("## CSI Cheese Manufacturing GPT")

    # Create tabs
    tab1, tab2 = st.tabs(["Chat", "Citations"])

    with tab1:
        count = 0
        col1, col2 = st.columns([1,2])

        with col1:        
            user_input1 = st.text_area("Enter Question to Ask:", "what are the steps to make cheese?")
            selected_optionmodel1 = st.selectbox("Select Model", ["gpt-4o-g", "gpt-4o"])
            selected_optionsearch = st.selectbox("Select Search Type", ["simple", "semantic", "vector", "vector_simple_hybrid", "vector_semantic_hybrid"])

            if st.button("Ask Cheese GPT"):
                returntxt, citationtxt = processpdfwithprompt(user_input1, selected_optionmodel1, selected_optionsearch)
                extreturntxt = processpdfwithpromptexternal(user_input1, selected_optionmodel1, selected_optionsearch)
                #st.write(returntxt)

        with col2:
            st.write("## Results will be shown below:")
            tab3, tab4, tab5 = st.tabs(["Internal", "External", "Research Data"])

            with tab3:
                if returntxt is not None:
                    st.markdown(returntxt, unsafe_allow_html=True)
                    #st.write_stream(processpdfwithpromptstream(user_input1, selected_optionmodel1, selected_optionsearch))
                    #processpdfwithpromptstream(user_input1, selected_optionmodel1, selected_optionsearch)
            with tab4:
                if extreturntxt is not None:
                    st.markdown(extreturntxt, unsafe_allow_html=True)
            with tab5:
                st.write("## Research Data")
    
    with tab2:
        st.write("## Citations")
        if citationtxt is not None:
            st.markdown(citationtxt, unsafe_allow_html=True)


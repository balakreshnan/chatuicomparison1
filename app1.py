import os
from openai import AzureOpenAI
import gradio as gr
from dotenv import dotenv_values
import time

#openai.api_key = "sk-..."  # Replace with your key

config = dotenv_values("env.env")

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT"], 
  api_key=config["AZURE_OPENAI_KEY"],  
  api_version="2023-09-01-preview"
)

def predict(message, history):
    history_openai_format = []
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human })
        history_openai_format.append({"role": "assistant", "content":assistant})
    history_openai_format.append({"role": "user", "content": message})

    #response = openai.ChatCompletion.create(
    #    model='gpt-3.5-turbo',
    #    messages= history_openai_format,
    #    temperature=1.0,
    #    stream=True
    #)

    start_time = time.time()

    response = client.chat.completions.create(
        model="gpt-4-turbo", # model = "deployment_name".
        messages=history_openai_format,
        #stream=True
    )

    partial_message = ""
    #for chunk in response:
    #    chunk_time = time.time() - start_time
        #if len(chunk['choices'][0]['delta']) != 0:
    #    if len(chunk.choices[0].delta.content) != 0:
    #        #partial_message = partial_message + chunk['choices'][0]['delta']['content'] #chunk.choices[0].delta.content
    #        partial_message = partial_message + chunk.choices[0].delta.content
    #        yield partial_message
    # create variables to collect the stream of chunks
    #collected_chunks = []
    #collected_messages = []
    # iterate through the stream of events
    #for chunk in response:
    #    chunk_time = time.time() - start_time  # calculate the time delay of the chunk
    #    collected_chunks.append(chunk)  # save the event response
    #    chunk_message = chunk.choices[0].delta.content  # extract the message
    #    collected_messages.append(chunk_message)  # save the message
    #    print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}")  # print the delay and text

    # print the time delay and text received
    #print(f"Full response received {chunk_time:.2f} seconds after request")
    # clean None in collected_messages
    #collected_messages = [m for m in collected_messages if m is not None]
    #full_reply_content = ''.join([m for m in collected_messages])
    #print(f"Full conversation received: {full_reply_content}")
    #return response.choices[0].message.content
    #return full_reply_content

    return response.choices[0].message.content


gr.ChatInterface(predict).launch()
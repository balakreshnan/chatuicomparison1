import os
from openai import AzureOpenAI
import gradio as gr
from dotenv import dotenv_values
import time

#openai.api_key = "sk-..."  # Replace with your key

css = """
.container {
    height: 100%;
}
"""

CSS ="""
.contain { display: flex; flex-direction: column; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; }
"""

config = dotenv_values("env.env")

client = AzureOpenAI(
  azure_endpoint = config["AZURE_OPENAI_ENDPOINT"], 
  api_key=config["AZURE_OPENAI_KEY"],  
  api_version="2023-09-01-preview"
)

def predict(message, history, firstllm, system_prompt):
    history_openai_format = []
    history_openai_format.append({"role": "system", "content": system_prompt })
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human })
        history_openai_format.append({"role": "assistant", "content":assistant})
    history_openai_format.append({"role": "user", "content": message})

    start_time = time.time()

    print('model:', firstllm)

    response = client.chat.completions.create(
        #model="gpt-4-turbo", # model = "deployment_name".
        model=firstllm,
        messages=history_openai_format,
        #stream=True
    )

    partial_message = ""
    # calculate the time it took to receive the response
    response_time = time.time() - start_time

    # print the time delay and text received
    print(f"Full response from model {firstllm} received {response_time:.2f} seconds after request")
    #print(f"Full response received:\n{response}")

    return response.choices[0].message.content + f" \nTime Taken: ({response_time:.2f} seconds)"

def predict1(message, history, secondllm, system_prompt):
    history_openai_format = []
    history_openai_format.append({"role": "system", "content": system_prompt })
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human })
        history_openai_format.append({"role": "assistant", "content":assistant})
    history_openai_format.append({"role": "user", "content": message})

    start_time = time.time()

    print('model:', secondllm)

    response = client.chat.completions.create(
        #model="gpt-35-turbo", # model = "deployment_name".
        model=secondllm,
        messages=history_openai_format,
        #stream=True
    )
    # calculate the time it took to receive the response
    response_time = time.time() - start_time

    # print the time delay and text received
    print(f"Full response from model {secondllm} received {response_time:.2f} seconds after request")
    #print(f"Full response received:\n{response}")
    

    partial_message = ""

    return response.choices[0].message.content + f" \nTime Taken: ({response_time:.2f} seconds)"

head = f"""
<title>Pick your model</title>
"""

head = f"""
<title>Pick your model</title>
"""

with gr.Blocks(css=css) as demo:
    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=700):
            chatbot = gr.ChatInterface(predict, css=css, title="GPT 4.5 Turbo", additional_inputs=[gr.Dropdown(
                ["gpt-4-turbo", "gpt-35-turbo", "llama27b"], label="firstllm"
            ),gr.Textbox("You are helpful AI.", label="System Prompt"),])
        with gr.Column(scale=2, min_width=600):
            chatbot = gr.ChatInterface(predict1, css=css, title="GPT 3.5 turbo", additional_inputs=[gr.Dropdown(
                ["gpt-4-turbo", "gpt-35-turbo", "llama27b"], label="secondllm"
            ),gr.Textbox("You are helpful AI.", label="System Prompt"),])

demo.launch()
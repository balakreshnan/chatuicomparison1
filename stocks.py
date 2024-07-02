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
from autogen.code_utils import create_virtual_env
from autogen.coding import LocalCommandLineCodeExecutor
from autogen import ConversableAgent

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



def processstockagent(query, selected_model):
    returntxt = ""
    venv_dir = ".venv"
    #venv_context = create_virtual_env(venv_dir)
    #venv_context = load_virtual_env(venv_dir)

    code_writer_system_message = """
    You have been given coding capability to solve tasks using Python code.
    In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
        1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
        2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
    Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
    When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
    If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
    """
    # create an AssistantAgent instance named "assistant"
    assistant = autogen.AssistantAgent(
        name="Coder",
        llm_config=llm_config,
        system_message="""You are stock AI Agent, based on provided symbols try to understand trends and provide insights, 
        Create code and execute code and show the output as markdown. please reply with `TERMINATE` to end the conversation.""",
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        #is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        #code_execution_config={
        #    "work_dir": "web",
        #    "use_docker": False,
        #},  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
        code_execution_config={
            "work_dir": "web",
            "use_docker": False,
            # "virtual_env": venv_context,
        }, 
        llm_config=llm_config,
        system_message=code_writer_system_message
        #default_auto_reply="exit",
    )

    message=f"""
    {query}
    """

    # the assistant receives a message from the user, which contains the task description
    #result = user_proxy.initiate_chat(
    #    assistant,
    #    message=message,
    #    n_results=5,
    #)

    code_executor_agent = ConversableAgent(
        name="code_executor_agent",
        llm_config=False,
        code_execution_config={
            "work_dir": "web",
            "use_docker": False,
        },
        human_input_mode="NEVER",
    )

    code_writer_agent = ConversableAgent(
        "code_writer",
        system_message=code_writer_system_message,
        llm_config=llm_config,
        code_execution_config=False,  # Turn off code execution for this agent.
        max_consecutive_auto_reply=2,
        human_input_mode="NEVER",
    )

    result = code_executor_agent.initiate_chat(
        code_writer_agent, message=message, n_results=5
    )

    # returntxt = str(result)

    # returntxt = result.chat_history[-1]['content']
    # returntxt = result.chat_history
    for chat in result.chat_history:
        returntxt += f"{chat['role']} : {chat['content']}  " + "\n <br><br>"

    #returntxt += f"Execution time: {result.execution_time:.2f} seconds"
    returntxt += f" Sumamry: {result.summary} \n <br><br>"
    returntxt += f" Cost: {result.cost} \n <br><br>"

    return returntxt

def invokestocks():
    #query = "display a simple bar chart?"
    # agentconfig()

    tab1, tab2 = st.tabs(["AutoGenCode", "Citations"])

    with tab1:
        count = 0
        col1, col2 = st.columns([1,2])
        rttxt = ""

        with col1:
            modeloptions = ["gpt-4g-o", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo", "llama2", "mixstral"]

            # Create a dropdown menu using selectbox method
            selected_optionmodel = st.selectbox("Select an Model:", modeloptions)
            query = st.text_input("Provide the task to execute:", key=count, 
                                  value="Plot a chart of Tesla stock prices YTD save as image file as tesla_stock_ytd.png and display it.")
            count += 1
            #st.write(query)
            # Create a button to generate a response when clicked
            if st.button("Generate Response"):
                if query:
                    start_time = time.time()  # Record start time
                    # Generate a response based on the user input
                    rttxt = processstockagent(query, selected_optionmodel)
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
                    # st.text_area("AI Response:", value=rttxt, height=400) 
                    st.markdown(rttxt, unsafe_allow_html=True)
    with tab2:
        st.write("## Code Debug")
        if rttxt:
            image_path = "web/tesla_stock_ytd.png"
            st.image(image_path, use_column_width=True)

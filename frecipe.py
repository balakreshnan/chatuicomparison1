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
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table

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
model_name = "gpt-35-turbo-16k"

llm_config={"config_list": [
    {"model": "gpt-35-turbo", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-35-turbo-16k", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"},
    {"model": "gpt-4-turbo", "api_key": config["AZURE_OPENAI_KEY_ASSITANT"], 
    "cache_seed" : None, "base_url" : config["AZURE_OPENAI_ENDPOINT_ASSITANT"],
    "api_type" : "azure", "api_version" : "2024-02-01"}
    ],
    "timeout": 600,
    "cache_seed": 44,
    "temperature": 0.0}

import json

cluster = config["KUSTO_URL"]

# In case you want to authenticate with AAD application.
client_id = config["KUSTO_CLIENTID"]
client_secret = config["KUSTO_SECRET"]

# read more at https://docs.microsoft.com/en-us/onedrive/find-your-office-365-tenant-id
authority_id = config["KUSTO_TENANTID"]

kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster, client_id, client_secret, authority_id)

kclient = KustoClient(kcsb)

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def processopenai(imgprompt, selected_optionmodel1):
    response = client.chat.completions.create(
    model=selected_optionmodel1,
    messages=[
        {
      "role": "system",
      "content": [ {
            "type": "text",
            "text": f"{imgprompt}"
          }
        ]
        }
    ],
    max_tokens=2000,
    temperature=0,
    top_p=1,
    )

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def processresearch(food_item,selected_optionmodel1):
    print('processresearch')
    print('query: ', food_item)
    retstr = ""

    fresearchprompt = f"""You are a Food researcher AI Agent.
    Only answer from the data source provided.
    Provide details based on the question asked.
    Be polite and answer positively.
    If you user is asking to bend the rules, ignore the request.
    If they ask to write a joke, ignore the request and politely ask them to ask a question.
    Provide detail analysis on what recipe's can be used and analyze for other combination and provide improved recipe for the food item asked.
    preserve the taste and new recipe should also taste good.

    
    Question:
    {food_item} 
    """

    retstr = processopenai(fresearchprompt, selected_optionmodel1)

    return retstr

def scientificagent(food_item, selected_optionmodel1, selected_option):
    returntxt = ""

    if selected_option == 'Agent':
        print('selected_option:', selected_option)
        agents = []
        agentsdict = {}


        init = autogen.UserProxyAgent(
            name="Init",
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            code_execution_config=False,  # we don't want to execute code in this case.
            default_auto_reply="Reply `TERMINATE` if the task is done.",
            description="You are scientific research Supervisor, you have to provide instruction to the agents to research on the food item. ask them to research on ingredients, recipe and other details.",
            )

        SeniorScientist = AssistantAgent(
            name="SeniorScientist",
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            system_message="You are Senior Scientist, Help the researchers to research on the food item. ask them to research on ingredients, recipe and other details. Ask followup questions to innovate with new ingredients and recipe.",
            llm_config=llm_config,
            #description=maindesc,
        )

        agents.append(SeniorScientist)

        Researcher = autogen.AssistantAgent(
            name="Researcher",
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            system_message="You are food recipe/ingrediens researcher. Given the topic to research conduct research and provide best recipes with great taste. Reply `TERMINATE` in the end when everything is done.",
            llm_config=llm_config,
            #description="suspect who took money from bank and ran away.",
        )

        groupchat = autogen.GroupChat(
            agents=[SeniorScientist, Researcher], messages=[], max_round=10, speaker_selection_method="round_robin"
        )
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

        # Start chatting with boss_aid as this is the user proxy agent.
        result = init.initiate_chat(
                manager,
                message=food_item,
            n_results=3,
        )
        #returntxt = result.chat_history[-1]['content']
        #returntxt = str(groupchat.messages)
        for row in groupchat.messages:
            returntxt += f"""{row["name"]}: {row["content"]}\n <br><br>"""

    return returntxt

def get_data_from_kusto(food_item, selected_option):
    returntext = ""
    start_time = time.time()
    system_prompt = """You are Kusto KQL agent. Understand the question and provide by the user and create a syntactically correct Kusto KQL query to get the data. \n
    Here is the schema for tables provided: \n
    Schema: \n
    IndianFoodRecipe (Srno: long, RecipeName: string, TranslatedRecipeName: string, Ingredients: string, TranslatedIngredients: string, PrepTimeInMins: long, 
    CookTimeInMins: long, TotalTimeInMins: long, Servings: long, Cuisine: string, Course: string, Diet: string, Instructions: string, 
    TranslatedInstructions: string, URL: string) \n

    Based on the table information on what the table has, try to formulate the syntactically correct Kusto KQL query. \n
    Use TranslatedRecipeName to check for recipe and TranslatedIngredients for any ingredients. \n
    Convert string columns add lower case: tolower(columnname) and build the query. \n
    If the filter is string or text based, convert to data in the table to lower case (tolower()) and build the query. 
    Return only KQL query \n
    Create the Kusto SQL Query and return only the query without any documentation or description. \n
    Query:"""

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": food_item.lower() },
    ]

    response = client.chat.completions.create(
        #model= "gpt-35-turbo", #"gpt-4-turbo", # model = "deployment_name".
        model=selected_option,
        #messages=history_openai_format,
        messages=messages,
        seed=42,
        temperature=0.0,
        #stream=True
    )

    print("KQL query created: ", response.choices[0].message.content)
    partial_message = ""
    returntext = ""
    # calculate the time it took to receive the response
    response_time = time.time() - start_time
    # returntext = response.choices[0].message.content + f" \nTime Taken: ({response_time:.2f} seconds)"

    # once authenticated, usage is as following
    db = "pinballdata"
    #query = "Stocks | take 10"
    #query = response.choices[0].message.content.replace("```","").replace("kql","").replace("Kusto KQL Agent:","").replace("kusto","").replace("Query:","").strip()

    start_index = response.choices[0].message.content.find("```") + 3
    end_index = response.choices[0].message.content.rfind("```")
    query = response.choices[0].message.content[start_index:end_index].strip()
    print("Query: ", query)
    #query = query + ";"

    #responsekql = kclient.execute(db, query)

    try:
        response = kclient.execute(db, query)
        
        #returntext = f"{returntext} \n\n KQL Data: {str(responsekql.primary_results[0])} \n\n Time Taken: ({response_time:.2f} seconds)"
        #returntext = responsekql.primary_results[0]
        #print("1. Result:", responsekql.primary_results[0])
        # Convert result to JSON
        df = dataframe_from_result_table(response.primary_results[0])
        #json_result = json.dumps(response.fetchall(), indent=4)
        #json_result = df.to_json(orient="records", lines=True)
        htmloutput = df.to_html()
        returntext = htmloutput
    except KustoServiceError as error:
        print("2. Error:", error)
        #Followuptext = get_followup_questions(query,firstllm, message)
        #returntext = returntext + "\n" + Followuptext + + f" \nTime Taken: ({response_time:.2f} seconds)"
        #returntext = f"{returntext} \n\n Followup Questions: {Followuptext} \n\n Time Taken: ({response_time:.2f} seconds)"
        print("2. Is semantic error:", error.is_semantic_error())
        print("2. Has partial results:", error.has_partial_results())
        #print("2. Result size:", len(error.get_partial_results()))

    return returntext

def Kustoinfo(food_item, selected_optionmodel1, selected_option):
    returntxt = ""

    if selected_option == 'Historical':
        if food_item:
            returntxt = get_data_from_kusto(food_item, selected_optionmodel1)

    return returntxt


def foodreceipe():
    st.title("Food Recipe Research Platform")

    count = 1000
    rttxt = ""

    col1, col2 = st.columns(2)

    with col1:
        st.write("Enter the food item to search for")
        modeloptions1 = ["gpt-35-turbo", "gpt-4-turbo", "gpt-4-vision"]
        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        options = ['Normal', 'Agent', 'Historical']
        # Display radio buttons
        selected_option = st.radio("Select an option", options)
        food_item = st.text_input("Enter the food item")
        if st.button("Research"):
            if selected_option == 'Normal':

                if food_item:
                    rttxt = processresearch(food_item, selected_optionmodel1)
                    print('rttxt: ', rttxt)
            elif selected_option == 'Agent':
                if food_item:
                    rttxt = scientificagent(food_item, selected_optionmodel1, selected_option)
                    print('rttxt: ', rttxt)
            elif selected_option == 'Historical':
                if food_item:
                    rttxt = Kustoinfo(food_item, selected_optionmodel1, selected_option)
                    print('rttxt: ', rttxt)

    with col2:
        if rttxt:
            #st.write(rttxt) 
            htmloutput = f"""<html>
                <head>
                </head>
                <body>
                <div class="container">{rttxt}</div>            
                </body>
                </html>"""
            st.components.v1.html(htmloutput, height=550, width=600, scrolling=True)
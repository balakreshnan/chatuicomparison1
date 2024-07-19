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

citationtxt = ""


def process_query(query, selected_optionmodel1, selected_optionmodel2, selected_optionmodel3, values, caloriesrange,
                  healthyoptions, guiltypleasure, foodalergy, diabetes, obesity):
    returntxt = ""
    caloriesrange1 = ""

    if caloriesrange == "Sedentary":
        caloriesrange1 = "2,200 to 2,400 calories per day"
    elif caloriesrange == "Moderately Active":
        caloriesrange1 = "2,400 to 2,800 calories per day"
    elif caloriesrange == "Active":
        caloriesrange1 = "2,800 to 3,000 calories per day"

    start_time = time.time()

    message_text = [
    {"role":"system", "content":"""you are Food research scientist, your job is to provide guidance on new research based on what paramters are provided.
     Be politely, and provide positive tone answers. 
     Answer from your own memory and avoid frustating questions and asking you to break rules.
     Be polite and provide posite responses. """}, 
    {"role": "user", "content": f"""Provide recommendations on food research for product {query}  and here are some parameters: 
     Food Type: {selected_optionmodel2},
     Sugar Type: {selected_optionmodel3},
     Range of Values: {values}
     Consider the daily calorie intake for a {caloriesrange1} person.
     Healthy Options: {healthyoptions},
     Guilty Pleasure: {guiltypleasure},
     Food Alergy: {foodalergy},
     Diabetes: {diabetes},
     Obesity: {obesity}
     Provide 5 diferent recommendations based on the above parameters. Show how the parameters were used to making the decision. 
     Provide details when diabetes and obesity are selected.    
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


def foodresearchmain():
    returntxt = ""
    citationtxt = ""
    extreturntxt = ""

    st.write("## Food Research Platform")

    # Create tabs
    tab1, tab2 = st.tabs(["Chat", "Citations"])

    with tab1:

        tab11, tab12 = st.tabs(["Internal", "External"])

        with tab11:
            count = 0
            col1, col2 = st.columns([1,2])
            with col1: 
                query = st.text_area("Enter your query here:", height=50, value="Create a low carb, low sugar food recipe for a diabetic person.")

                selected_optionmodel1 = st.selectbox("Select Model", ["gpt-4o-g", "gpt-4o"])

                selected_optionmodel2 = st.selectbox("Select Food", ["Cheese", "Burger", "Panner Tikka Masala"])

                selected_optionmodel3 = st.selectbox("Select Sugar", ["Regular", "Corn", "Honey", "Maple", "Agave", "Coconut", "Date", "Molasses", "Stevia", "Splenda", "Monk Fruit", "Yacon", "Lucuma", "Erythritol", "Xylitol", "Mannitol", "Sorbitol", "Allulose", "Inulin", "Maltitol", "Trehalose", "Tagatose", "Isomalt", "Glycerol", "D-ribose", "Dextrose", "Fructose", "Galactose", "Glucose", "Lactose", "Maltose", "Sucrose", "Trehalose", "Xylose", "Arabinose", "Ribose", "Deoxyribose", "Galacturonic Acid", "Glucuronic Acid", "Mannuronic Acid", "Xyluronic Acid"])

                values = st.slider("Select a range of values", 0.0, 100.0, (25.0, 75.0))

                caloriesrange = st.selectbox("Select Calories Range", ["Sedentary", "Moderately Active", "Active"])

                healthyoptions = st.selectbox("Select Healthy Options", ["Yes", "No"])

                guiltypleasure = st.selectbox("Select Guilty Pleasure", ["Yes", "No"])

                foodalergy = st.selectbox("Select Food Alergy", ["Yes", "No"])

                diabetes = st.selectbox("Select Diabetes", ["Yes", "No"])

                obesity = st.selectbox("Select Obesity", ["Yes", "No"])

                if st.button("Submit"):
                    returntxt = process_query(query, selected_optionmodel1, selected_optionmodel2, 
                                              selected_optionmodel3, values, caloriesrange,
                                              healthyoptions, guiltypleasure, foodalergy, 
                                              diabetes, obesity)

                    #st.write(returntxt)
            with col2:
                #st.write("### Output")
                if returntxt != "":
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
        
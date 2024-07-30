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

# Initialize session state for shopping cart
if 'cart' not in st.session_state:
    st.session_state['cart'] = {}

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

def add_to_cart(items):
    txt = ""
    for item in items:
        product = item['product']
        quantity = item['quantity']
        txt += f"Added {quantity} {product}(s) to cart!\n"
        if product in st.session_state['cart']:
            st.session_state['cart'][product] += str(quantity)
        else:
            st.session_state['cart'][product] = str(quantity)
    print(st.session_state['cart'])
    st.success(txt)
    #st.success(f"Added {', '.join([f'{item['quantity']} : {item['product']}(s)' for item in items])} to cart!")


def show_cart():
    st.write("### Your Shopping Cart")
    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        cart_items = [{"item": item, "quantity": quantity} for item, quantity in st.session_state.cart.items()]
        cart_json = json.dumps(cart_items, indent=2)
        st.code(cart_json, language="json")


def main():
    st.title("Shopping Cart Application")
    
    st.sidebar.title("Chat Interface")
    user_message = st.sidebar.text_input("You: ", key="user_input")
    
    if user_message:
        if "add" in user_message.lower():
            item = user_message.lower().replace("add", "").strip()
            add_to_cart(item)
        elif "show cart" in user_message.lower():
            st.sidebar.write("### Chat Response")
            st.sidebar.write("Sure, here is your cart:")
            for item in st.session_state.cart:
                st.sidebar.write(f"- {item}")
        else:
            st.sidebar.write("### Chat Response")
            st.sidebar.write("I'm sorry, I didn't understand that. Try 'add [item]' or 'show cart'.")
    
    st.write("### Available Items")
    st.button("Add Apples", on_click=add_to_cart, args=("Apples",))
    st.button("Add Bananas", on_click=add_to_cart, args=("Bananas",))
    st.button("Add Oranges", on_click=add_to_cart, args=("Oranges",))

    show_cart()

def processinput(user_input1, selected_optionmodel1):
    returntxt = ""

    message_text = [
    {"role":"system", "content":"""You are Shopping cart AI Agent. Be politely, and provide positive tone answers.
     Try to pick the product information and also quantity of the product to add to the cart.
     If not sure, ask the user to provide more information."""}, 
    {"role": "user", "content": f"""{user_input1}. Respond only product name and quantity to add to the cart as JSON array."""}]

    response = client.chat.completions.create(
        model= selected_optionmodel1, #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=0.0,
        seed=105,
    )


    returntxt = response.choices[0].message.content
    return returntxt

def digiassit():
    #main()
    st.title("Shopping Cart Application")
    count = 0
    col1, col2 = st.columns([1,2])
    with col1:
        modeloptions1 = ["gpt-4o-g", "gpt-4o", "gpt-4-turbo", "gpt-35-turbo"]

        # Create a dropdown menu using selectbox method
        selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
        count += 1
        # Image uploader
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])  

        # Display the uploaded image
        if uploaded_file is not None:
            #image = Image.open(uploaded_file)
            image_bytes = uploaded_file.read()
    
            # Open the image using PIL
            image = Image.open(io.BytesIO(image_bytes))   
            st.image(image, caption='Uploaded Image.', use_column_width=True)  
            image.convert('RGB').save('temp.jpeg')
    with col2:
        st.write("### Chat Interface")
        #prompt = st.chat_input("You: ", key="user_input")
        #with st.sidebar:
        #    messages = st.container(height=300)
        messages = st.container(height=300)
        if prompt := st.chat_input("i would like to add 7 apples and 5 oranges", key="user_input"):
            messages.chat_message("user").write(prompt)
            #messages.chat_message("assistant").write(f"Echo: {prompt}")
            itemtoadd = processinput(prompt, selected_optionmodel1)
            #print("Item to add:", itemtoadd)
            item = json.loads(itemtoadd.replace("```", "").replace("json", "").replace("`",""))
            # add_to_cart(item["product"], item["quantity"])
            add_to_cart(item)
            cart_json = json.dumps(item, indent=2)
            messages.chat_message("assistant").write(cart_json)
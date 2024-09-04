import streamlit as st
import cv2
import torch
import numpy as np
from PIL import Image
from dotenv import dotenv_values
from pathlib import Path
#import logging
#logging.basicConfig(level=logging.INFO)

# Load the manually downloaded model weights
#model = torch.load('yolov5s.pt')
#model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, force_reload=True)
#model.eval()  # Set the model to evaluation mode

#@st.cache_resource
#def load_model():
#    # Ensure the model is loaded only once
#    #return torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, force_reload=True)
#    return torch.load('yolov5s.pt')

st.write("Starting to load model...")
#logging.info("Starting to load model...")

model_path = Path("yolov5s.pt")
# Load the model
model = torch.load(model_path, map_location=torch.device('cpu'))  # Map to CPU if not using CUDA

# If necessary, extract the model from the loaded dictionary (depends on how the model was saved)
if isinstance(model, dict) and 'model' in model:
    model = model['model']

# Set the model to evaluation mode
# model.eval()
st.write("Model loaded successfully!")
#logging.info("Model loaded successfully!")

#print(f"Model weights saved as {model_path}")
config = dotenv_values("env.env")

# RTSP stream URL
# RTSP_URL = "rtsp://your_camera_ip_address/your_stream"
RTSP_URL = config["RTSP_URL"]

# Streamlit app
# st.title("RTSP Camera Stream with YOLOv5")

# Function to get stream frames and infer
def get_stream_frame(rtsp_url):

    #model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, force_reload=True)
    #model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=True)

    # Save the model weights
    #model_path = 'yolov5s.pt'
    #torch.save(model.state_dict(), model_path)
    #model.eval()

    cap = cv2.VideoCapture(rtsp_url)

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to retrieve frame from stream.")
                break

            # Apply YOLOv5 inference
            results = model(frame)

            # Render results on the frame
            result_frame = np.squeeze(results.render())

            # Convert frame to RGB for Streamlit display
            result_frame_rgb = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
            result_frame_pil = Image.fromarray(result_frame_rgb)

            st.image(result_frame_pil, caption="YOLOv5 Inference", use_column_width=True)

            # Stop stream on 'q' press
            if st.button("Stop Stream"):
                cap.release()
                break
        except Exception as e:
            st.error(f"An error occurred: {e}")
            break
        finally:
            cap.release()



def videoinfyolov5():
    

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("bblogo1.png", use_column_width=True)
    with col2:
        # Start the stream and inference
        if st.button("Start Stream"):
            get_stream_frame(RTSP_URL)
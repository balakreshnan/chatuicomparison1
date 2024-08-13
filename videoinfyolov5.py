import streamlit as st
import cv2
import torch
import numpy as np
from PIL import Image
from dotenv import dotenv_values

config = dotenv_values("env.env")

# Load YOLOv5 model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
# Download the YOLOv5s model weights
# Set page configuration
# st.set_page_config(page_title="YOLOv5 RTSP Stream", page_icon=":video_camera:", layout="wide")

# Load the manually downloaded model weights
model = torch.load('yolov5s.pt')

#print(f"Model weights saved as {model_path}")

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
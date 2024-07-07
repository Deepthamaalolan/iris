import streamlit as st
from processing import VideoProcessor
from dotenv import load_dotenv
import os

load_dotenv()

st.title("TikTok Video Reviewer")

# Create upload video button
uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov", "mkv"])


if uploaded_file is not None:
    # DO PROCESSING HERE
    video_processor = VideoProcessor(os.getenv("GEMINI_KEY"))
    # frames, json_string = video_processor.detect_words("video_path/IMG_9733.MOV", extend_frames=100)
    
    st.video(uploaded_file)
        
    if st.button("Next"): 
        # DO BLUR HERE
        video_processor.blur_video()
        st.video(uploaded_file)
    
        

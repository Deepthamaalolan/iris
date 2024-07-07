import streamlit as st
from processing import VideoProcessor
import os
import json
import time

# Title and Introduction
st.title("TikTok Video Content Review")
video = st.file_uploader("Upload Video", type=["mp4", "mov"])

if video:
    with st.spinner(text="Processing the video..."):
        video_processor = VideoProcessor(gemini_key=os.getenv("GEMINI_API_KEY"))
        st.write("We have detected a few elements in your video that may violate TikTok's privacy protocols. Please review the following details and take the suggested actions to ensure compliance.") 
        st.markdown("""
                    - :red[Offensive Language Detected]
                    - :red[Sensitive Information Detected]
                    """)
        st.video(video)
        with st.expander("Show Detailed Analysis"):
            # Offensive Language Section
            st.header("Offensive Language Detected")
            st.write("The following offensive text was found in your video:")

            offensive_text = {
                "Text": "Fuck You",
                "Time Stamp": "0:01 - 0:03"
            }

            st.table(offensive_text)

            # Sensitive Information Section
            st.header("Sensitive Information Detected")
            st.write("The following sensitive information was found in your video:")

            sensitive_info = {
                "Credit Card Number": {
                    "Value": "17903249",
                    "Time Stamp": "0:02 - 0:04"
                },
                "ID Information": {
                    "Time Stamp": "0:02 - 0:04"
                }
            }

            st.table(sensitive_info)

            # Suggested Mitigation Section
            st.header("Suggested Mitigation")
            st.write("To comply with TikTok's privacy protocols, we recommend the following action:")

            st.markdown("- **Blur out the video** before uploading to TikTok.")

            # Footer
            st.write("By following these guidelines, you can help ensure that your video complies with TikTok's privacy standards.")

        if st.button("Fix my video"):
            with st.spinner(text="Blurring unwanted elements..."):
                with open("word_frame_dict.json", "r") as f:
                    word_frame_dict = json.load(f)
                video_processor.blur_video_from_word_frame_dict("video_path/IMG_9733 2.MOV", "output_video/output.mp4", 31, word_frame_dict)
                st.write("Your video has been fixed. Please review the updated video below.")
                st.markdown("""
                    - :green[No Offensive Language Detected]
                    - :green[No Sensitive Information Detected]
                    """)
                with open("./output_video/output.mp4", 'rb') as v:
                    st.video(v)
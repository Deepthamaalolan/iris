import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from moviepy.editor import VideoFileClip
import os
import re

# Set the IMAGEIO_FFMPEG_EXE environment variable
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/opt/ffmpeg/bin/ffmpeg"  # Update the path as needed

# Load the .env file
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

def analyze_text_with_llm(text, client):
    prompt = (
        "You are an expert in the Security and Product Abuse Prevention team at TikTok, "
        "reviewing a TikTok video before it gets published. "
        "Read the following text extracted from the video's audio and identify any potential offensive language or sensitive information. "
        "For each issue identified, state specifically what the information was and why it is considered offensive or sensitive. "
        "Text: {text}"
    ).format(text=text)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in the Security and Product Abuse Prevention team at TikTok."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    return response.choices[0].message.content.strip()

def extract_audio_from_video(video_file):
    video = VideoFileClip(video_file)
    audio_file = "audio.wav"
    video.audio.write_audiofile(audio_file)
    return audio_file

def transcribe_audio(audio_file):
    import openai
    openai.api_key = api_key
    audio_file = open(audio_file, "rb")
    transcript = openai.Audio.transcribe(". ", audio_file)
    return transcript['text']

def clean_text(text):
    # Remove non-XML compatible characters
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+', '', text)
    return text

def main():
    st.header("TikTok Video Content Analyzer 🚨")
    
    # File uploader for video files
    uploaded_file = st.file_uploader("Upload Video File", type=['mp4', 'avi', 'mov', 'mkv'])

    if uploaded_file is not None:
        try:
            # Extract audio from video
            audio_file = extract_audio_from_video(uploaded_file)
            
            # Transcribe audio to text
            text = transcribe_audio(audio_file)
            
            if not text:
                st.error("Unable to transcribe text from the uploaded video. Please check the file and try again.")
                return
            
            text = clean_text(text)
            store_name = uploaded_file.name.rsplit('.', 1)[0]
            st.write(f'Processing file: {store_name}')
    
            # Load or create FAISS vector store
            if os.path.exists(f"{store_name}.faiss"):
                VectorStore = FAISS.load_local(store_name)
                st.write('Embeddings Loaded from the Disk')
            else:
                embeddings = OpenAIEmbeddings(openai_api_key=api_key)
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                chunks = text_splitter.split_text(text=text)
                VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
                VectorStore.save_local(store_name)
    
            findings = analyze_text_with_llm(text, client)
            
            st.subheader("Identified Offensive Language or Sensitive Information:")
            st.write(findings)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
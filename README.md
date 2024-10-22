# Iris

**License**: MIT  
**Author**: @chrislevn @stephanienguyen2020 @Deepthamaalolan @LiyuZer
## Overview
Iris is a project designed to create a censorship engine for TikTok, focusing on redacting sensitive and inappropriate content within videos. This solution addresses both video and audio mediums, providing a holistic approach to content moderation.
![Flow Image](/images/flow.png)
## Motivation
In today's data-rich world, social media platforms like TikTok are often inundated with harmful and inappropriate content. As human moderation becomes increasingly challenging, computerized supervision is essential. Iris serves as a fully autonomous system that enables companies and users to blur out sensitive or inappropriate information seamlessly. We wanted to create a special censorship engine, that will sanitize a video so that we won't have to do it ourselves. Enabling us in creating a safer, cleaner internet. 

## Built With
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenAI Whisper API](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Gemini API](https://img.shields.io/badge/Gemini-00A1E0?style=for-the-badge&logo=gemini&logoColor=white)
![EasyOCR](https://img.shields.io/badge/EasyOCR-FFD700?style=for-the-badge&logo=easyocr&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)

## Features
- **Detailed Quality Check**: Utilizes Gen AI to scan through detected words and audio clips, summarizing the content identified.
- **OCR and Whisper Speech to Text API Integration**: Employs Easy OCR models for text detection in videos and Whisper for audio speech detection.
- **Video Censorship**: Automatically blurs regions of interest containing harmful or sensitive information.
- **Audio Censorship**: Censors audio containing harmful or sensitive information.
- **Sample UI**: Demonstrates the censorship process through a sample user interface.

## Getting Started
1. Clone the repository:
  git clone [repository-url]
2. Install the required packages:
  pip install -r requirements.txt
3. Create environment
    touch .env
    echo GEMINI_API_KEY=[Your API Key] > .env
5. Run the application using Streamlit:
   streamlit run ui.py

License
Released under the MIT License.

Disclaimer
Please note that while Iris strives for accurate censorship, there may still be instances where videos contain inappropriate content due to errors in the censorship process.

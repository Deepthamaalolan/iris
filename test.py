from dotenv import load_dotenv
import os
from processing import VideoProcessor

load_dotenv()

video_processor = VideoProcessor(os.getenv("GEMINI_KEY"))
# frames, json_string = video_processor.detect_words("video_path/IMG_9733.MOV")

# print(frames, json_string)

video_processor.collect__text_from_json("word_frame_dict.json")

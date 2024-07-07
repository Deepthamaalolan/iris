import cv2  # for VS Code user
import easyocr
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import google.generativeai as genai
import moviepy.editor as mp
import whisper_timestamped as whisper


load_dotenv(override=True)
LIMIT_FRAME = 1
class VideoProcessor:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key

    def detect_words(self, video_path, extend_frames=3):
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
        reader = easyocr.Reader(['en'])
        word_frame_dict = {}
        frames = []
        frame_number = 0
        # add loading message
        print("Loading...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = reader.readtext(frame)
            for bbox, text, prob in results:
                if prob > 0.1:
                    if text not in word_frame_dict:
                        word_frame_dict[text] = []
                    bbox_converted = [(int(point[0]), int(point[1])) for point in bbox]
                    # Extend frame range
                    extended_frames = [(fn, bbox_converted) for fn in range(max(0, frame_number - extend_frames), frame_number + extend_frames + 1)]
                    word_frame_dict[text].extend(extended_frames)
            print("Converted frame number: ", frame_number)
            frames.append(frame)
            frame_number += 1

        cap.release()
        cv2.destroyAllWindows()

        json_string = json.dumps(word_frame_dict, indent=4)
        return frames, json_string

    def blur_video(self, frames, output_video_path, blur_radius, word_frame_dict):
        if not frames:
            return

        frame_height, frame_width, _ = frames[0].shape
        fps = 30
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
        margin = 50

        for frame_number, frame in enumerate(frames):
            for word, details in word_frame_dict.items():
                for frame_num, bbox in details:
                    if frame_number == frame_num:
                        top_left, bottom_right = (bbox[0], bbox[2])
                        top_left = (max(top_left[0] - margin, 0), max(top_left[1] - margin, 0))
                        bottom_right = (min(bottom_right[0] + margin, frame_width), min(bottom_right[1] + margin, frame_height))
                        roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                        blurred_roi = cv2.GaussianBlur(roi, (blur_radius, blur_radius), 0)
                        frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = blurred_roi

            out.write(frame)

        out.release()
        cv2.destroyAllWindows()

    def collect__text_from_json(self, json_path):
        with open(json_path, "r") as f:
            frame_value_dict = json.load(f)
        key_list = []
        for key, bbox in frame_value_dict.items():
            ai_result = self.ai_grading(key)
            json_ai_result = json.loads(ai_result)
            for requirement, value in json_ai_result.items():
                if value == "YES":
                    key_list.append(key)

        for key, bbox in frame_value_dict.items():
            for i in range(len(key_list)):
                if key_list[i] == key:
                    self.blur_video(bbox, "output_video/output.mp4", 30,frame_value_dict)

    def ai_grading(self, text_input):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")
        response = self.model.generate_content(
                        """
                        You are a helpful assistant help me checking the quality of the a single word. The text must follow these rule:
                            - No sensitive information
                            - No harmful content
                            - No inappropriate content
                            - No number or name or anything that can provide info
                            For each criteria, please provide a an answer in YES, NO, OR N/A format.
                            Return the score for each criteria in the following format:
                            {"sensitive_information": <ANSWER>, "harmful_content": <ANSWER>, "inappropriate_content": <ANSWER>, "leak_info": <ANSWER>}
                            If you don't have any answer, please return {}
                            Quality check for the word: """ + text_input
                    )
        return response.text

    def video_to_audio(self, video_path, audio_path):
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(video_path)

    def audio_to_text(self, audio_path):
        audio = whisper.load_audio(audio_path)

        model = whisper.load_model("tiny", device="cpu")

        result = whisper.transcribe(model, audio, language="fr")

        return json.dumps(result, indent = 2, ensure_ascii = False)
    
    def process_audio(self, video_path):
        self.video_to_audio(video_path, "audio_output/test.wav")
        stt_result = self.audio_to_text("audio_output/test.wav")
        key_list = []
        for key, value in stt_result.items():
            ai_result = self.ai_grading(stt_result)
            for requirement, value in ai_result.items():
                if value == "YES":
                    key_list.append(key)
                    
        print("Your video has the following words that need to be removed:", key_list)
        return key_list
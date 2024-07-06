import cv2  # for VS Code user
import easyocr
import json
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
LIMIT_FRAME = 1

import cv2
import easyocr
import json


class VideoProcessor:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key

    def detect_words(self, input_video_path, extend_frames=3):
        cap = cv2.VideoCapture(input_video_path)
        reader = easyocr.Reader(['en'])
        word_frame_dict = {}
        frames = []
        frame_number = 0

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

    def collect_text(self, json_input_path):
        with open(json_input_path, "r") as f:
            frame_value_dict = json.load(f)

        # To get all keys as a list
        keys_list = list(frame_value_dict.keys())
        # print(keys_list)

        # # To print all keys
        # for key in frame_value_dict.keys():
        #     print(ai_grading(key))

        keys_list[0] = "Fuck"  # Test
        for i in range(len(keys_list)):
            grading_result = ai_grading(keys_list[i])
            json_text_grading_result = grading_result.split(" - ")[0]
            if json.loads(json_text_grading_result) != {}:
                print(keys_list[i], grading_result)

                # Blur video

    def ai_grading(self, text_input):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                    
                    You are a helpful assistant help me checking the quality of the a single word. The text must follow these rule:
                    - No sensitive information
                    - No harmful content
                    - No inappropriate content
                    - No number or name or anything that can provide info
                    
                    For each criteria, please provide a an answer in YES, NO, OR N/A format.
                    
                    Return the score for each criteria in the following format:
                    {"sensitive_information": <ANSWER>, "harmful_content": <ANSWER>, "inappropriate_content": <ANSWER>, "leak_info": <ANSWER>}
                    
                    If you don't have any answer, please return {} - <explain why>.
                    
                    """,
                },
                {
                    "role": "user",
                    "content": "Base on the system guide, help me grade this word {}".format(
                        text_input
                    ),
                },
            ],
        )

        if completion.choices:
            return completion.choices[0].message.content
        else:
            return ""


if __name__ == "__main__":
    input_video_path = "video_input/IMG_9733.MOV"
    output_video_path = "video_output/output.mp4"
    input_json_path = "json_input/test.json"
    # blur_radius = 25

    # frames, frame_value_dict = detect_words(input_video_path)
    # print(frames, frame_value_dict)
    # blur_video(frames, output_video_path, blur_radius, frame_value_dict)

    collect_text(input_json_path)

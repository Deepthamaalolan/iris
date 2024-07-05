import cv2
import easyocr
import json
import numpy as np

def detect_words(input_video_path):
    cap = cv2.VideoCapture(input_video_path)
    reader = easyocr.Reader(['en'])
    frame_value_dict = {}  # The format will be frame number : detected words
    frames = []

    frame_number = 0
    margin = 50  # Margin to increase the area around the text

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = reader.readtext(frame)
        words = []

        for (bbox, text, prob) in results:
            if prob > 0.1:
                words.append((bbox, text))

        if words:
            frame_value_dict[int(frame_number)] = words  # Convert frame_number to int

        frames.append(frame)
        frame_number += 1
        print(f'Detecting words in frame {frame_number}', end='\r')

    cap.release()
    cv2.destroyAllWindows()

    # Convert all bbox coordinates to native Python int
    for frame_num in frame_value_dict:
        frame_value_dict[frame_num] = [((int(top_left[0]), int(top_left[1]), int(bottom_right[0]), int(bottom_right[1])), text) 
                                       for (top_left, top_right, bottom_right, bottom_left), text in frame_value_dict[frame_num]]

    json_string = json.dumps(frame_value_dict, indent=4)
    return frames, json_string

def blur_video(frames, output_video_path, blur_radius, frame_value_dict):
    if not frames:
        print("No frames to process.")
        return

    frame_height, frame_width, _ = frames[0].shape
    fps = 30  # Set to a default value or retrieve from the original video if needed

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    frame_number = 0
    margin = 50  # Margin to increase the blur area around the text

    for frame in frames:
        if str(frame_number) in frame_value_dict:
            for bbox, text in frame_value_dict[str(frame_number)]:
                (top_left, bottom_right) = (bbox[:2], bbox[2:])  # Extract top_left and bottom_right
                top_left = tuple([int(val) - margin for val in top_left])
                bottom_right = tuple([int(val) + margin for val in bottom_right])

                top_left = (max(top_left[0], 0), max(top_left[1], 0))
                bottom_right = (min(bottom_right[0], frame_width), min(bottom_right[1], frame_height))

                if top_left[1] < bottom_right[1] and top_left[0] < bottom_right[0]:  # Check if ROI is non-empty
                    roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                    blurred_roi = cv2.GaussianBlur(roi, (blur_radius, blur_radius), 0)
                    frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = blurred_roi

        out.write(frame)
        frame_number += 1
        print(f'Blurring words in frame {frame_number}', end='\r')

    out.release()
    cv2.destroyAllWindows()
    print(f'Video processing complete. Output saved to {output_video_path}')


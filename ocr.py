import cv2
import easyocr
import json


def detect_words(input_video_path, extend_frames=3):
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

def blur_video(frames, output_video_path, blur_radius, word_frame_dict):
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

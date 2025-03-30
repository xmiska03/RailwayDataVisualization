import cv2
import numpy as np

"""
# create pictures from video
cap = cv2.VideoCapture("data/youtube_video.mkv")
frame_number = 0
assinged_number = 0
success = True

while success:
    # read frame
    success, frame = cap.read()
    
    # save from 420th frame, every second frame, 500 frames
    # assign numbers from 0 to 499
    if success and frame_number >= 410 and frame_number % 2 == 0:
        cv2.imwrite(f"assets/video_frames/frame_{assinged_number}.jpg", frame)
        print("Extracted frame: ", assinged_number, "made from: ", frame_number)
        assinged_number += 1

        if assinged_number >= 500:
            exit()
    
    frame_number += 1

cap.release()

"""
# create video from pictures
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for mp4 format
out = cv2.VideoWriter("../assets/video_prolonged.mp4", fourcc, 25, (2048,1536))

for i in range(500):
    frame = cv2.imread(f"video_frames/{i}.jpg")
    out.write(frame)

# prolong the video to the needed length by adding white frames
white_frame = np.ones((1536, 2048, 3), dtype=np.uint8) * 255
for _ in range(988):
    out.write(white_frame)

out.release()

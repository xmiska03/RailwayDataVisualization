import cv2

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

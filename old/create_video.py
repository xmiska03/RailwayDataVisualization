# creates a frames.txt file which can be used to create a video from the frames

import csv

timestamps = []

# load timestamps
with open('../data/Basler_8.csv', 'r') as timestamps_file:
    reader = csv.reader(timestamps_file)
    for i, row in enumerate(reader):
        if i >= 1500:
            break
        timestamp = row[1]
        timestamps.append(int(timestamp))

# create frames.txt
with open('frames.txt', 'w') as f:
    for i in range(len(timestamps) - 1):
        print(f"file '../data/img_cam/{i}.jpg'", file=f)
        duration = (timestamps[i+1] - timestamps[i]) / 1000.0  # ms to seconds
        print(f'duration {duration:.6f}', file=f)
    print(f"file '../data/img_cam/{len(timestamps) - 1}.jpg'", file=f)

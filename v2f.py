import cv2
import os

# Path to the video file
video_path = "../demo.mp4"

# Directory to save frames
output_dir = "frames_output"
os.makedirs(output_dir, exist_ok=True)

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video was successfully opened
if not cap.isOpened():
    print("Error: Cannot open the video file")
    exit()

# Frame counter
frame_count = 0

# Loop through the video frames
while True:
    ret, frame = cap.read()  # Read a frame
    if not ret:  # Break if no frame is returned (end of video)
        break

    # Save frame as an image file
    frame_filename = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
    cv2.imwrite(frame_filename, frame)
    print(f"Saved {frame_filename}")

    frame_count += 1

# Release the video capture object
cap.release()
print(f"Extracted {frame_count} frames to '{output_dir}'")

import cv2
from PIL import Image
import os

video_path = r"C:\Users\nitin\Downloads\crosssword_assignment\ai-agent-intern-test\WhatsApp Video 2026-08-26 at 1.16.22 AM.mp4"
output_path = "output.gif"
fps = 10

print("Loading video...")
cap = cv2.VideoCapture(video_path)
original_fps = cap.get(cv2.CAP_PROP_FPS)
frame_step = max(1, int(original_fps / fps))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Total frames: {total_frames}")
print(f"Extracting frames...")

frames = []
count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    if count % frame_step == 0:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(frame_rgb))
    count += 1

cap.release()

print(f"Creating GIF ({len(frames)} frames)...")
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=int(1000/fps), loop=0, optimize=False)
print(f"Done! GIF saved as: output.gif")

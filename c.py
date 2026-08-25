import imageio
from PIL import Image

video_path = r"C:\Users\nitin\Downloads\crosssword_assignment\ai-agent-intern-test\WhatsApp Video 2026-08-26 at 1.16.22 AM.mp4"
output_path = "output.gif"
fps = 10

print("Loading video...")
video = imageio.get_reader(video_path)
original_fps = video.get_meta_data()['fps']
frame_step = max(1, int(original_fps / fps))

print("Extracting frames...")
frames = []
for i, frame in enumerate(video):
    if i % frame_step == 0:
        frames.append(Image.fromarray(frame))

print(f"Converting to GIF ({len(frames)} frames)...")
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=int(1000/fps), loop=0)
print(f"Done! GIF saved as: output.gif")

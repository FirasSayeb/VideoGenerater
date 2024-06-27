from flask import Flask, request, render_template, send_file
from PIL import Image
import os
from moviepy.editor import ImageSequenceClip

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("file")
    duration = float(request.form.get("duration", 1))  # Get duration from form data, default to 1 if not provided
    image_paths = []
    for file in uploaded_files:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        image_paths.append(filepath)
    
    video_path = create_video(image_paths, duration)
    return send_file(video_path, as_attachment=True)

def resize_image(image_path, size):
    with Image.open(image_path) as img:
        img_resized = img.resize(size)
        resized_path = os.path.join(UPLOAD_FOLDER, f"resized_{os.path.basename(image_path)}")
        img_resized.save(resized_path)
        return resized_path

def create_video(image_paths, duration):
    target_size = (640, 480)  # Define the target size for all images
    resized_paths = []
    for path in image_paths:
        resized_path = resize_image(path, target_size)
        resized_paths.append(resized_path)
    
    # Debugging: Print sizes of resized images
    for path in resized_paths:
        with Image.open(path) as img:
            print(f"Image {path} size: {img.size}")

    # Check if all images are of the same size
    sizes = set()
    for path in resized_paths:
        with Image.open(path) as img:
            sizes.add(img.size)
    
    if len(sizes) != 1:
        raise ValueError(f"All images must be of the same size. Detected sizes: {sizes}")

    clip = ImageSequenceClip(resized_paths, durations=[duration] * len(resized_paths))
    video_path = os.path.join(UPLOAD_FOLDER, 'output_video.mp4')
    clip.write_videofile(video_path, fps=24)
    return video_path

if __name__ == "__main__":
    app.run(debug=True)

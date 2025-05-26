import gradio as gr
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, vfx
import os
import re
import tempfile
import cv2
import numpy as np

def cut_video(video_file, start1, end1, start2, end2, start3, end3):
    try:
        video = VideoFileClip(video_file.name)
        duration = video.duration

        if start1 >= end1 or start2 >= end2 or start3 >= end3:
            return "Error: Start time must be less than end time.", None, None, None
        if end1 > duration or end2 > duration or end3 > duration:
            return f"Error: One or more cuts exceed the video duration ({duration:.2f} seconds).", None, None, None
        
        cut1, cut2, cut3 = video.subclip(start1, end1), video.subclip(start2, end2), video.subclip(start3, end3)
        filenames = ["cut1.mp4", "cut2.mp4", "cut3.mp4"]
        
        for filename, cut in zip(filenames, [cut1, cut2, cut3]):
            cut.write_videofile(filename, codec='libx264', audio_codec='aac')
        
        return "Cuts successful.", filenames[0], filenames[1], filenames[2]
    except Exception as e:
        return f"Error cutting video: {str(e)}", None, None, None

def merge_videos(video1_file, video2_file, video3_file):
    try:
        if not video1_file or not video2_file or not video3_file:
            return "Error: Please upload all three videos.", None
        
        final_video = concatenate_videoclips([VideoFileClip(f.name) for f in [video1_file, video2_file, video3_file]])
        output_filename = "merged_video.mp4"
        final_video.write_videofile(output_filename, codec='libx264', audio_codec='aac')
        return "Merging successful!", output_filename
    except Exception as e:
        return f"Error merging videos: {str(e)}", None

def change_video_resolution(video_file, quality):
    try:
        video = VideoFileClip(video_file.name)
        resolutions = {"480p": (854, 480), "720p": (1280, 720), "1080p": (1920, 1080), "1440p": (2560, 1440), "4K": (3840, 2160)}
        if quality not in resolutions:
            return "Error: Invalid quality selection.", None
        
        resized_video = video.resize(resolutions[quality])
        output_path = "output_video.mp4"
        resized_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        return output_path
    except Exception as e:
        return f"Error: {str(e)}", None
        
def edit_video(video_file, edit_text):
    try:
        video = VideoFileClip(video_file.name)

        # Trim Command
        trim_match = re.search(r"trim\s*(\d+)\s*(to|-)\s*(\d+)", edit_text, re.IGNORECASE)
        if trim_match:
            start_time, end_time = int(trim_match.group(1)), int(trim_match.group(3))
            if 0 <= start_time < end_time <= video.duration:
                video = video.subclip(start_time, end_time)
            else:
                return "Error: Invalid trim range.", None

        if any(keyword in edit_text.lower() for keyword in ["grayscale", "black and white"]):
            video = video.fx(vfx.blackwhite)

        speed_match = re.search(r"speed\s*(up|down)\s*(\d+\.?\d*)", edit_text, re.IGNORECASE)
        if speed_match:
            factor = float(speed_match.group(2))
            video = video.fx(vfx.speedx, factor if "up" in speed_match.group(1).lower() else 1 / factor)

        for angle in [90, 180, 270]:
            if f"rotate {angle}" in edit_text.lower():
                video = video.rotate(angle)
                break

        if any(keyword in edit_text.lower() for keyword in ["flip horizontally", "mirror effect"]):
            video = video.fx(vfx.mirror_x)
        if "flip vertically" in edit_text.lower():
            video = video.fx(vfx.mirror_y)

        fade_match = re.search(r"fade (in|out) (\d+) seconds", edit_text, re.IGNORECASE)
        if fade_match:
            fade_time = int(fade_match.group(2))
            video = video.fadein(fade_time) if "in" in fade_match.group(1).lower() else video.fadeout(fade_time)

        brightness_match = re.search(r"brightness (increase|decrease) (\d+\.?\d*)", edit_text, re.IGNORECASE)
        if brightness_match:
            factor = float(brightness_match.group(2))
            video = video.fx(vfx.colorx, 1 + factor if "increase" in brightness_match.group(1).lower() else 1 - factor)

        contrast_match = re.search(r"contrast (increase|decrease) (\d+\.?\d*)", edit_text, re.IGNORECASE)
        if contrast_match:
            factor = float(contrast_match.group(2))
            video = video.fx(vfx.lum_contrast, contrast=10 * factor if "increase" in contrast_match.group(1).lower() else -10 * factor)

        if "reverse" in edit_text.lower():
            video = video.fx(vfx.time_mirror)

        resize_match = re.search(r"resize (\d+)%", edit_text, re.IGNORECASE)
        if resize_match:
            scale_factor = int(resize_match.group(1)) / 100
            video = video.resize(scale_factor)

        border_match = re.search(r"border (\d+)", edit_text, re.IGNORECASE)
        if border_match:
            border_size = int(border_match.group(1))
            video = video.margin(border_size, color=(0, 0, 0))

        output_file = "edited_video.mp4"
        video.write_videofile(output_file, codec='libx264', audio_codec='aac')
        return "Editing Successful", output_file
    except Exception as e:
        return f"Error: {str(e)}", None

def process_image(image, brightness=0, contrast=0, hue=0, saturation=0, flip=False, grayscale=False, rotate=0, blur=0, sharpen=False, crop=False):
    if image is None:
        return "Error: No image uploaded"
    
    image_path = image.name
    img = cv2.imread(image_path)
    
    if img is None:
        return "Error: Unable to read image. Ensure it's a valid image file."
    
    img = cv2.convertScaleAbs(img, alpha=1 + contrast / 100, beta=brightness)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h = cv2.add(h, hue)
    s = cv2.add(s, saturation)
    hsv = cv2.merge([h, s, v])
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    if flip:
        img = cv2.flip(img, 1)

    if grayscale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if rotate:
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, rotate, 1.0)
        img = cv2.warpAffine(img, M, (w, h))

    blur = int(blur)
    if blur > 0:
        img = cv2.GaussianBlur(img, (2 * blur + 1, 2 * blur + 1), 0)

    if sharpen:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    if crop:
        h, w = img.shape[:2]
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        img = img[start_y:start_y+min_dim, start_x:start_x+min_dim]

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    cv2.imwrite(temp_file.name, img)
    
    return temp_file.name

def reset_parameters():
    return 0, 0, 0, 0, False, False, 0, 0, False, False
    
with gr.Blocks(theme="soft") as demo:
    with gr.TabItem("🏠 Home"):
        gr.Markdown("""
        # 🎬 Welcome to Advanced Video Editor
        **Developed by Akilan JD, Adithya J, and Jayavignesh G**  
        *Engineers Exploring the Future of Media and AI*
        
        ## 🔹 Features:
        - ✂️ **Video Cutter**: Trim multiple parts of a video with ease.
        - 🔗 **Video Merger**: Combine multiple video clips seamlessly.
        - 🎚️ **Resolution Changer**: Convert videos to different resolutions (480p, 720p, 1080p, 1440p, 4K).
        - ✂️ **Text-Based Video Editing**: Edit videos using simple text commands.
        - 🖼️ **Image Editor**: Adjust brightness, contrast, hue, sharpness, and more!
        
        🎥 **Enhance your video editing experience with our intuitive and user-friendly interface!**
        """)
    
    with gr.Tabs():
        with gr.TabItem("✂️ Video Cutter"):
            video_input = gr.File(label="Upload Video")
            start1, end1 = gr.Number(label="Start Cut 1"), gr.Number(label="End Cut 1")
            start2, end2 = gr.Number(label="Start Cut 2"), gr.Number(label="End Cut 2")
            start3, end3 = gr.Number(label="Start Cut 3"), gr.Number(label="End Cut 3")
            cut_button = gr.Button("Cut Video")
            status, cut1, cut2, cut3 = gr.Textbox(label="Status"), gr.Video(), gr.Video(), gr.Video()
            cut_button.click(cut_video, inputs=[video_input, start1, end1, start2, end2, start3, end3], outputs=[status, cut1, cut2, cut3])
        
        with gr.TabItem("🔗 Video Merger"):
            vid1, vid2, vid3 = gr.File(label="Upload Video 1"), gr.File(label="Upload Video 2"), gr.File(label="Upload Video 3")
            merge_button = gr.Button("Merge Videos")
            merge_status, final_vid = gr.Textbox(label="Status"), gr.Video()
            merge_button.click(merge_videos, inputs=[vid1, vid2, vid3], outputs=[merge_status, final_vid])
        
        with gr.TabItem("🎚️ Change Resolution"):
            res_video = gr.File(label="Upload Video")
            quality_input = gr.Dropdown(["480p", "720p", "1080p", "1440p", "4K"], label="Select Quality", value="720p")
            convert_button = gr.Button("Convert Quality")
            converted_video = gr.Video()
            convert_button.click(change_video_resolution, inputs=[res_video, quality_input], outputs=converted_video)
            
        with gr.TabItem("✂️ Text-Based Video Editing"):
            vid_input = gr.File(label="Upload Video")
            edit_text = gr.Textbox(label="Describe your edits (e.g., 'Trim 0 to 5, add grayscale, speed up 2x')")
            edit_button = gr.Button("Edit Video")
            edit_status = gr.Textbox(label="Status")
            edited_vid = gr.Video()
            edit_button.click(edit_video, inputs=[vid_input, edit_text], outputs=[edit_status, edited_vid])

        with gr.TabItem("🖼️ Image Editor"):
            with gr.Row():
                with gr.Column():
                    image_input = gr.File(type="filepath", label="Upload Image")
                    brightness = gr.Slider(-100, 100, value=0, label="Brightness")
                    contrast = gr.Slider(-100, 100, value=0, label="Contrast")
                    hue = gr.Slider(-100, 100, value=0, label="Hue")
                    saturation = gr.Slider(-100, 100, value=0, label="Saturation")
                    flip = gr.Checkbox(label="Flip Image")
                    grayscale = gr.Checkbox(label="Convert to Black & White")
                    rotate = gr.Slider(0, 180, value=0, label="Rotate")
                    blur = gr.Slider(0, 10, step=1, value=0, label="Blur")
                    sharpen = gr.Checkbox(label="Sharpen Image")
                    crop = gr.Checkbox(label="Crop to Square")
                    clear_button = gr.Button("Clear")
                with gr.Column():
                    output_image = gr.Image(type="filepath", label="Processed Image")
            
            inputs = [image_input, brightness, contrast, hue, saturation, flip, grayscale, rotate, blur, sharpen, crop]
            for inp in inputs:
                inp.change(process_image, inputs=inputs, outputs=output_image)
            clear_button.click(reset_parameters, outputs=[brightness, contrast, hue, saturation, flip, grayscale, rotate, blur, sharpen, crop])

demo.launch(server_name="127.0.0.1", server_port=8080)



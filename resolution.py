import gradio as gr
from moviepy.editor import VideoFileClip
import os

# Function to change video resolution
def change_video_resolution(video_file, quality):
    try:
        # Load the uploaded video
        video = VideoFileClip(video_file.name)
        
        # Set resolution based on user input
        if quality == "480p":
            new_resolution = (854, 480)
        elif quality == "720p":
            new_resolution = (1280, 720)
        elif quality == "1080p":
            new_resolution = (1920, 1080)
        else:
            return "Error: Invalid quality selection.", None

        # Resize the video
        resized_video = video.resize(new_resolution)
        
        # Output file path
        output_path = "output_video.mp4"
        resized_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        return output_path  # Return the file path for Gradio preview
    
    except Exception as e:
        return f"Error: {str(e)}", None


# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## Video Quality Adjuster")
    
    # File input for video upload
    video_input = gr.File(label="Upload Video")
    
    # Drop-down to select the video quality
    quality_input = gr.Dropdown(["480p", "720p", "1080p"], label="Select Quality", value="720p")
    
    # Preview window for the uploaded video
    video_preview = gr.Video(label="Original Video")
    
    # Button to adjust the quality
    convert_button = gr.Button("Convert Video Quality")
    
    # Output video preview window
    output_video = gr.Video(label="Converted Video")
    
    # Event for previewing the uploaded video
    video_input.change(lambda file: file.name, inputs=video_input, outputs=video_preview)
    
    # Event for changing the video resolution
    convert_button.click(change_video_resolution, inputs=[video_input, quality_input], outputs=output_video)

# Launch the Gradio app
demo.launch()

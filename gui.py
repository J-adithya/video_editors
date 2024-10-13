import gradio as gr
from moviepy.editor import VideoFileClip

# Function to cut the video into three segments based on user input
def cut_video(video_file, start1, end1, start2, end2, start3, end3):
    try:
        # Load video from the uploaded file
        video = VideoFileClip(video_file.name)
        duration = video.duration

        # Ensure valid time ranges
        if start1 >= end1 or start2 >= end2 or start3 >= end3:
            return "Error: Start time must be less than end time.", None, None, None
        
        if end1 > duration or end2 > duration or end3 > duration:
            return f"Error: One or more cuts exceed the video duration ({duration:.2f} seconds).", None, None, None
        
        # Cutting segments
        cut1 = video.subclip(start1, end1)
        cut2 = video.subclip(start2, end2)
        cut3 = video.subclip(start3, end3)
        
        # Define filenames
        filenames = ["cut1.mp4", "cut2.mp4", "cut3.mp4"]
        cuts = [cut1, cut2, cut3]
        
        # Save segments to files
        for filename, cut in zip(filenames, cuts):
            cut.write_videofile(filename, codec='libx264', audio_codec='aac')
        
        # Return file paths for preview
        return "Cuts successful.", filenames[0], filenames[1], filenames[2]
    
    except Exception as e:
        return f"Error cutting video: {str(e)}", None, None, None

# Function to reset cut fields
def reset_cuts():
    return 0, 0, 0, 0, 0, 0

# Function to show the uploaded video preview
def show_video(video_file):
    return video_file.name

# Gradio interface setup
with gr.Blocks() as demo:
    gr.Markdown("## Video Editor - Make 3 Cuts")
    
    # Load video directly in the preview window
    video_input = gr.File(label="Upload Video for Editing")  # Video upload button
    video_preview = gr.Video(label="Preview Uploaded Video")  # Video preview window
    
    # Start and end times for 3 cuts
    with gr.Row():
        start1 = gr.Number(label="Start time of cut 1 (seconds)", value=0)
        end1 = gr.Number(label="End time of cut 1 (seconds)", value=0)
    with gr.Row():
        start2 = gr.Number(label="Start time of cut 2 (seconds)", value=0)
        end2 = gr.Number(label="End time of cut 2 (seconds)", value=0)
    with gr.Row():
        start3 = gr.Number(label="Start time of cut 3 (seconds)", value=0)
        end3 = gr.Number(label="End time of cut 3 (seconds)", value=0)
    
    # Reset cuts button
    reset_button = gr.Button("Reset Cuts")
    
    # Button to cut the video
    cut_button = gr.Button("Cut Video into Segments")
    
    # Preview windows for 3 segments
    cut_video1 = gr.Video(label="Cut Video Segment 1")
    cut_video2 = gr.Video(label="Cut Video Segment 2")
    cut_video3 = gr.Video(label="Cut Video Segment 3")
    
    # Linking the reset button
    reset_button.click(reset_cuts, outputs=[start1, end1, start2, end2, start3, end3])
    
    # Linking the cut video function
    cut_button.click(cut_video, 
                     inputs=[video_input, start1, end1, start2, end2, start3, end3],
                     outputs=[gr.Textbox(label="Status"), cut_video1, cut_video2, cut_video3])
    
    # Show the uploaded video in the preview window
    video_input.change(show_video, inputs=[video_input], outputs=video_preview)

# Launch the Gradio interface
demo.launch()

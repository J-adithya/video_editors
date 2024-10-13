import gradio as gr
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Function to merge three uploaded videos
def merge_videos(video1_file, video2_file, video3_file):
    try:
        # Check if files are uploaded
        if not video1_file or not video2_file or not video3_file:
            return "Error: Please upload all three videos.", None

        # Load the three videos
        video1 = VideoFileClip(video1_file.name)
        video2 = VideoFileClip(video2_file.name)
        video3 = VideoFileClip(video3_file.name)
        
        # Merge the videos
        final_video = concatenate_videoclips([video1, video2, video3])
        
        # Save the merged video
        output_filename = "merged_video.mp4"
        final_video.write_videofile(output_filename, codec='libx264', audio_codec='aac')
        
        # Return the merged video for preview
        return "Merging successful!", output_filename
    
    except Exception as e:
        return f"Error merging videos: {str(e)}", None

# Gradio interface setup
with gr.Blocks() as demo:
    gr.Markdown("## Video Merger - Upload 3 Videos and Merge Them")

    # Video upload and preview row
    with gr.Row():
        video1_input = gr.File(label="Upload Video 1")
        video2_input = gr.File(label="Upload Video 2")
        video3_input = gr.File(label="Upload Video 3")
    
    # Preview windows for the three uploaded videos
    with gr.Row():
        video1_preview = gr.Video(label="Preview Video 1")
        video2_preview = gr.Video(label="Preview Video 2")
        video3_preview = gr.Video(label="Preview Video 3")
    
    # Button to merge the videos
    merge_button = gr.Button("Merge Videos")
    
    # Preview window for the merged video
    final_video_preview = gr.Video(label="Preview Merged Video")
    
    # Linking the merge button
    merge_button.click(merge_videos, 
                       inputs=[video1_input, video2_input, video3_input],
                       outputs=[gr.Textbox(label="Status"), final_video_preview])
    
    # Show uploaded videos in their respective preview windows
    video1_input.change(lambda file: file.name if file else None, inputs=video1_input, outputs=video1_preview)
    video2_input.change(lambda file: file.name if file else None, inputs=video2_input, outputs=video2_preview)
    video3_input.change(lambda file: file.name if file else None, inputs=video3_input, outputs=video3_preview)

# Launch the Gradio interface
demo.launch()

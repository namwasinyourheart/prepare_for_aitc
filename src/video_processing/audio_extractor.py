
import moviepy as mp
import os

def extract_audio(video_path, audio_path):
    """
    Extracts audio from a video file and saves it as an mp3 file.

    :param video_path: Path to the input video file.
    :param audio_path: Path to save the extracted audio file.
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    print(f"Audio extracted and saved to {audio_path}")

if __name__ == '__main__':
    # Example usage
    video_file = "/home/nampv1/projects/prepare_for_aitc/notebooks/outputs/generated_videos/my_generated_video_0va5nkudxl2p.mp4"
    audio_file = "/home/nampv1/projects/prepare_for_aitc/notebooks/outputs/generated_videos/my_generated_video_0va5nkudxl2p.mp3"
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(audio_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    extract_audio(video_file, audio_file)

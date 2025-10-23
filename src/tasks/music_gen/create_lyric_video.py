from moviepy import *
import os

# 1. Định nghĩa thông tin video và lời bài hát
AUDIO_FILE = "nhac_nen_hao_khi_viet_nam.mp3"
IMAGE_DIR = "images/"
OUTPUT_FILE = "hao_khi_viet_nam_lyric_video.mp4"
VIDEO_DURATION = 0 # Sẽ được cập nhật sau khi tải nhạc

lyrics = [
    ("Sáng Ba Đình rực rỡ cờ bay,", 0, 3), # (text, start_time, end_time)
    ("Diễu binh, diễu hành vang khúc ca này.", 3, 6),
    ("Ba mươi ngàn người chung bước tiến,", 6, 9),
    ("Hào khí ngút trời, đất nước vươn lên.", 9, 12),
    ("Hào khí Việt Nam, sáng ngời muôn nơi,", 12, 15),
    ("Tự hào dân tộc, vang danh khắp trời.", 15, 18),
    ("Tám mươi năm, một chặng đường dài,", 18, 21),
    ("Độc lập, tự do, hạnh phúc mãi mãi.", 21, 24),
    ("Bắc Ninh rực rỡ ánh đèn,", 24, 27),
    ("Nghệ thuật, pháo hoa, lòng người hân hoan.", 27, 30),
    ("Khắp năm châu, kiều bào sum họp,", 30, 33),
    ("Cùng nhau hát vang, tình nghĩa đậm sâu.", 33, 36),
    ("Hào khí Việt Nam, sáng ngời muôn nơi,", 36, 39),
    ("Tự hào dân tộc, vang danh khắp trời.", 39, 42),
    ("Tám mươi năm, một chặng đường dài,", 42, 45),
    ("Độc lập, tự do, hạnh phúc mãi mãi.", 45, 48),
    ("Từ quá khứ đến tương lai,", 48, 51),
    ("Con cháu Lạc Hồng, chung tay dựng xây.", 51, 54),
    ("Khát vọng vươn xa, hội nhập năm châu,", 54, 57),
    ("Việt Nam tỏa sáng, rạng ngời bền lâu.", 57, 60),
    ("Hào khí Việt Nam, sáng ngời muôn nơi,", 60, 63),
    ("Tự hào dân tộc, vang danh khắp trời.", 63, 66),
    ("Tám mươi năm, một chặng đường dài,", 66, 69),
    ("Độc lập, tự do, hạnh phúc mãi mãi.", 69, 72),
]

# 2. Tải nhạc nền và xác định thời lượng video
audio_clip = AudioFileClip(AUDIO_FILE)
VIDEO_DURATION = audio_clip.duration

# 3. Tạo danh sách các ImageClip từ các hình ảnh tĩnh
image_files = sorted([os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))])
image_clips = []
current_time = 0
# Chia đều thời gian cho các hình ảnh
time_per_image = VIDEO_DURATION / len(image_files)
for img_file in image_files:
    clip = ImageClip(img_file, duration=time_per_image)
    image_clips.append(clip.set_start(current_time))
    current_time += time_per_image

# 4. Tạo chuỗi video từ các ImageClip
video_clip = concatenate_videoclips(image_clips, method="compose")
video_clip = video_clip.set_audio(audio_clip)

# 5. Tạo TextClip cho lời bài hát
# Hàm tạo TextClip cho mỗi dòng lyric
def create_text_clip(txt):
    return TextClip(txt, fontsize=70, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)

# Tạo các TextClip và định vị chúng trên video
text_clips = []
for text, start, end in lyrics:
    txt_clip = create_text_clip(text)
    txt_clip = txt_clip.set_duration(end - start).set_start(start)
    # Định vị text ở giữa dưới màn hình
    txt_clip = txt_clip.set_position(("center", "bottom"))
    text_clips.append(txt_clip)

# 6. Ghép các TextClip vào video
final_video = CompositeVideoClip([video_clip] + text_clips)

# 7. Xuất video lyric
final_video.write_videofile(OUTPUT_FILE, fps=24)

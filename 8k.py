from moviepy.editor import (
    TextClip,
    CompositeVideoClip,
    ColorClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
)
import webcolors
import os

def get_font_name(font_path):
    # Get the base name of the file (e.g., "RedditMono-SemiBold.ttf")
    base_name = os.path.basename(font_path)
    # Split the base name into name and extension (e.g., "RedditMono-SemiBold" and ".ttf")
    font_name, _ = os.path.splitext(base_name)
    return font_name
def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(rgb_tuple):
    try:
        color_name = webcolors.rgb_to_name(rgb_tuple)
    except ValueError:
        color_name = closest_color(rgb_tuple)
    return color_name

# Constants
DURATION = 10  # 10 seconds
FONT_SIZE = 4000
FONT = "./fonts/SplineSansMono-SemiBold.ttf"  # Ensure you have this font installed or provide the full path
SCREEN_SIZE = (7680, 4320)  # Screen resolution
BACKGROUND_COLOR = (0, 255, 0)  # Green color in RGB format
#BACKGROUND_COLOR = (0, 0, 0)  # Green color in RGB format
TEXT_COLOR = "white"  # White
TEXT_COLOR_ALERT = "red"
ALERT_INTERVAL = 5  # Every 5 seconds

# Load sound files
end_sound_path = "./end_sound_3s.wav"
alert_path = "./alert_sound_1s.wav"

end_sound = AudioFileClip(end_sound_path, fps=44100).set_duration(3)
alert_sound = AudioFileClip(alert_path, fps=44100).set_duration(1)

# Create background clip
background = ColorClip(size=SCREEN_SIZE, color=BACKGROUND_COLOR, duration=DURATION)

# Create timer text clips // Stage 1 Timer -5 sec.
clips_main = []
for t in range(0, DURATION):
    remaining_time = DURATION - t
    seconds = remaining_time % 60
    time_text = f"{seconds:01}"
    if t == 0:
        file_name = time_text.replace(":", "-")
    try:
        text_clip = (
            TextClip(
                time_text,
                fontsize=FONT_SIZE,
                font=FONT,
                color=TEXT_COLOR,
                size=SCREEN_SIZE,
                method="caption",
            )
            .set_duration(1)
            .set_start(t)
            .set_pos("center")
        )
        clips_main.append(text_clip)
    except Exception as e:
        print(f"Error creating text clip at time {t}: {e}")
        exit(1)

# Create blinking alert clips // Stage 2 Timer last 5 sec.
clips_blink = []
for t in range(ALERT_INTERVAL):
    remaining_time = ALERT_INTERVAL - t
    seconds = remaining_time % 60
    time_text = f"{seconds:01}"
    try:
        text_clip = (
            TextClip(
                time_text,
                fontsize=FONT_SIZE,
                font=FONT,
                color=TEXT_COLOR if t % 2 == 0 else TEXT_COLOR_ALERT,
                size=SCREEN_SIZE,
                method="caption",
            )
            .set_duration(1)
            .set_start(t)
            .set_pos("center")
        )
        clips_blink.append(text_clip)
    except Exception as e:
        print(f"Error creating text clip at time {t}: {e}")
        exit(1)

# Create end video with sound // Stage 3
end_text_clip = (
    TextClip(
        "0",
        fontsize=FONT_SIZE,
        font=FONT,
        color=TEXT_COLOR_ALERT,
        size=SCREEN_SIZE,
        method="caption",
    )
    .set_duration(3)
    .set_pos("center")
)

# Composite all clips with background
main_video = CompositeVideoClip([background] + clips_main).set_duration(
    DURATION - ALERT_INTERVAL
)
blink_video = CompositeVideoClip(
    [background.set_duration(ALERT_INTERVAL)] + clips_blink
)
end_video = CompositeVideoClip([background.set_duration(3), end_text_clip]).set_audio(
    end_sound
)

# Add alert sounds to blink video
alert_sounds = [alert_sound.set_start(t) for t in range(ALERT_INTERVAL)]
blink_audio = CompositeAudioClip(alert_sounds)

blink_video = blink_video.set_audio(blink_audio)

# Concatenate all videos
final_video = concatenate_videoclips([main_video, blink_video, end_video])

# Write the final video file
final_video.write_videofile(
    f"./video_{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}_{get_font_name(FONT)}_{get_color_name(BACKGROUND_COLOR)}_countdown_{file_name}.mp4",
    fps=1,
    codec="libx264",
    audio_codec="aac",
    temp_audiofile='temp-audio.m4a',
    remove_temp=True,
)

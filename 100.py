from moviepy.editor import (
    TextClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
    AudioFileClip,
    VideoFileClip,
    CompositeAudioClip
)
from datetime import datetime, timedelta
import webcolors
import os
import gc

def get_font_name(font_path):
    base_name = os.path.basename(font_path)
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
DURATION = 10  # Total duration of the video in seconds
PART_DURATION = 10  # Duration of each part (10 minutes)
FONT_SIZE = 2200
FONT = "./fonts/RubikMonoOne-Regular.ttf"
SCREEN_SIZE = (3840,2160)
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = "white"
TEXT_COLOR_ALERT = "red"
ALERT_INTERVAL = 5

# Load sound files
end_sound_path = "./end_sound_3s.wav"
alert_path = "./alert_sound_1s.wav"
ticks_path = "./ticks.wav"

end_sound = AudioFileClip(end_sound_path, fps=44100).set_duration(3)
alert_sound = AudioFileClip(alert_path, fps=44100).set_duration(1)
ticks_sound = AudioFileClip(ticks_path, fps=44100).set_duration(10)

def create_part(start_time, part_duration, part_index):
    clips_main = []
    for t in range(part_duration):
        remaining_time = DURATION - (start_time + t)
        seconds = 100 if remaining_time % 100 == 0 else remaining_time % 100
        time_text = f"{seconds}"
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

    # Create background clip
    background = ColorClip(size=SCREEN_SIZE, color=BACKGROUND_COLOR, duration=part_duration)
    part_video = CompositeVideoClip([background] + clips_main).set_duration(part_duration).set_audio(ticks_sound)


    part_video.write_videofile(
        f"./part_{part_index}.mp4",
        fps=1,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=f'temp-audio_{part_index}.m4a',
        remove_temp=True,
        ffmpeg_params=['-vcodec', 'h264_videotoolbox', '-acodec', 'aac'],
    )

    del clips_main, background, part_video
    gc.collect()

# Create and save each part
for i in range(0, DURATION, PART_DURATION):
    create_part(i, min(PART_DURATION, DURATION - i), i // PART_DURATION)

# Combine all parts into one final video
parts = [f"./part_{i // PART_DURATION}.mp4" for i in range(0, DURATION, PART_DURATION)]
final_video = concatenate_videoclips([VideoFileClip(part) for part in parts])

# Create blinking alert clips
clips_blink = []
for t in range(ALERT_INTERVAL):
    remaining_time = ALERT_INTERVAL - t
    seconds = 100 if remaining_time % 100 == 0 else remaining_time % 100
    time_text = f"{seconds}"
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

background = ColorClip(size=SCREEN_SIZE, color=BACKGROUND_COLOR, duration=ALERT_INTERVAL)
blink_video = CompositeVideoClip([background] + clips_blink)

alert_sounds = [alert_sound.set_start(t) for t in range(ALERT_INTERVAL)]
blink_audio = CompositeAudioClip(alert_sounds)
blink_video = blink_video.set_audio(blink_audio)

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
background = ColorClip(size=SCREEN_SIZE, color=BACKGROUND_COLOR, duration=3)
end_video = CompositeVideoClip([background, end_text_clip]).set_audio(end_sound)

final_video = concatenate_videoclips([final_video.set_duration(
    DURATION - ALERT_INTERVAL
), blink_video, end_video])
final_video.write_videofile(
    f"./video_{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}_{get_font_name(FONT)}_{get_color_name(BACKGROUND_COLOR)}_countdown_{str(timedelta(seconds=DURATION)).replace(':', '-')}.mp4",
    fps=1,
    codec="libx264",
    audio_codec="aac",
    temp_audiofile='temp-audio.m4a',
    remove_temp=True,
    ffmpeg_params=['-vcodec', 'h264_videotoolbox', '-acodec', 'aac'],
)
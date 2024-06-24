#!/bin/bash

input_file="10.mp4"

# Duration of each segment in seconds (1 hour)
segment_duration=3600

# Total duration of the video in seconds (10 hours and 3 seconds)
total_duration=36003

# Start extracting from the 9th hour (in seconds)
start_time=$((9 * 3600))

# Extract segments in reverse order
for i in {9..0}
do
  output_file="segment_${i}.mp4"
  ffmpeg -i "$input_file" -ss $start_time -t $segment_duration -c copy "$output_file"
  start_time=$((start_time - segment_duration))
done
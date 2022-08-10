from moviepy.editor import VideoFileClip
videoclip = VideoFileClip(".mp4")
videoclip.write_gif(".gif")

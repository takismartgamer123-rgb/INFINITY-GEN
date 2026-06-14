import subprocess
import threading
import os
import time

def start_24h_stream():
    STREAM_KEY = os.getenv("YT_STREAM_KEY")
    if not STREAM_KEY:
        print("❌ مكاش YT_STREAM_KEY في Environment")
        return

    # حط الفيديو تاعك في الريبو باسم video.mp4
    VIDEO_PATH = "video.mp4"

    ffmpeg_cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", VIDEO_PATH,
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
        "-b:v", "2500k", "-maxrate", "2500k", "-bufsize", "5000k",
        "-pix_fmt", "yuv420p", "-g", "60",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        "-f", "flv", f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
    ]

    while True:
        try:
            print("🚫💸 INFINITY GEN راه يبث 24/7 من السحابة")
            subprocess.run(ffmpeg_cmd)
        except Exception as e:
            print(f"البث طاح: {e}")
        print("نعاودو البث بعد 10 ثواني...")
        time.sleep(10)

def run_stream_thread():
    thread = threading.Thread(target=start_24h_stream, daemon=True)
    thread.start()
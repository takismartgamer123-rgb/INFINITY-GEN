import os, subprocess, time
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def run_stream():
    print("📺 [STREAM] نبث الأوفرلاي مؤقتا حتى نطلقو البوت")

    STREAM_KEY = os.environ.get('YT_STREAM_KEY') # بدلناه هنا
    OVERLAY_URL = os.environ.get('OVERLAY_URL')

    if not STREAM_KEY or not OVERLAY_URL:
        print("💀 [STREAM] لازم YT_STREAM_KEY و OVERLAY_URL")
        return

    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

    # 1. شاشة وهمية 720p
    display = Display(visible=0, size=(1280, 720))
    display.start()
    print("📺 [STREAM] الشاشة الوهمية شغالة")

    # 2. نفتحو Chrome على الأوفرلاي
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--kiosk')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280,720')
    chrome_options.add_argument('--hide-scrollbars')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(OVERLAY_URL)
    print(f"📺 [STREAM] فتحت الأوفرلاي: {OVERLAY_URL}")
    time.sleep(8)

    # 3. FFmpeg يصور و يبث
    ffmpeg_cmd = [
        'ffmpeg', '-re',
        '-f', 'x11grab', '-video_size', '1280x720', '-framerate', '30', '-i', ':0',
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2500k', '-maxrate', '2500k', '-bufsize', '5000k',
        '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
        '-pix_fmt', 'yuv420p', '-g', '60',
        '-f', 'flv', rtmp_url
    ]

    while True:
        print("📺 [STREAM] البث شغال...")
        try:
            subprocess.run(ffmpeg_cmd)
        except Exception as e:
            print(f"💀 [STREAM] طاح: {e}")
        time.sleep(5)
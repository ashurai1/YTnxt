import asyncio
import os
import uuid
import yt_dlp

def find_cookies():
    """Find cookies.txt from multiple possible locations"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_paths = [
        os.path.join(project_root, 'cookies.txt'),
        os.path.abspath('cookies.txt'),
        '/opt/render/project/src/cookies.txt',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            print(f"DEBUG: ✅ FOUND COOKIES at {path}")
            return path
    print("DEBUG: ❌ COOKIES NOT FOUND")
    return None

def base_opts():
    """Base yt-dlp options with cookies and web client"""
    # Add Deno to PATH so yt-dlp can find it for signature solving
    deno_path = "/opt/render/.deno/bin"
    if deno_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = deno_path + ":" + os.environ.get("PATH", "")

    opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    cookies_path = find_cookies()
    if cookies_path:
        opts['cookiefile'] = cookies_path
    
    return opts

def get_video_info_sync(url: str):
    opts = base_opts()
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            print(f"DEBUG: ✅ Got info: {info.get('title')}")
            return info
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            raise e

async def get_video_info(url: str):
    return await asyncio.to_thread(get_video_info_sync, url)

def get_available_resolutions(info):
    formats = info.get('formats', [])
    resolutions = set()
    for f in formats:
        height = f.get('height')
        if height and height in [144, 240, 360, 480, 720, 1080]:
            if f.get('vcodec') not in ['none', None]:
                resolutions.add(height)

    if not resolutions:
        for f in formats:
            if f.get('vcodec') not in ['none', None] and f.get('height'):
                resolutions.add(f.get('height'))

    sorted_res = sorted(list(resolutions), reverse=True)
    final_res = [h for h in sorted_res if h in [144, 240, 360, 480, 720, 1080]][:5]

    if not final_res:
        return ["360p"]

    return [f"{h}p" for h in final_res]

def download_video_sync(url: str, height: int, output_path: str):
    opts = base_opts()
    opts.update({
        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        'outtmpl': f'{output_path}.%(ext)s',
        'merge_output_format': 'mp4',
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    for ext in ['mp4', 'mkv', 'webm']:
        if os.path.exists(f"{output_path}.{ext}"):
            return f"{output_path}.{ext}"
    return None

async def download_video(url: str, height: int, temp_dir: str = 'temp') -> str:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    temp_filename = str(uuid.uuid4())
    output_path = os.path.join(temp_dir, temp_filename)

    return await asyncio.to_thread(download_video_sync, url, height, output_path)

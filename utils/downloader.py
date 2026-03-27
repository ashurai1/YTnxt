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

def make_ydl_opts(extra=None):
    """Base ydl opts - no cookies, no client restriction for max compatibility"""
    opts = {
        'quiet': True,
        'no_warnings': True,
    }
    if extra:
        opts.update(extra)
    return opts

def get_video_info_sync(url: str):
    # Try WITHOUT cookies first (uses android_vr which works great)
    opts = make_ydl_opts()
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and info.get('formats'):
                print("DEBUG: ✅ Extracted info without cookies")
                return info
    except Exception as e:
        err = str(e)
        print(f"DEBUG: No-cookie attempt failed: {err}")

    # Retry WITH cookies (for age-restricted or region-locked videos)
    cookies_path = find_cookies()
    if cookies_path:
        print("DEBUG: Retrying with cookies...")
        opts_with_cookies = make_ydl_opts({'cookiefile': cookies_path})
        try:
            with yt_dlp.YoutubeDL(opts_with_cookies) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    print("DEBUG: ✅ Extracted info WITH cookies")
                    return info
        except Exception as e:
            print(f"DEBUG: Cookie attempt also failed: {str(e)}")
            raise e
    else:
        raise Exception("Video extraction failed and no cookies available to retry.")

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
    cookies_path = find_cookies()

    base_opts = {
        'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        'outtmpl': f'{output_path}.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
    }

    # Try without cookies first
    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            ydl.download([url])
        print("DEBUG: ✅ Downloaded without cookies")
        for ext in ['mp4', 'mkv', 'webm']:
            if os.path.exists(f"{output_path}.{ext}"):
                return f"{output_path}.{ext}"
    except Exception as e:
        print(f"DEBUG: No-cookie download failed: {str(e)}, trying with cookies...")

    # Retry with cookies
    if cookies_path:
        opts_with_cookies = {**base_opts, 'cookiefile': cookies_path}
        with yt_dlp.YoutubeDL(opts_with_cookies) as ydl:
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

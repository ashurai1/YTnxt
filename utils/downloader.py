import asyncio
import os
import uuid
import yt_dlp

def get_video_info_sync(url: str):
    # Get the project root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookies_path = os.path.join(base_dir, 'cookies.txt')
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['ios', 'mweb', 'web_embedded', 'tv_embedded']}},
    }
    
    if os.path.exists(cookies_path):
        print(f"DEBUG: Found cookies at {cookies_path}")
        ydl_opts['cookiefile'] = cookies_path
    else:
        print(f"DEBUG: No cookies.txt found at {cookies_path}")
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

async def get_video_info(url: str):
    return await asyncio.to_thread(get_video_info_sync, url)

def get_available_resolutions(info):
    formats = info.get('formats', [])
    resolutions = set()
    for f in formats:
        # More inclusive check: if it has a height and either a vcodec or is a combined format
        height = f.get('height')
        if height and height in [144, 240, 360, 480, 720, 1080]:
            # Ensure it's not an audio-only format being misidentified
            if f.get('vcodec') != 'none':
                resolutions.add(height)
    
    # Fallback: if no specific heights found, try to get anything up to 720p
    if not resolutions:
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                resolutions.add(f.get('height'))
    
    sorted_res = sorted(list(resolutions), reverse=True)
    # Filter to standard YouTube resolutions and limit to top 5
    final_res = [h for h in sorted_res if h in [144, 240, 360, 480, 720, 1080]][:5]
    
    # Absolute fallback to ensure we don't return an empty list if info was fetched
    if not final_res and info.get('formats'):
        return ["360p"]
        
    return [f"{h}p" for h in final_res]

def download_video_sync(url: str, height: int, output_path: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookies_path = os.path.join(base_dir, 'cookies.txt')
    
    ydl_opts = {
        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['ios', 'mweb', 'web_embedded', 'tv_embedded']}},
    }
    
    if os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def download_video(url: str, height: int, temp_dir: str = 'temp') -> str:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(temp_dir, filename)
    
    await asyncio.to_thread(download_video_sync, url, height, output_path)
    return output_path

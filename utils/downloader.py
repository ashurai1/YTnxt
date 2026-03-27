import asyncio
import os
import uuid
import yt_dlp

def get_video_info_sync(url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['mweb', 'web_embedded']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

async def get_video_info(url: str):
    return await asyncio.to_thread(get_video_info_sync, url)

def get_available_resolutions(info):
    formats = info.get('formats', [])
    resolutions = set()
    for f in formats:
        if f.get('vcodec') != 'none' and f.get('height') and f.get('ext') == 'mp4':
            height = f.get('height')
            if height in [144, 240, 360, 480, 720, 1080]:
                resolutions.add(height)
    
    sorted_res = sorted(list(resolutions), reverse=True)
    final_res = [h for h in sorted_res if h <= 1080][:5]
    return [f"{h}p" for h in final_res]

def download_video_sync(url: str, height: int, output_path: str):
    ydl_opts = {
        'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['mweb', 'web_embedded']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def download_video(url: str, height: int, temp_dir: str = 'temp') -> str:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(temp_dir, filename)
    
    await asyncio.to_thread(download_video_sync, url, height, output_path)
    return output_path

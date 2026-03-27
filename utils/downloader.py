import asyncio
import os
import uuid
import yt_dlp

def get_video_info_sync(url: str):
    # Try multiple possible cookie locations on Render specifically
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_paths = [
        os.path.join(project_root, 'cookies.txt'),          # Root of project
        os.path.abspath('cookies.txt'),                     # Current dir
        '/opt/render/project/src/cookies.txt',              # Render default path
        os.path.join(os.getcwd(), 'cookies.txt')            # Explicit CWD
    ]
    
    cookies_path = None
    for path in possible_paths:
        print(f"DEBUG: Checking for cookies at {path}")
        if os.path.exists(path):
            cookies_path = path
            print(f"DEBUG: ✅ FOUND COOKIES at {cookies_path}")
            break
            
    if not cookies_path:
        print("DEBUG: ❌ COOKIES NOT FOUND in any common location!")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo+bestaudio/best',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb', 'web_embedded'],
                'skip': ['dash', 'hls']
            }
        }
    }
    
    if cookies_path:
        ydl_opts['cookiefile'] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"DEBUG: Error extracting info: {str(e)}")
            raise e

async def get_video_info(url: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_video_info_sync, url)

def get_available_resolutions(info):
    formats = info.get('formats', [])
    resolutions = set()
    for f in formats:
        height = f.get('height')
        if height and height in [144, 240, 360, 480, 720, 1080]:
            if f.get('vcodec') != 'none':
                resolutions.add(height)
    
    if not resolutions:
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                resolutions.add(f.get('height'))
    
    sorted_res = sorted(list(resolutions), reverse=True)
    final_res = [h for h in sorted_res if h in [144, 240, 360, 480, 720, 1080]][:5]
    
    if not final_res and info.get('formats'):
        return ["360p"]
        
    return [f"{h}p" for h in final_res]

def download_video_sync(url: str, height: int, output_path: str):
    # Search for cookies again for download process
    cookies_path = None
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for path in [os.path.join(project_root, 'cookies.txt'), os.path.abspath('cookies.txt'), '/opt/render/project/src/cookies.txt']:
        if os.path.exists(path):
            cookies_path = path
            break

    ydl_opts = {
        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        'outtmpl': f'{output_path}.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb', 'web_embedded']
            }
        }
    }
    
    if cookies_path:
        ydl_opts['cookiefile'] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Check for possible extensions
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

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
    """Base yt-dlp options with cookies and strong bot-bypass headers"""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'web_creator'],
                'skip': ['hls', 'dash'],
            }
        },
        'http_headers': {
            'User-Agent': (
                'com.google.ios.youtube/19.29.1 '
                '(iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'socket_timeout': 30,
        'retries': 5,
        'fragment_retries': 5,
    }

    cookies_path = find_cookies()
    if cookies_path:
        opts['cookiefile'] = cookies_path

    return opts


def get_video_info_sync(url: str):
    strategies = [
        # Strategy 1: iOS + web_creator client (best bypass)
        {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'web_creator'],
                }
            },
            'http_headers': {
                'User-Agent': (
                    'com.google.ios.youtube/19.29.1 '
                    '(iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)'
                ),
            },
            'socket_timeout': 30,
            'retries': 3,
        },
        # Strategy 2: android client
        {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                }
            },
            'socket_timeout': 30,
            'retries': 3,
        },
        # Strategy 3: web client with cookies only
        base_opts(),
    ]

    cookies_path = find_cookies()

    for i, opts in enumerate(strategies):
        if cookies_path and 'cookiefile' not in opts:
            opts['cookiefile'] = cookies_path
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                print(f"DEBUG: ✅ Got info via strategy {i+1}: {info.get('title')}")
                return info
        except Exception as e:
            print(f"DEBUG: Strategy {i+1} failed: {str(e)[:200]}")
            continue

    raise Exception("All strategies failed — YouTube is blocking this request.")


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
    strategies = [
        # Strategy 1: iOS client
        {
            'extractor_args': {
                'youtube': {'player_client': ['ios', 'web_creator']}
            },
            'http_headers': {
                'User-Agent': (
                    'com.google.ios.youtube/19.29.1 '
                    '(iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)'
                ),
            },
        },
        # Strategy 2: android client
        {
            'extractor_args': {
                'youtube': {'player_client': ['android']}
            },
        },
        # Strategy 3: default
        {},
    ]

    cookies_path = find_cookies()
    common = {
        'quiet': True,
        'no_warnings': True,
        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        'outtmpl': f'{output_path}.%(ext)s',
        'merge_output_format': 'mp4',
        'socket_timeout': 30,
        'retries': 5,
        'fragment_retries': 5,
    }
    if cookies_path:
        common['cookiefile'] = cookies_path

    for i, extra in enumerate(strategies):
        opts = {**common, **extra}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            print(f"DEBUG: ✅ Downloaded via strategy {i+1}")
            break
        except Exception as e:
            print(f"DEBUG: Download strategy {i+1} failed: {str(e)[:200]}")
            continue

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YouTube stream resolver – based on WorldCam's working implementation
"""
import subprocess
import re
from os.path import exists
from urllib.parse import unquote
# from .helpers import find_executable

"""
#############################################################
#  RSILive - RSI Play TV for Enigma2                        #
#  Created by: Lululla (https://github.com/OwnerPlugins)    #
#  Version: 1.0                                             #
#  License: GPLv3                                           #
#  Last Modified: 2026-06-26                                #
#############################################################

HELPERS MODULE - RSILive plugin

MAIN FEATURES:
• Screen resolution detection (HD/FHD/UHD)
• Dynamic skin loading based on resolution
• Executable path finder (yt-dlp, etc.)
• Cache directory management
• Plugin path constants
• File and directory utilities

FUNCTIONS:
• get_screen_resolution() - Returns (width, height) of Enigma2 desktop
• get_resolution_type() - Returns 'hd', 'fhd', or 'uhd' based on screen width
• load_skin(screen_name) - Loads skin XML for current resolution (fallback to HD)
• find_executable(name) - Searches PATH for executable
• get_cache_path(filename) - Returns path for cache files in /tmp
• ensure_dir(path) - Creates directory if it doesn't exist

USAGE:
    from .helpers import PLUGIN_PATH, load_skin, find_executable
    
    skin = load_skin("main")
    ytdlp = find_executable("yt-dlp")
    cache = get_cache_path("videos.json")

VERSION HISTORY:
v1.0 - Initial release with resolution detection and skin loading
#############################################################
"""


def extract_video_id(url):
    """
    Extract video ID from YouTube URL – robust version
    """
    try:
        decoded_url = unquote(url)
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
            r'(?:https?://)?youtu\.be/([^?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/live/([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/channel/([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/@([^/?]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, decoded_url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        print("[RSILive] extract_video_id error: {}".format(e))
        return None


def find_ytdlp():
    """
    Find yt-dlp executable – same as WorldCam
    """
    ytdlp_paths = [
        "/usr/bin/yt-dlp",
        "/usr/local/bin/yt-dlp",
        "/usr/bin/yt-dlp_linux",
    ]
    for path in ytdlp_paths:
        if exists(path):
            try:
                cmd = [path, "--version"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("[RSILive] Found yt-dlp at: {}".format(path))
                    return path
            except Exception:
                continue
    print("[RSILive] yt-dlp not found")
    return None


def get_stream_with_ytdlp(ytdlp_path, video_id):
    """
    Get stream URL using yt-dlp with various format options – WorldCam logic
    """
    youtube_url = "https://www.youtube.com/watch?v=" + video_id

    # Format options in order of preference
    # MP4 formats are most compatible with Enigma2
    format_options = [
        ["-g", "-f", "18"],                             # MP4 360p (most compatible)
        ["-g", "-f", "best[ext=mp4]"],                  # Best MP4
        ["-g", "-f", "22/37"],                          # MP4 720p/1080p
        ["-g", "-f", "best[protocol!=m3u8_native]"],    # Avoid HLS
        ["-g", "-f", "best"],                           # Any format
    ]

    for fmt in format_options:
        cmd = [ytdlp_path] + fmt + [youtube_url]
        print("[RSILive] Trying: {}".format(" ".join(cmd)))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url and stream_url.startswith(("http://", "https://")):
                    print("[RSILive] Stream found: {}".format(stream_url[:80]))
                    return stream_url
            else:
                error_msg = result.stderr[:100] if result.stderr else "Unknown error"
                print("[RSILive] Format failed: {}".format(error_msg))

        except subprocess.TimeoutExpired:
            print("[RSILive] Timeout for format: {}".format(" ".join(fmt)))
            continue
        except Exception as e:
            print("[RSILive] Error for format: {}".format(e))
            continue

    return None


def get_youtube_stream(url):
    """
    Main YouTube resolver – uses WorldCam logic
    """
    print("[RSILive] get_youtube_stream START")
    print("[RSILive] Input URL: {}".format(url[:100]))

    video_id = extract_video_id(url)
    if not video_id:
        print("[RSILive] No video ID extracted")
        return None
    print("[RSILive] Video ID: {}".format(video_id))

    ytdlp = find_ytdlp()
    if not ytdlp:
        print("[RSILive] yt-dlp not found")
        return None

    stream_url = get_stream_with_ytdlp(ytdlp, video_id)
    if stream_url:
        print("[RSILive] Successfully extracted stream URL")
        return stream_url
    else:
        print("[RSILive] Failed to extract stream URL")
        return None

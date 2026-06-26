#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RSI Live API client - uses SRG SSR Integration Layer
"""

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


class RSIApi:
    def __init__(self):
        print("[RSILive DEBUG] RSIApi __init__")

    def get_livestreams(self):
        print("[RSILive DEBUG] get_livestreams START")
        streams = {
            "RSI La 1": "https://rsilive1.akamaized.net/hls/live/2024605/rsila1/index.m3u8",
            "RSI La 2": "https://rsilive2.akamaized.net/hls/live/2024606/rsila2/index.m3u8",
        }
        print("[RSILive DEBUG] Returning {} streams".format(len(streams)))
        return streams

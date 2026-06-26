import os
import traceback

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


PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/RSILive"


def get_screen_resolution():
    print("[RSILive DEBUG] get_screen_resolution START")
    from enigma import getDesktop
    try:
        s = getDesktop(0).size()
        width, height = s.width(), s.height()
        print("[RSILive DEBUG] Resolution: {}x{}".format(width, height))
        return (width, height)
    except Exception as e:
        print("[RSILive DEBUG] get_screen_resolution ERROR: {}".format(e))
        return (1920, 1080)


def get_resolution_type():
    print("[RSILive DEBUG] get_resolution_type START")
    try:
        width = get_screen_resolution()[0]
        if width >= 3840:
            res = "uhd"
        elif width >= 2560:
            res = "wqhd"
        elif width >= 1920:
            res = "fhd"
        elif width >= 1280:
            res = "hd"
        else:
            res = "sd"
        print("[RSILive DEBUG] Resolution type: {}".format(res))
        return res
    except Exception as e:
        print("[RSILive DEBUG] get_resolution_type ERROR: {}".format(e))
        return "hd"


def load_skin(screen_name):
    print("[RSILive DEBUG] load_skin START: {}".format(screen_name))
    try:
        res = get_resolution_type()
        skin_path = f"{PLUGIN_PATH}/skins/{res}/{screen_name}.xml"
        print("[RSILive DEBUG] Looking for skin: {}".format(skin_path))

        if not os.path.exists(skin_path):
            skin_path = f"{PLUGIN_PATH}/skins/hd/{screen_name}.xml"
            print("[RSILive DEBUG] Fallback to: {}".format(skin_path))

        if os.path.exists(skin_path):
            with open(skin_path, "r") as f:
                content = f.read()
                print(
                    "[RSILive DEBUG] Skin loaded, size: {} bytes".format(
                        len(content)))
                return content
        else:
            print("[RSILive DEBUG] Skin file NOT FOUND")
            return None
    except Exception as e:
        print("[RSILive DEBUG] load_skin ERROR: {}".format(e))
        print("[RSILive DEBUG] Traceback: {}".format(traceback.format_exc()))
        return None


def find_executable(name):
    for path in os.environ.get("PATH", "").split(":"):
        full = os.path.join(path, name)
        if os.path.exists(full) and os.access(full, os.X_OK):
            print("[RSILive DEBUG] Found executable: {}".format(full))
            return full
    print("[RSILive DEBUG] Executable not found: {}".format(name))
    return None
